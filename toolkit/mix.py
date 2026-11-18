import subprocess, sys, json
SFX = '/home/claude/work/wall/sfx/'

def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())

def mix(d, end, sfx, music='/home/claude/work/chillwave.mp3', music_db=-21, music_start=0):
    """sfx: list of (name, start, db, fade_out, max_dur)"""
    inputs = ['-i', f'{d}/vo.mp3', '-ss', str(music_start), '-i', music]; flt = []; labels = []
    for i, (f, st, db, fo, md) in enumerate(sfx):
        inputs += ['-i', SFX + f + '.mp3']; parts = []
        if md: parts.append(f'atrim=0:{md}')
        if fo:
            dd = md or dur(SFX + f + '.mp3'); parts.append(f'afade=t=out:st={max(0, dd - fo)}:d={fo}')
        parts += [f'volume={db}dB', f'adelay={int(st * 1000)}|{int(st * 1000)}']
        flt.append(f'[{i + 2}:a]' + ','.join(parts) + f'[s{i}]'); labels.append(f'[s{i}]')
    flt.append('[0:a]adelay=150|150[vo]')
    flt.append(f'[1:a]atrim=0:{end},afade=t=in:d=0.4,afade=t=out:st={end - 2.0}:d=2.0,volume={music_db}dB[mu]')
    flt.append('[vo]' + ''.join(labels) + f'[mu]amix=inputs={len(labels) + 2}:normalize=0:duration=longest,atrim=0:{end},loudnorm=I=-14:TP=-1.5:LRA=11[out]')
    subprocess.run(['ffmpeg', '-y', '-v', 'error'] + inputs + ['-filter_complex', ';'.join(flt), '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s16le', f'{d}/mix.wav'], check=True)

def assemble(d, name, vend, endcard_dur=2.5):
    total = vend + endcard_dur
    fc = ('[0:v]minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos,'
          f'trim=0:{vend},setpts=PTS-STARTPTS[bg];[1:v]format=rgba[ov];[bg][ov]overlay=0:0:shortest=0:eof_action=pass[b2];[b2][4:v]overlay=34:134,format=yuv420p,fps=30[main];'
          f'[2:v]scale=1080:1920,format=yuv420p,fps=30,fade=t=in:d=0.3[end];[main][end]concat=n=2:v=1:a=0[v]')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '12', '-pattern_type', 'glob', '-i', f'{d}/frames/f_*.png',
                    '-framerate', '24', '-i', f'{d}/ovl/o_%05d.png',
                    '-loop', '1', '-t', str(endcard_dur), '-i', '/home/claude/work/endcard.png',
                    '-i', f'{d}/mix.wav', '-i', '/home/claude/work/watermark.png',
                    '-filter_complex', fc, '-map', '[v]', '-map', '3:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16',
                    '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart',
                    '-t', str(total), f'{d}/{name}.mp4'], check=True)
