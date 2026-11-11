import sys, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
import engine
B = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
C = B + 'canela/'
fH = font('Inter-ExtraBold.otf', 130); fB = font('Inter-ExtraBold.otf', 90); fM = font('Inter-ExtraBold.otf', 66)
fP = font('Inter-ExtraBold.otf', 50); fS = font('Inter-Bold.otf', 44); fT = font('Inter-Medium.otf', 30)
RED = (200, 25, 25, 240); BROWN = (110, 55, 25, 235); CREAM = (255, 240, 215, 245); DARK = (25, 15, 10, 220)
LEG = 'Este producto no es un medicamento.\nEl consumo de este producto es responsabilidad\nde quien lo recomienda y de quien lo usa.'

R = {
 'olla': dict(hook='hook_olla.mp4', pack=B + 'carrusel/prod/black.png', music=('musicaA.mp3', 0),
   hook_txt=[('CAFÉ DE OLLA', fH, (255, 255, 255), None, 0.1, 300), ('CON UN TOQUE DIFERENTE', fP, (255, 255, 255), RED, 1.2, 470)],
   ingred=('o_ingred', ['Agua (1 taza por persona)', '1 raja de canela', 'Piloncillo al gusto', '1 sobre de Lingzhi Black Coffee']),
   steps=[('o_hierve', '1 · Hierve agua, canela\ny piloncillo 3 minutos'), ('o_agrega', '2 · Apaga el fuego\ny agrega el café'), ('o_final', '3 · Sirve en jarrito de barro')],
   final=('o_final', 'Sabor de casa ☕'), cta=('¿Y EN TU CASA\nCÓMO LO PREPARAN?', 'Cuéntame en los comentarios'), name='Lingzhi Black Coffee 2 en 1'),
 'miel': dict(hook='hook_miel.mp4', pack=B + 'carrusel/prod/black.png', music=('musicaB.mp3', 0),
   hook_txt=[('SI MEZCLAS CAFÉ', fB, (255, 255, 255), None, 0.1, 280), ('CON CANELA Y MIEL...', fB, (255, 214, 120), None, 1.0, 400), ('PASA ESTO 👀'.replace(' 👀', ''), fP, (255, 255, 255), RED, 2.4, 560)],
   ingred=('m_ingred', ['1 sobre de Lingzhi Black Coffee', '1 taza de agua caliente', '½ cucharadita de canela', '1 cucharadita de miel']),
   steps=[('m_extra', '1 · Disuelve el café\ny agrega la canela'), ('m_mezcla', '2 · Agrega la miel\ny mezcla bien'), ('m_final', '3 · El aroma cambia\npor completo')],
   final=('m_final', 'Dulce y especiado'), cta=('GUÁRDALO PARA\nMAÑANA TEMPRANO', 'y me cuentas qué tal'), name='Lingzhi Black Coffee 2 en 1'),
 'latte': dict(hook='hook_latte.mp4', pack=C + 'l3en1.png', music=('musicaA.mp3', 40),
   hook_txt=[('LATTE DE CANELA', fB, (255, 255, 255), None, 0.1, 300), ('EN 1 MINUTO', fH, (255, 214, 120), None, 1.0, 420)],
   ingred=('l_ingred', ['1 sobre de Lingzhi Coffee 3 en 1', 'Un chorrito de agua caliente', 'Mucho hielo', 'Leche fría', 'Canela al gusto']),
   steps=[('l_hielo', '1 · Disuelve el café\ny agrega hielo'), ('l_leche', '2 · Agrega leche fría'), ('l_final', '3 · Canela por encima')],
   final=('l_final', 'Cremoso y frío'), cta=('COMPÁRTELO CON QUIEN\nAMA EL CAFÉ HELADO', 'Guárdalo para el próximo calor'), name='Lingzhi Coffee 3 en 1'),
}
key = sys.argv[1]; cfg = R[key]; T = 31.0
raw = subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', C + cfg['hook'], '-vf', f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}',
                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
fs = W * H * 3; hook = [Image.frombytes('RGB', (W, H), raw[i:i + fs]) for i in range(0, len(raw) - fs + 1, fs)]
st = {k: engine.load_still(C + k + '.png') for k in [cfg['ingred'][0]] + [s[0] for s in cfg['steps']] + [cfg['final'][0]]}
pack = Image.open(cfg['pack']); pack.thumbnail((600, 820), Image.LANCZOS)
emb = Embers(35, seed=3)
# timeline
SEG = [(0, 4.6, 'hook')]; t0 = 4.6
SEG.append((t0, t0 + 5.4, 'ingred')); t0 += 5.4
for i in range(3): SEG.append((t0, t0 + 4.2, f'step{i}')); t0 += 4.2
SEG.append((t0, t0 + 3.8, 'final')); t0 += 3.8
SEG.append((t0, T, 'end'))
def seg_of(t):
    for a, b, n in SEG:
        if a <= t < b: return a, b, n
    return SEG[-1]
def base(t):
    a, b, n = seg_of(t); p = ease_in_out_sine((t - a) / (b - a))
    if n == 'hook': return hook[min(len(hook) - 1, int(t * FPS))].convert('RGBA')
    if n == 'ingred': fr = engine.kb(st[cfg['ingred'][0]], p, 1.0, 1.1).convert('RGBA')
    elif n.startswith('step'): fr = engine.kb(st[cfg['steps'][int(n[-1])][0]], p, 1.12 if int(n[-1]) % 2 else 1.0, 1.0 if int(n[-1]) % 2 else 1.12).convert('RGBA')
    elif n == 'final': fr = engine.kb(st[cfg['final'][0]], p, 1.15, 1.0).convert('RGBA')
    else:
        fr = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(fr)
        for y in range(H): d.line((0, y, W, y), fill=(int(70 + 40 * y / H), int(38 + 20 * y / H), int(18 + 8 * y / H), 255))
        k = entrance(t, a, 0.6); dy, sc, ang = idle(t, 0.5, amp=7)
        place(fr, pack, W / 2, 1000 + 220 * (1 - k) + dy, (0.7 + 0.3 * k) * sc, ang, clamp(k * 1.4))
    emb.draw(fr, t, color=(255, 200, 130), alpha=0.5); return fr
# text schedule
texts = [(s, 4.6, TL, c, pl, y) for (TL, f, c, pl, s, y) in []]
L = []
for txt, f, col, pl, s, y in cfg['hook_txt']: L.append((s, 4.6, text_layer(txt, f, fill=col, pill=pl), y))
a = SEG[1][0]; L.append((a + 0.1, SEG[1][1], text_layer('NECESITAS', fM, pill=RED), 260))
for i, it in enumerate(cfg['ingred'][1]): L.append((a + 0.5 + i * 0.35, SEG[1][1], text_layer(it, fS, pill=DARK), 420 + i * 120))
for i in range(3):
    a, b, _ = SEG[2 + i]; L.append((a + 0.15, b, text_layer(cfg['steps'][i][1], fM, pill=BROWN), 330))
a, b, _ = SEG[5]; L.append((a + 0.1, b, text_layer('¡LISTO!', fH, fill=(255, 220, 120)), 300)); L.append((a + 0.6, b, text_layer(cfg['final'][1].replace(' ☕', ''), fP, pill=DARK), 480))
a = SEG[6][0]; L.append((a + 0.1, T, text_layer(cfg['cta'][0], fM), 240)); L.append((a + 0.6, T, text_layer(cfg['cta'][1], fS, pill=RED), 1460))
L.append((a + 0.4, T, text_layer(cfg['name'], fS, fill=(255, 225, 170)), 1560 - 1560 + 1540))
L.append((a + 0.9, T, text_layer(LEG, fT, pill=(0, 0, 0, 160), pad=(26, 12)), 1720))
def frame_at(t):
    if 4.4 <= t < 5.2: return saber_slash(base(4.38), base(t if t >= 4.72 else 5.2), (t - 4.4) / 0.8, color=(255, 175, 80))
    fr = base(t)
    for a, _, _ in SEG[2:]:
        if a <= t < a + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 245, 225, 255)), 0.4 * (1 - (t - a) / 0.1))
    return fr
def compose(t):
    fr = frame_at(t)
    for i, (s, e, ly, y) in enumerate(L): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    return fr
if sys.argv[2] == 'preview':
    ts = [float(x) for x in sys.argv[3].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[4]); sys.exit()
out = sys.argv[2]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', C + key + '_mudo.mp4'], stdin=subprocess.PIPE)
for n in range(int(T * FPS)): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait()
m, off = cfg['music']
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', C + key + '_mudo.mp4', '-ss', str(off), '-t', str(T), '-i', C + m, '-filter_complex',
                f'[1]afade=t=in:d=0.3,afade=t=out:st={T-1.8}:d=1.8,loudnorm=I=-14:TP=-1.5:LRA=11[a]', '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-t', str(T), '-movflags', '+faststart', out], check=True)
print('ok', key)
