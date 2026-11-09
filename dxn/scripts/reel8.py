import sys, json, math, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
import engine
B = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
N = B + 'negro/'
T = 74.0

# ---------- assets ----------
bg_big = cover(Image.open(N + 'bg.png').convert('RGB'), int(W * 1.18), int(H * 1.18))
cup = Image.open(N + 'cup_cut.png'); cup.thumbnail((760, 760), Image.LANCZOS)
beans = Image.open(N + 'beans_cut.png'); beans.thumbnail((1000, 1600), Image.LANCZOS)
pack = Image.open(B + 'carrusel/prod/black.png'); pack.thumbnail((420, 640), Image.LANCZOS)
pack_big = Image.open(B + 'carrusel/prod/black.png'); pack_big.thumbnail((560, 860), Image.LANCZOS)
still = {k: engine.load_still(v) for k, v in {
    'mature': B + 'reel/s4.png', 'wild': B + 'dia2/f_ruyi.png', 'kedah': B + 'reel2/s2.png',
    'green': B + 'reel2/s3.png', 's1': B + 'reel/s1.png', 's2': B + 'reel/s2.png', 's3': B + 'reel/s3.png',
    's4': B + 'reel/s4.png', 'clasico': B + 'carrusel/c2.png', 'helado': N + 'helado.png', 'canela': N + 'canela.png'}.items()}
embers = Embers(45)

# saber clip frames (5 s @30fps)
raw = subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', N + 'saber.mp4', '-vf',
                      f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}',
                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
fs = W * H * 3; saber = [Image.frombytes('RGB', (W, H), raw[i:i + fs]) for i in range(0, len(raw) - fs + 1, fs)]

# ---------- text layers ----------
fH = font('Inter-ExtraBold.otf', 150); fB = font('Inter-ExtraBold.otf', 92); fM = font('Inter-ExtraBold.otf', 68)
fP = font('Inter-ExtraBold.otf', 56); fS = font('Inter-Bold.otf', 46); fT = font('Inter-Medium.otf', 32)
RED = (200, 25, 25, 240); GOLD = (214, 150, 40, 240); DARK = (20, 20, 20, 225)
def TL(txt, f, **k): return text_layer(txt, f, **k)
# (start, end, layer, cx, cy)
texts = [
 (0.10, 2.30, TL('¿UN CAFÉ NEGRO', fB), W/2, 330),
 (2.30, 5.10, TL('CON UN HONGO DE', fM), W/2, 300),
 (4.15, 5.10, TL('+2,000 AÑOS?', fH, fill=(255, 205, 90)), W/2, 470),
 (6.30, 10.4, TL('QUÉDATE HASTA EL FINAL', fP, pill=RED), W/2, 300),
 (7.50, 10.4, TL('3 FORMAS DE\nPREPARARLO', fB), W/2, 470),
 (10.9, 20.8, TL('LINGZHI BLACK COFFEE', fM), W/2, 260),
 (11.3, 20.8, TL('2 EN 1', fP, pill=GOLD), W/2, 370),
 (14.0, 20.8, TL('SABOR INTENSO', fP, pill=DARK), 330, 560),
 (15.3, 20.8, TL('AROMA RICO', fP, pill=DARK), 330, 680),
 (16.7, 20.8, TL('SIN AZÚCAR AÑADIDA', fP, pill=RED), 400, 800),
 (18.4, 20.8, TL('CAFÉ + EXTRACTO\nDE GANODERMA', fS, pill=GOLD), W/2, 1180),
 (21.1, 27.4, TL('EL SECRETO', fH), W/2, 330),
 (25.3, 27.4, TL('"EL REY DE LAS HIERBAS"', fM, fill=(255, 205, 90)), W/2, 520),
 (27.6, 31.0, TL('DIFÍCIL DE ENCONTRAR\nEN LA NATURALEZA', fM), W/2, 330),
 (31.4, 36.1, TL('DESDE 1993', fH), W/2, 320),
 (34.1, 36.1, TL('DXN · MALASIA', fP, pill=RED), W/2, 500),
 (36.3, 39.6, TL('PROCESO ORGÁNICO', fP, pill=GOLD), W/2, 300),
 (37.6, 39.6, TL('CONTROL DE CALIDAD PROPIO', fP, pill=DARK), W/2, 420),
 (39.7, 42.6, TL('3 MESES PARA MADURAR', fP, pill=RED), W/2, 300),
 (42.9, 45.1, TL('3 FORMAS\nDE TOMARLO', fB), W/2, 380),
 (45.2, 50.0, TL('1 · CLÁSICO', fB), W/2, 300),
 (46.8, 50.0, TL('1 sobre + 1 taza de agua caliente', fS, pill=DARK), W/2, 450),
 (50.2, 56.7, TL('2 · AMERICANO HELADO', fM), W/2, 300),
 (52.3, 56.7, TL('agua caliente + hielo + agua fría', fS, pill=DARK), W/2, 430),
 (56.9, 63.3, TL('3 · CON CANELA', fB), W/2, 300),
 (58.7, 63.3, TL('una rajita mientras se prepara', fS, pill=DARK), W/2, 450),
 (63.5, 66.5, TL('PARA LOS QUE TOMAN\nSU CAFÉ NEGRO', fM), W/2, 280),
 (64.6, 66.5, TL('EN SERIO', fP, pill=RED), W/2, 470),
 (66.7, T, TL('¿Y TÚ, YA\nLO PROBASTE?', fB), W/2, 260),
 (68.4, T, TL('Cuéntame cómo te gusta tu café negro', fS, pill=RED), W/2, 1450),
 (68.8, T, TL('Este producto no es un medicamento.\nEl consumo de este producto es responsabilidad\nde quien lo recomienda y de quien lo usa.', fT, pill=(0, 0, 0, 170), pad=(30, 14)), W/2, 1700),
]
stage = {}  # stagger seeds
# timelapse labels
tl_labels = [(39.7 + i * 0.72, l) for i, l in enumerate(['1 SEMANA', '1 MES', '2 MESES', '3 MESES'])]

# ---------- captions ----------
words = [w for w in json.load(open(N + 'words.json'))['words'] if w.get('type') == 'word']
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1):
    if caps[i + 1][0] - caps[i][1] < 0.6: caps[i][1] = caps[i + 1][0]
    else: caps[i][1] += 0.25
KEY = {'CAFÉ', 'NEGRO', 'HONGO', 'AÑOS', 'HISTORIA', 'LINGZHI', 'BLACK', 'COFFEE', 'INTENSO', 'RICO', 'AZÚCAR', 'GANODERMA',
       'SECRETO', 'REY', 'HIERBAS', '1993', 'DXN', 'MALASIA', 'ORGÁNICO', 'CALIDAD', 'MESES', 'CLÁSICO', 'HELADO', 'CANELA', 'TRES', 'PROBASTE'}
fC = font('Inter-ExtraBold.otf', 64)
def draw_caption(fr, txt, t, s):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2; y = 1560 + 30 * (1 - k)
    for w, ww in zip(ws, wd):
        col = (255, 214, 10) if w.strip('¡!¿?.,:') in KEY else (255, 255, 255)
        d.text((x, y), w, font=fC, fill=col + (int(255 * clamp(k * 1.5)),), stroke_width=6, stroke_fill=(0, 0, 0))
        x += ww
    return fr

# ---------- scenes ----------
def cam(t): return (45 * math.sin(t * 0.33), 28 * math.sin(t * 0.26 + 1))
def cup_scene(t, with_pack_from=None):
    fr = parallax_frame(bg_big, cup, beans, cam(t), t, (W / 2 - 60, 1000), (W / 2 + 40, 1500), 1.15, 0.8)
    if with_pack_from is not None and t >= with_pack_from:
        k = entrance(t, with_pack_from, 0.6); dy, sc, ang = idle(t, 2.2, amp=6)
        cx = W + 300 - (W + 300 - 800) * k
        place(fr, pack, cx - cam(t)[0] * 0.8, 980 + dy, sc, ang)
    embers.draw(fr, t, alpha=0.6); return fr
def still_scene(key, t, t0, t1, z0=1.0, z1=1.12):
    p = ease_in_out_sine((t - t0) / max(0.01, t1 - t0))
    fr = engine.kb(still[key], p, z0, z1).convert('RGBA')
    embers.draw(fr, t, alpha=0.8); return fr
def end_scene(t):
    fr = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(fr)
    for y in range(H): d.line((0, y, W, y), fill=(int(30 + 25 * y / H), int(20 + 12 * y / H), int(12 + 6 * y / H), 255))
    embers.draw(fr, t, alpha=1.0)
    k = entrance(t, 66.6, 0.6); dy, sc, ang = idle(t, 0.7, amp=7)
    place(fr, pack_big, W / 2, 960 + 200 * (1 - k) + dy, (0.7 + 0.3 * k) * sc, ang, clamp(k * 1.4))
    return fr
def base(t):
    if t < 5.0: return saber[min(len(saber) - 1, int(t * FPS))].convert('RGBA')
    if t < 10.4: return cup_scene(t)
    if t < 20.8: return cup_scene(t, with_pack_from=10.8)
    if t < 27.5: return still_scene('mature', t, 20.8, 27.5)
    if t < 31.2: return still_scene('wild', t, 27.5, 31.2, 1.12, 1.0)
    if t < 36.2: return still_scene('kedah', t, 31.2, 36.2)
    if t < 39.6: return still_scene('green', t, 36.2, 39.6, 1.0, 1.15)
    if t < 42.6:
        i = min(3, int((t - 39.6) / 0.75)); return still_scene(['s1', 's2', 's3', 's4'][i], t, 39.6 + i * 0.75, 39.6 + (i + 1) * 0.75, 1.1, 1.0)
    if t < 50.0: return still_scene('clasico', t, 42.6, 50.0)
    if t < 56.7: return still_scene('helado', t, 50.0, 56.7, 1.12, 1.0)
    if t < 63.3: return still_scene('canela', t, 56.7, 63.3)
    if t < 66.5: return cup_scene(t, with_pack_from=63.4)
    return end_scene(t)
# saber-slash transitions: (start, dur)
SLASH = [(4.95, 0.85), (20.55, 0.75), (42.35, 0.75), (66.3, 0.6)]
CUTS = [27.5, 31.2, 36.2, 50.0, 56.7, 63.3]  # quick flash cuts
def frame_at(t):
    for s, d in SLASH:
        if s <= t < s + d:
            return saber_slash(base(s - 0.02), base(t + 0.0001 if t >= s + d * 0.4 else s + d), (t - s) / d,
                               color=(255, 165, 40))
    fr = base(t)
    for c in CUTS:
        if c <= t < c + 0.12: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 245, 225, 255)), 0.45 * (1 - (t - c) / 0.12))
    return fr

# ---------- render ----------
def compose(t):
    fr = frame_at(t)
    for i, (s, e, layer, cx, cy) in enumerate(texts):
        animate_in(fr, layer, t, s, cx, cy, end=e, seed=i * 0.9)
    for s, l in tl_labels:
        if s <= t < min(s + 0.72, 42.6): animate_in(fr, TL(l, fB), t, s, W / 2, 520, end=s + 0.72, seed=1)
    for s, e, txt in caps:
        if s <= t < e and t < 66.5: draw_caption(fr, txt, t, s)
    return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]
    ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]
    c.save(sys.argv[3]); sys.exit()
lo, hi = float(sys.argv[1]), float(sys.argv[2]); out = sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(hi * FPS))):
    t = n / FPS; fr = compose(t)
    p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
