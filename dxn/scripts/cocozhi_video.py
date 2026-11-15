import sys, json, os, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
import engine
B = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
C = B + 'cocozhi/'
T = 61.0
still = {k: engine.load_still(v) for k, v in {
    'bg': C + 'bg.png', 'maya': C + 'c_maya.png', 'sabor': C + 'c_sabor.png', 'prepara': C + 'c_prepara.png',
    'familia': C + 'c_familia.png', 'reishi': B + 'reel/s4.png', 'green': B + 'reel2/s3.png'}.items()}
pack = Image.open(B + 'carrusel/prod/cocozhi.png'); pack.thumbnail((620, 820), Image.LANCZOS)
pack_s = Image.open(B + 'carrusel/prod/cocozhi.png'); pack_s.thumbnail((330, 440), Image.LANCZOS)
emb = Embers(40, seed=11)
hook = []
if os.path.exists(C + 'hook.mp4'):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', C + 'hook.mp4', '-vf', f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    fs = W * H * 3; hook = [Image.frombytes('RGB', (W, H), raw[i:i + fs]) for i in range(0, len(raw) - fs + 1, fs)]
fH = font('Inter-ExtraBold.otf', 140); fB = font('Inter-ExtraBold.otf', 88); fM = font('Inter-ExtraBold.otf', 64)
fP = font('Inter-ExtraBold.otf', 52); fS = font('Inter-Bold.otf', 42); fT = font('Inter-Medium.otf', 30)
RED = (200, 25, 25, 240); CHOC = (95, 45, 20, 235); DARK = (25, 12, 6, 220); GOLD = (255, 205, 110)
def TL(t, f, **k): return text_layer(t, f, **k)
texts = [
 (0.10, 4.2, TL('¿CHOCOLATE', fH), 300), (1.30, 4.2, TL('CON UN HONGO DE', fM), 480), (2.40, 4.2, TL('+2,000 AÑOS?', fB, fill=GOLD), 580),
 (4.60, 9.3, TL('SE LLAMA', fM), 220), (4.90, 9.3, TL('COCOZHI', fH, fill=GOLD), 310), (6.90, 9.3, TL('Al final te digo para quién es', fS, pill=RED), 1500),
 (9.40, 13.7, TL('LO ESENCIAL', fB), 260), (10.9, 13.7, TL('COCOA DE CALIDAD', fP, pill=CHOC), 420), (12.2, 13.7, TL('+ EXTRACTO DE GANODERMA', fP, pill=RED), 540),
 (13.8, 19.6, TL('EL CACAO', fH), 260), (16.1, 19.6, TL('Mayas y aztecas ya lo bebían', fS, pill=DARK), 450),
 (19.7, 23.7, TL('EL GANODERMA', fB), 260), (21.6, 23.7, TL('"EL REY DE LAS HIERBAS"', fM, fill=GOLD), 400),
 (23.8, 30.0, TL('DXN · MALASIA', fP, pill=RED), 260), (25.6, 30.0, TL('DESDE 1993', fH), 360), (27.4, 30.0, TL('PROCESO ORGÁNICO', fP, pill=CHOC), 560), (28.8, 30.0, TL('CONTROL DE CALIDAD PROPIO', fP, pill=DARK), 670),
 (30.5, 35.0, TL('¿A QUÉ SABE?', fB), 260), (31.5, 35.0, TL('A CHOCOLATE', fM, fill=GOLD), 380), (32.4, 35.0, TL('CREMOSO', fP, pill=CHOC), 500), (33.3, 35.0, TL('SUAVE', fP, pill=CHOC), 610), (34.1, 35.0, TL('RECONFORTANTE', fP, pill=CHOC), 720),
 (35.1, 42.8, TL('¿CÓMO SE PREPARA?', fB), 240), (36.4, 42.8, TL('1 SOBRE', fP, pill=RED), 400), (37.2, 42.8, TL('+ 1 TAZA DE AGUA CALIENTE', fP, pill=DARK), 510), (38.7, 42.8, TL('MEZCLA Y LISTO', fP, pill=CHOC), 620),
 (40.3, 42.8, TL('Tal cual, sin agregar nada más', fS, pill=DARK), 1500),
 (42.9, 51.0, TL('¿PARA QUIÉN?', fB), 240), (44.0, 51.0, TL('PARA TODA LA FAMILIA', fP, pill=RED), 400), (44.6, 51.0, TL('(según DXN)', fS), 500),
 (47.3, 51.0, TL('Un momento para compartir en familia', fS, pill=DARK), 1450),
 (51.4, T, TL('¿Y TÚ, YA\nLO PROBASTE?', fB), 230), (52.7, T, TL('Cuéntame a qué te supo', fS, pill=RED), 1450),
 (53.4, T, TL('Este producto no es un medicamento.\nEl consumo de este producto es responsabilidad\nde quien lo recomienda y de quien lo usa.', fT, pill=(0, 0, 0, 160), pad=(26, 12)), 1660),
]
words = [w for w in json.load(open(C + 'words.json'))['words'] if w.get('type') == 'word' and not (47.1 <= w['start'] < 50.9)]
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1):
    caps[i][1] = caps[i + 1][0] if caps[i + 1][0] - caps[i][1] < 0.6 else caps[i][1] + 0.25
KEY = {'CHOCOLATE', 'HONGO', 'AÑOS', 'HISTORIA?', 'COCOZHI', 'COCOA', 'CALIDAD', 'GANODERMA', 'CACAO', 'MAYAS', 'AZTECAS', 'REY', 'HIERBAS', 'DXN', 'MALASIA', '1993',
       'ORGÁNICO', 'SABE?', 'CREMOSO', 'SUAVE', 'RECONFORTANTE', 'SOBRE', 'LISTO', 'FAMILIA', 'PEDIATRA', 'PROBASTE?'}
fC = font('Inter-ExtraBold.otf', 62)
def draw_caption(fr, txt, t, s, y=1700):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2
    for w, ww in zip(ws, wd):
        col = (255, 214, 10) if w.strip('¡!¿.,:') in KEY or w.strip('¡!¿.,:?') in KEY else (255, 255, 255)
        d.text((x, y + 30 * (1 - k)), w, font=fC, fill=col, stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
def st(key, t, a, b, z0=1.0, z1=1.12):
    fr = engine.kb(still[key], ease_in_out_sine((t - a) / (b - a)), z0, z1).convert('RGBA'); emb.draw(fr, t, color=(255, 190, 120), alpha=0.6); return fr
def packed(fr, t, start, x, y, big=False):
    k = entrance(t, start, 0.55); dy, sc, ang = idle(t, 1.7, amp=6); p = pack if big else pack_s
    place(fr, p, x, y + 200 * (1 - k) + dy, (0.75 + 0.25 * k) * sc, ang, clamp(k * 1.4)); return fr
def base(t):
    if t < 4.2:
        if hook: return hook[min(len(hook) - 1, int(t * FPS))].convert('RGBA')
        return st('sabor', t, 0, 4.2, 1.25, 1.0)
    if t < 9.3: return packed(st('bg', t, 4.2, 9.3, 1.15, 1.0), t, 4.7, W / 2, 1000, big=True)
    if t < 13.7: return packed(st('bg', t, 9.3, 13.7), t, 10.0, W - 250, 1150)
    if t < 19.6: return st('maya', t, 13.7, 19.6)
    if t < 23.7: return st('reishi', t, 19.6, 23.7, 1.12, 1.0)
    if t < 30.0: return st('green', t, 23.7, 30.0)
    if t < 35.0: return st('sabor', t, 30.0, 35.0, 1.12, 1.0)
    if t < 42.8:
        fr = st('prepara', t, 35.0, 42.8)
        return packed(fr, t, 36.5, W - 240, 1180) if t >= 36.5 else fr
    if t < 51.0: return st('familia', t, 42.8, 51.0, 1.12, 1.0)
    fr = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(fr)
    for y in range(H): d.line((0, y, W, y), fill=(int(70 + 40 * y / H), int(32 + 18 * y / H), int(14 + 8 * y / H), 255))
    emb.draw(fr, t, color=(255, 190, 120), alpha=0.9)
    return packed(fr, t, 51.2, W / 2, 900, big=True)
SLASH = [(4.0, 0.8, (255, 170, 90)), (29.8, 0.75, (255, 170, 90)), (50.8, 0.6, (255, 170, 90))]
CUTS = [9.3, 13.7, 19.6, 23.7, 35.0, 42.8]
def frame_at(t):
    for s, d, col in SLASH:
        if s <= t < s + d: return saber_slash(base(s - 0.02), base(t if t >= s + d * 0.4 else s + d), (t - s) / d, color=col)
    fr = base(t)
    for c in CUTS:
        if c <= t < c + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 240, 225, 255)), 0.4 * (1 - (t - c) / 0.1))
    return fr
def compose(t):
    fr = frame_at(t)
    for i, (s, e, ly, y) in enumerate(texts): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    for s, e, txt in caps:
        if s <= t < e and t < 51.2: draw_caption(fr, txt, t, s, 1600 if 40.3 <= t < 51 or 6.9 <= t < 9.3 else 1700)
    return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(hi * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
