"""Mezcla de voz + música sincronizada: la entrada emotiva de la pista (0:50) cae en la revelación,
y el final tranquilo de la canción acompaña el versículo y la pregunta final."""
import json, subprocess, sys
ROOT = sys.argv[1]; MUSIC = sys.argv[2]; OUT = sys.argv[3]
tm = json.load(open(f'{ROOT}/timing.json'))
total, reveal, tail, V0 = tm['total'], tm['reveal'] + tm['V0'], tm['tail'] + tm['V0'], tm['V0']
DROP = 50.0                      # entrada emotiva de "Rise with Purpose"
off = DROP - reveal              # inicio de la pista para que la entrada caiga en la revelación
xf = tail - 1.5                  # fundido cruzado hacia el final de la canción
tail_len = total - xf
tail_start = 175.0 - tail_len    # el final natural de la pista termina con el video
fc = (f"[1]atrim={off:.3f}:{off + xf + 2:.3f},asetpts=PTS-STARTPTS[a];"
      f"[1]atrim={tail_start - 2:.3f}:175.5,asetpts=PTS-STARTPTS[b];"
      f"[a][b]acrossfade=d=2:c1=tri:c2=tri,atrim=0:{total:.3f},afade=t=in:d=0.4,afade=t=out:st={total - 1.6:.3f}:d=1.6,"
      f"equalizer=f=2500:t=q:w=1.2:g=-4,volume=0.40[m];"
      f"[0]adelay={int(V0 * 1000)}|{int(V0 * 1000)},aformat=channel_layouts=stereo,apad,asplit=2[v1][v2];"
      f"[m][v1]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=280[md];"
      f"[md][v2]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/voz.mp3', '-i', MUSIC, '-filter_complex', fc,
                '-map', '[out]', '-ar', '48000', '-ac', '2', OUT], check=True)
print(f'pista desde {off:.2f}s; fundido al final en {xf:.2f}s (pista {tail_start:.2f}s)')
