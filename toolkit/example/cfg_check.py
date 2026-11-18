import sys; sys.path.insert(0,'/home/claude/work')
from ovl_lib import *
build(dict(dir='/home/claude/work/check', end=50.0, title_end=4.0,
 title=[("DON'T HIRE ANYONE", WHITE), ('FOR A PATIO UNTIL', WHITE), ('YOU CHECK THESE 3', GREEN)],
 keys=['base','writing.','nothing.','deep','underneath,','compacted.','paper.','water','slope','away','downspouts','foundation.','included.','digging,','hauling','sand,','cleanup.','extras.','three.','looking.','three'],
 badges=[('BUILT WRONG', RED, 0, 4.0), ('1  THE BASE', BLUE, 4.1, 20.1), ('2  THE WATER', BLUE, 20.2, 32.8),
         ("3  WHAT'S INCLUDED", BLUE, 32.9, 44.2), ('ALL 3 CHECKED', DGREEN, 44.3, 50.0)],
 tags=[('DIG DEPTH', GREEN, 12.6, 16.9), ('FABRIC', GREEN, 13.9, 16.9), ('COMPACTED IN LAYERS', GREEN, 15.8, 16.9),
       ('SLOPED AWAY FROM HOUSE', GREEN, 23.7, 28.6), ('DOWNSPOUT PIPED AWAY', GREEN, 25.9, 28.6),
       ('WATER AT YOUR FOUNDATION', RED, 30.4, 32.8)],
 callouts=[('depth','HOW DEEP?','L',-330,12.1,16.9), ('edge','EDGE RESTRAINT','R',-330,18.6,20.1),
           ('pipe','UNDERGROUND PIPE','R',170,26.0,28.6)]))
# ---------- paper cards ----------
fh = ImageFont.truetype(FD + 'Oswald-Bold.ttf', 50); fl = ImageFont.truetype(FD + 'Montserrat-Bold.ttf', 36); fb = ImageFont.truetype(FD + 'Montserrat-ExtraBold.ttf', 40)
def card(d, y0, h, al, title, lines, stamp=None, scol=RED):
    A = lambda c, k=1.0: c + (int(255 * al * k),)
    x0, x1 = 120, W - 120
    d.rounded_rectangle((x0, y0, x1, y0 + h), 18, fill=A((246, 244, 238)), outline=A((30, 30, 30)), width=3)
    d.text((x0 + 40, y0 + 26), title, font=fh, fill=A((25, 25, 25)))
    d.line((x0 + 40, y0 + 96, x1 - 40, y0 + 96), fill=A((60, 60, 60)), width=3)
    y = y0 + 120
    for txt, col in lines:
        d.text((x0 + 40, y), txt, font=fl, fill=A(col)); y += 56
    if stamp:
        w_ = d.textlength(stamp, font=fb); sx = x1 - w_ - 70; sy = y0 + 26
        d.rounded_rectangle((sx - 18, sy - 6, sx + w_ + 18, sy + 62), 10, outline=A(scol), width=6)
        d.text((sx, sy), stamp, font=fb, fill=A(scol))
def fd(t, a, b, r=0.25):
    if t < a or t > b: return 0
    return min(1, (t - a) / r, (b - t) / r)
DK = (25, 25, 25)
d0 = '/home/claude/work/check/ovl'
for f in range(int(50.0 * FPS)):
    t = f / FPS
    cards = []
    a = fd(t, 6.9, 11.95)
    if a: cards.append((330, 300, a, 'ESTIMATE', [('Patio ................................ $8,000', DK)] + ([('Base depth?  Fabric?  Compaction?', RED)] if t > 10.5 else []), 'VAGUE' if t > 10.5 else None, RED))
    a = fd(t, 17.3, 20.15)
    if a: cards.append((1080, 410, a, 'ESTIMATE', [('Excavation & haul away', DK), ('Fabric + compacted stone base', DK), ('Screeded bedding + pavers', DK), ('Edge restraint, sloped away', DK)], 'IN WRITING', DGREEN))
    a = fd(t, 34.0, 44.2)
    if a:
        ls = [(n, DK) for n, tt in [('Digging', 35.8), ('Hauling the dirt away', 36.4), ('Joint sand', 38.1), ('Cleanup', 38.9)] if t >= tt]
        if t > 40.0: ls.append(('Not listed? Expect extras later.', RED))
        cards.append((330, 120 + 56 * 5 + 30, a, "WHAT'S INCLUDED?", ls, 'ASK FIRST', DGREEN))
    if not cards: continue
    p = f'{d0}/o_{f:05d}.png'; im = Image.open(p).convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for y0, h, al, ti, ls, st, sc_ in cards: card(d, y0, h, al, ti, ls, st, sc_)
    im.alpha_composite(lay); im.save(p)
