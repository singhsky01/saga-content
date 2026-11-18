import json, os
from PIL import Image, ImageDraw, ImageFont

FPS = 24; W, H = 1080, 1920
FD = '/home/claude/work/fonts/'
f_cap = ImageFont.truetype(FD + 'Montserrat-ExtraBold.ttf', 66)
f_title = ImageFont.truetype(FD + 'Oswald-Bold.ttf', 82)
f_badge = ImageFont.truetype(FD + 'Oswald-Bold.ttf', 50)
f_tag = ImageFont.truetype(FD + 'Oswald-Bold.ttf', 40)
f_call = ImageFont.truetype(FD + 'Montserrat-ExtraBold.ttf', 30)
GREEN = (74, 222, 128); RED = (220, 38, 38); BLUE = (59, 130, 246); WHITE = (255, 255, 255); DGREEN = (22, 163, 74); AMBER = (234, 140, 20)

def tw(d, t, f): return d.textlength(t, font=f)
def fade(t, a, b, r=0.18):
    if t < a or t >= b: return 0
    return min(1, (t - a) / r, (b - t) / r)

def build(cfg):
    d0 = cfg['dir']; words = json.load(open(d0 + '/words.json')); anch = json.load(open(d0 + '/anchors.json'))
    END = cfg['end']; KEY = set(cfg['keys']); out = d0 + '/ovl'; os.makedirs(out, exist_ok=True)
    chunks = []; cur = []
    for w, s, e in words:
        cur.append((w, s, e))
        if w[-1] in '.,?' or w.endswith('...') or len(cur) >= 3: chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    caps = []
    for i, c in enumerate(chunks):
        st = c[0][1]; en = chunks[i + 1][0][1] if i + 1 < len(chunks) else END
        if en - c[-1][2] > 0.6: en = c[-1][2] + 0.45
        caps.append((st, en, c))
    maxf = max(int(k) for k in anch)
    for f in range(int(END * FPS)):
        t = f / FPS; af = str(min(maxf, f))
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
        # title
        al = fade(t, -1, cfg['title_end'], 0.25)
        if al > 0:
            for i, (txt, col) in enumerate(cfg['title']):
                x = (W - tw(d, txt, f_title)) / 2
                d.text((x, 230 + i * 104), txt, font=f_title, fill=col + (int(255 * al),), stroke_width=4, stroke_fill=(0, 0, 0, int(255 * al)))
        # badges
        for text, col, a, b in cfg['badges']:
            al = fade(t, a, b, 0.12)
            if al <= 0: continue
            w_ = tw(d, text, f_badge); x1 = W - 56; x0 = x1 - w_ - 36
            d.rounded_rectangle((x0, 120, x1, 196), 8, fill=col + (int(255 * al),))
            d.text((x0 + 18, 126), text, font=f_badge, fill=(255, 255, 255, int(255 * al)))
        # stacked tags
        y = 230
        for text, col, a, b in cfg['tags']:
            al = fade(t, a, b, 0.15)
            if al <= 0: continue
            w_ = tw(d, text, f_tag)
            d.rectangle((56, y, 56 + w_ + 28, y + 60), fill=(10, 10, 12, int(200 * al)), outline=col + (int(255 * al),), width=4)
            d.text((70, y + 4), text, font=f_tag, fill=col + (int(255 * al),)); y += 76
        # callouts
        for key, text, side, dy, a, b in cfg['callouts']:
            al = fade(t, a, b, 0.2)
            if al <= 0: continue
            ax, ay = anch[af][key]; px, py = ax * W, (1 - ay) * H
            w_ = tw(d, text, f_call); bh = 50; ly = py + dy
            if side == 'L': x0 = 40; x1 = x0 + w_ + 28; lx = x1
            else: x1 = W - 40; x0 = x1 - w_ - 28; lx = x0
            A = int(255 * al)
            d.line((px, py, lx, ly + bh / 2), fill=(255, 255, 255, A), width=4)
            d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=(255, 255, 255, A))
            d.rounded_rectangle((x0, ly, x1, ly + bh), 8, fill=(15, 15, 18, int(225 * al)), outline=(255, 255, 255, A), width=3)
            d.text((x0 + 14, ly + 8), text, font=f_call, fill=(255, 255, 255, A))
        img.alpha_composite(lay)
        dd = ImageDraw.Draw(img)
        for st, en, c in caps:
            if st <= t < en:
                toks = [w for w, _, _ in c]; disp = [w.replace('...', '…') for w in toks]
                sp = tw(dd, ' ', f_cap); total = sum(tw(dd, w, f_cap) for w in disp) + sp * (len(disp) - 1)
                x = (W - total) / 2
                for w, dw in zip(toks, disp):
                    dd.text((x, 1505), dw, font=f_cap, fill=GREEN if w.lower().strip('.,?') in KEY else WHITE, stroke_width=7, stroke_fill=(0, 0, 0))
                    x += tw(dd, dw, f_cap) + sp
                break
        img.save(f'{out}/o_{f:05d}.png', compress_level=1)
