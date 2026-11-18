import sys, json, subprocess, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
B = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/espirulina/'
words = [w for w in json.load(open(B + 'words.json'))['words'] if w.get('type') == 'word']
T = 70.0
def at(word, after=0.0):
    for w in words:
        if w['start'] >= after and w['text'].lower().strip('¿?¡!.,:') == word: return w['start']
    raise SystemExit('no ' + word)
t_hoy = at('hoy'); t1 = at('uno'); t2 = at('dos'); t3 = at('tres'); t4 = at('cuatro', t3); t5 = at('cinco'); t6 = at('seis', t5)
t_algo = at('algo', t6); t_dxn = at('dxn'); t_est = at('estanques'); t_sin = at('sin', t_est); t_cual = at('cuál')
SEG = [(0, t_hoy - 0.1, 'mexicas'), (t_hoy - 0.1, t1 - 0.15, 'intro'), (t1 - 0.15, t2 - 0.15, 'c1'), (t2 - 0.15, t3 - 0.15, 'c2'),
       (t3 - 0.15, t4 - 0.15, 'c3'), (t4 - 0.15, t5 - 0.15, 'jugo'), (t5 - 0.15, t6 - 0.15, 'c5'), (t6 - 0.15, t_algo - 0.1, 'c6'),
       (t_algo - 0.1, t_cual - 0.15, 'c7'), (t_cual - 0.15, T, 'end')]
PK = {k: Image.open(B + 'prod/' + k + '.png') for k in ['FB032', 'HF037', 'HF066']}
def sized(im, w): r = w / im.width; return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
SM = {'FB032': sized(PK['FB032'], 400), 'HF037': sized(PK['HF037'], 250), 'HF066': sized(PK['HF066'], 250)}
BG = {'FB032': sized(PK['FB032'], 560), 'HF037': sized(PK['HF037'], 340), 'HF066': sized(PK['HF066'], 340)}
PACK_OF = {'c1': 'FB032', 'c2': 'FB032', 'c3': 'HF037', 'jugo': 'HF066', 'c5': 'FB032', 'c6': 'FB032'}
emb = Embers(40, seed=7)
grad = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(grad)
for y in range(H): d.line((0, y, W, y), fill=(int(8 + 20 * y / H), int(48 + 40 * y / H), int(36 + 20 * y / H), 255))
fNum = font('Inter-ExtraBold.otf', 300); fH = font('Inter-ExtraBold.otf', 120); fB = font('Inter-ExtraBold.otf', 86); fM = font('Inter-ExtraBold.otf', 64)
fP = font('Inter-ExtraBold.otf', 54); fS = font('Inter-Bold.otf', 42); fT = font('Inter-Medium.otf', 30)
RED = (200, 25, 25, 240); GREEN = (20, 120, 70, 240); DARK = (10, 25, 18, 220); GOLD = (255, 214, 110)
def frame_of(name, t, a, b):
    n = 237; p = (t - a) / (b - a) if (b - a) > 7.9 else (t - a) / 7.9
    i = int(clamp(p) * (n - 1)) + 1
    return Image.open(f'{B}fr/{name}/{i:04d}.jpg').convert('RGBA')
def lineup(fr, t, start, y=1000):
    for j, (k, x) in enumerate([('HF037', 300), ('HF066', W - 300), ('FB032', W / 2)]):
        k_ = entrance(t, start + j * 0.25, 0.55); dy, sc, ang = idle(t, j * 1.3, amp=6)
        yy = y + (230 if k == 'FB032' else -120)
        place(fr, BG[k], x, yy + 220 * (1 - k_) + dy, (0.7 + 0.3 * k_) * sc, ang, clamp(k_ * 1.4))
def base(t):
    for a, b, n in SEG:
        if a <= t < b: break
    if n in ('intro', 'end'):
        fr = grad.copy(); emb.draw(fr, t, color=(170, 255, 200), alpha=0.7)
        lineup(fr, t, a + (1.0 if n == 'intro' else 0.3), 1000 if n == 'intro' else 960); return fr
    fr = frame_of(n, t, a, b)
    if n in PACK_OF:
        k = entrance(t, a + 0.6, 0.55); dy, sc, ang = idle(t, 1.1, amp=6)
        place(fr, SM[PACK_OF[n]], W - 240, 1290 + 160 * (1 - k) + dy, (0.75 + 0.25 * k) * sc, ang + 5, clamp(k * 1.4))
    return fr
L = []
def add(s, e, ly, y): L.append((s, e, ly, y))
a = 0; add(0.1, SEG[0][1], text_layer('HACE 500 AÑOS', fH), 250); add(1.7, SEG[0][1], text_layer('LOS MEXICAS YA LA COMÍAN', fP, pill=RED), 420)
add(at('tecuitlatl') - 0.1, SEG[0][1], text_layer('"TECUITLATL"', fB, fill=GOLD), 560)
add(0.6, SEG[0][1], text_layer('Recreación · dato histórico de crónicas del siglo XVI', fT, pill=(0, 0, 0, 150), pad=(22, 10)), 1560)
a, b, _ = SEG[1]; add(a + 0.2, b, text_layer('ESPIRULINA', fH, fill=GOLD), 250); add(at('seis') - 0.1, b, text_layer('6 FORMAS DE TOMARLA', fP, pill=RED), 420)
add(at('cuatro') - 0.1, b, text_layer('¿La #4? Casi nadie la conoce', fS, pill=DARK), 1450)
LAB = ['CON LECHE CALIENTE', 'EN LICUADO', 'EN CÁPSULAS', 'EN TU JUGO', 'SOBRE FRUTA', 'BIEN FRÍO']
for i in range(6):
    a, b, _ = SEG[2 + i]
    add(a + 0.1, b, text_layer(str(i + 1), fNum, fill=GOLD, stroke=10), 120); add(a + 0.4, b, text_layer(LAB[i], fP, pill=GREEN), 470)
add(at('treinta', at('en', t1 + 3)) - 0.1, SEG[2][1], text_layer('Listo en 30 segundos', fS, pill=DARK), 1500)
add(at('según') - 0.1, SEG[4][1], text_layer('Ingrediente: espirulina en polvo\n(según la etiqueta)', fS, pill=DARK), 1440)
add(at('casi', t4) - 0.1, SEG[5][1], text_layer('LA QUE CASI NADIE CONOCE', fS, pill=RED), 590)
a, b, _ = SEG[8]
add(t_dxn - 0.1, b, text_layer('DXN', fH, fill=GOLD), 230); add(t_dxn + 0.4, b, text_layer('CULTIVA SU PROPIA ESPIRULINA', fP, pill=RED), 400)
add(t_est - 0.1, b, text_layer('EN ESTANQUES', fP, pill=GREEN), 510); add(t_sin - 0.1, b, text_layer('SIN PESTICIDAS NI HERBICIDAS', fP, pill=GREEN), 620)
add(t_sin + 0.6, b, text_layer('Según DXN · imagen ilustrativa', fT, pill=(0, 0, 0, 150), pad=(22, 10)), 1560)
a, b, _ = SEG[9]
add(a + 0.2, T, text_layer('¿CUÁL DE LAS 6\nCONOCÍAS?', fB), 210); add(at('guarda') - 0.1, T, text_layer('Guárdalo para cuando la prepares', fS, pill=RED), 1430)
add(a + 1.2, T, text_layer('Este producto no es un medicamento.\nEl consumo de este producto es responsabilidad\nde quien lo recomienda y de quien lo usa.', fT, pill=(0, 0, 0, 160), pad=(26, 12)), 1650)
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1): caps[i][1] = caps[i + 1][0] if caps[i + 1][0] - caps[i][1] < 0.6 else caps[i][1] + 0.25
KEY = {'MEXICAS', 'TEXCOCO', 'TECUITLATL', 'ESPIRULINA', 'SEIS', 'CUATRO', 'UNO', 'DOS', 'TRES', 'CINCO', 'CEREAL', 'LICUADO', 'CÁPSULAS',
       'JUGO', 'NARANJA', 'FRUTA', 'FRÍO', 'DXN', 'ESTANQUES', 'PESTICIDAS', 'HERBICIDAS', 'CONOCÍAS', 'GUARDA', '500', 'COLORES', 'PLÁTANO'}
fC = font('Inter-ExtraBold.otf', 62)
def draw_caption(fr, txt, t, s):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2
    for w, ww in zip(ws, wd):
        col = (255, 214, 10) if w.strip('¿?¡!.,:"') in KEY else (255, 255, 255)
        d.text((x, 1730 + 30 * (1 - k)), w, font=fC, fill=col, stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
SL = SEG[1][0]
def frame_at(t):
    if SL - 0.4 <= t < SL + 0.4:
        return saber_slash(base(SL - 0.42), base(t if t >= SL else SL + 0.02), (t - SL + 0.4) / 0.8, color=(120, 255, 170))
    fr = base(t)
    for a, _, _ in SEG[2:]:
        if a <= t < a + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (235, 255, 240, 255)), 0.45 * (1 - (t - a) / 0.1))
    return fr
def compose(t):
    fr = frame_at(t)
    for i, (s, e, ly, y) in enumerate(L): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    for s, e, txt in caps:
        if s <= t < e and t < SEG[9][0]: draw_caption(fr, txt, t, s)
    return fr
if sys.argv[1] == 'info': print([(round(a, 2), round(b, 2), n) for a, b, n in SEG]); sys.exit()
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(min(hi, T) * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
