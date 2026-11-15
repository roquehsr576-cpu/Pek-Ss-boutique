import sys, json, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
import engine
B = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
P = B + 'pavo/'; D = B + 'dia2/'
T = 81.0
def clip(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', path, '-vf', f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    fs = W * H * 3; return [Image.frombytes('RGB', (W, H), raw[i:i + fs]) for i in range(0, len(raw) - fs + 1, fs)]
pavo = clip(P + 'hook_pavo.mp4'); cora = clip(D + 'hook_corazon.mp4')
st = {k: engine.load_still(v) for k, v in {'grid': D + 'grid.png', 'higado': D + 'f_higado.png', 'cerebro': D + 'f_cerebro.png', 'kimshen': D + 'f_kimshen.png',
      'ruyi': D + 'f_ruyi.png', 'pavo': D + 'f_pavo.png', 's1': B + 'reel/s1.png', 's2': B + 'reel/s2.png', 's3': B + 'reel/s3.png', 's4': B + 'reel/s4.png',
      'green': B + 'reel2/s3.png', 'kedah': B + 'reel2/s2.png'}.items()}
emb = Embers(45, seed=5)
fH = font('Inter-ExtraBold.otf', 130); fB = font('Inter-ExtraBold.otf', 86); fM = font('Inter-ExtraBold.otf', 64)
fP = font('Inter-ExtraBold.otf', 56); fS = font('Inter-Bold.otf', 44)
RED = (200, 25, 25, 240); DARK = (15, 25, 15, 220); GOLDP = (190, 130, 30, 240); GOLD = (255, 210, 110)
def TL(t, f, **k): return text_layer(t, f, **k)
texts = [
 (0.10, 4.9, TL('¿SABÍAS QUE', fM), 260), (0.9, 4.9, TL('ESTE HONGO CRECE COMO', fP), 360), (2.6, 4.9, TL('LA COLA DE UN\nPAVO REAL?', fB, fill=GOLD), 470),
 (5.8, 13.3, TL('ES GANODERMA', fB), 250), (8.4, 13.3, TL('6 FORMAS', fH, fill=GOLD), 380), (11.2, 13.3, TL('La última es mi favorita', fS, pill=RED), 560),
 (13.4, 20.2, TL('ALGO IMPORTANTE', fM, pill=RED), 300), (15.7, 20.2, TL('SE LLAMAN ASÍ\nPOR CÓMO SE VEN', fB), 450), (18.8, 20.2, TL('NO POR LO QUE HACEN', fP, pill=DARK), 700),
 (20.4, 25.6, TL('1 · HÍGADO', fB, pill=RED), 260), (22.0, 25.6, TL('Sombrero ancho y lobulado', fS, pill=DARK), 420),
 (25.8, 30.1, TL('2 · CORAZÓN', fB, pill=RED), 260), (27.6, 30.1, TL('Un corazón casi perfecto', fS, pill=DARK), 420),
 (30.3, 35.4, TL('3 · CEREBRO', fB, pill=RED), 260), (32.1, 35.4, TL('Capas plegadas una sobre otra', fS, pill=DARK), 420),
 (35.6, 40.4, TL('4 · KIMSHEN', fB, pill=RED), 260), (37.4, 40.4, TL('Ramas delgadas, como un árbol', fS, pill=DARK), 420),
 (40.6, 48.4, TL('5 · RUYI', fB, pill=RED), 260), (42.4, 48.4, TL('Como el ruyi chino:\nsímbolo de buena fortuna', fS, pill=DARK), 420),
 (48.7, 55.0, TL('6 · PAVO REAL', fB, pill=GOLDP), 260), (49.6, 55.0, TL('MI FAVORITA', fM, fill=GOLD), 420), (52.0, 55.0, TL('Sus capas se abren como abanico', fS, pill=DARK), 540),
 (55.2, 58.6, TL('¿CÓMO NACEN?', fB), 260), (56.6, 58.6, TL('HILOS BLANCOS', fP, pill=DARK), 420),
 (58.7, 60.7, TL('1 MES', fH, fill=GOLD), 300), (60.8, 63.5, TL('3 MESES', fH, fill=GOLD), 300), (62.3, 63.5, TL('HONGO MADURO', fP, pill=RED), 480),
 (63.7, 70.0, TL('DXN · MALASIA', fP, pill=RED), 260), (65.6, 70.0, TL('DESDE 1993', fH), 360), (68.3, 70.0, TL('PROCESO ORGÁNICO', fP, pill=GOLDP), 560),
 (70.2, 75.1, TL('CONTROL DE CALIDAD PROPIO', fP, pill=DARK), 260), (71.5, 75.1, TL('DIFÍCIL DE ENCONTRAR\nEN LA NATURALEZA', fM), 380),
 (75.3, T, TL('¿CUÁL ES TU\nFAVORITA?', fB, fill=GOLD), 330), (77.2, T, TL('Cuéntame por qué en los comentarios', fS, pill=RED), 560),
 (77.6, T, TL('Las formas y sus nombres, según DXN', font('Inter-Medium.otf', 32), pill=(0, 0, 0, 150), pad=(26, 12)), 1500),
]
words = [w for w in json.load(open(P + 'words.json'))['words'] if w.get('type') == 'word']
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1):
    caps[i][1] = caps[i + 1][0] if caps[i + 1][0] - caps[i][1] < 0.6 else caps[i][1] + 0.25
KEY = {'HONGO', 'PAVO', 'REAL?', 'REAL.', 'GANODERMA', 'SEIS', 'FAVORITA.', 'FAVORITA:', 'FAVORITA?', 'HÍGADO.', 'CORAZÓN.', 'CEREBRO.', 'KIMSHEN.', 'RUYI.', 'RUYI,',
       'FORTUNA.', 'BLANCOS.', 'CUERNOS', 'MESES', 'MADURO.', 'DXN', 'MALASIA', '1993', 'ORGÁNICO', 'CALIDAD,', 'NATURALEZA', 'VEN,', 'HACEN.'}
fC = font('Inter-ExtraBold.otf', 62)
def draw_caption(fr, txt, t, s):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2
    for w, ww in zip(ws, wd):
        col = (255, 214, 10) if w in KEY or w.strip('¿?.,:') in KEY else (255, 255, 255)
        d.text((x, 1700 + 30 * (1 - k)), w, font=fC, fill=col, stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
def S(key, t, a, b, z0=1.0, z1=1.12, dark=False):
    fr = engine.kb(st[key], ease_in_out_sine((t - a) / (b - a)), z0, z1)
    if dark: fr = ImageEnhance.Brightness(fr).enhance(0.45)
    fr = fr.convert('RGBA'); emb.draw(fr, t, color=(255, 210, 140), alpha=0.7); return fr
def V(frames, t, a):
    return frames[min(len(frames) - 1, int((t - a) * FPS))].convert('RGBA')
def base(t):
    if t < 5.0: return V(pavo, t, 0)
    if t < 13.3: return S('grid', t, 5.0, 13.3)
    if t < 20.2: return S('grid', t, 13.3, 20.2, 1.12, 1.0, dark=True)
    if t < 25.6: return S('higado', t, 20.2, 25.6)
    if t < 30.1: return V(cora, t, 25.6)
    if t < 35.4: return S('cerebro', t, 30.1, 35.4, 1.12, 1.0)
    if t < 40.4: return S('kimshen', t, 35.4, 40.4)
    if t < 48.4: return S('ruyi', t, 40.4, 48.4, 1.12, 1.0)
    if t < 53.4: return V(pavo, t, 48.4)
    if t < 55.0: return S('pavo', t, 53.4, 55.0, 1.15, 1.2)
    if t < 58.6: return S('s1', t, 55.0, 58.6)
    if t < 60.7: return S('s2', t, 58.6, 60.7)
    if t < 62.2: return S('s3', t, 60.7, 62.2)
    if t < 63.5: return S('s4', t, 62.2, 63.5)
    if t < 70.0: return S('green', t, 63.5, 70.0)
    if t < 75.1: return S('kedah', t, 70.0, 75.1, 1.12, 1.0)
    return S('grid', t, 75.1, T, 1.0, 1.1, dark=True)
SLASH = [(4.85, 0.8), (48.1, 0.75), (74.85, 0.6)]
CUTS = [13.3, 20.2, 25.6, 30.1, 35.4, 40.4, 55.0, 58.6, 60.7, 62.2, 63.5, 70.0]
def frame_at(t):
    for s, d in SLASH:
        if s <= t < s + d: return saber_slash(base(s - 0.02), base(t if t >= s + d * 0.4 else s + d), (t - s) / d, color=(255, 190, 90))
    fr = base(t)
    for c in CUTS:
        if c <= t < c + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 245, 225, 255)), 0.4 * (1 - (t - c) / 0.1))
    return fr
def compose(t):
    fr = frame_at(t)
    for i, (s, e, ly, y) in enumerate(texts): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    for s, e, txt in caps:
        if s <= t < e and t < 75.2: draw_caption(fr, txt, t, s)
    return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((180, 320)) for t in ts]
    c = Image.new('RGB', (180 * len(ims), 320)); [c.paste(im, (i * 180, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(hi * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
