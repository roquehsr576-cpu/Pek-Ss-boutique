import sys, json, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
B = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/noni/'
words = [w for w in json.load(open(B + 'words.json'))['words'] if w.get('type') == 'word']
T = 66.0
def at(word, after=0.0):
    for w in words:
        if w['start'] >= after and w['text'].lower().strip('¿?¡!.,:') == word: return w['start']
    raise SystemExit('no ' + word)
t_se = at('se'); t_su = at('su'); t_cuando = at('cuando'); t_suelta = at('suelta'); t_y = at('y', at('queso', 34)); t_pac = at('y', at('telas'))
t_ent = at('entonces'); t_dxn = at('dxn'); t_tu = at('¿tú') if False else at('tú')
SEG = [(0, t_se - 0.15, 'n1a'), (t_se - 0.15, t_su - 0.15, 'n2'), (t_su - 0.15, t_cuando - 0.15, 'n3'), (t_cuando - 0.15, t_suelta - 0.1, 'still'),
       (t_suelta - 0.1, t_y - 0.1, 'n1b'), (t_y - 0.1, t_pac - 0.1, 'n4'), (t_pac - 0.1, t_dxn - 0.2, 'n5'), (t_dxn - 0.2, t_tu - 0.15, 'prod'), (t_tu - 0.15, T, 'end')]
def frame(name, i): return Image.open(f'{B}fr/{name}/{max(1, min(237, i)):04d}.jpg').convert('RGBA')
def clipf(name, t, a, b, f0=1, f1=237):
    p = clamp((t - a) / (b - a)); return frame(name, int(f0 + p * (f1 - f0)))
bottle = Image.open(B + 'prod/FB007.png'); r = 520 / bottle.height; BIG = bottle.resize((int(bottle.width * r * 1.4), int(520 * 1.4)), Image.LANCZOS)
r = 700 / bottle.height; END = bottle.resize((int(bottle.width * r), 700), Image.LANCZOS)
ripe = frame('n3', 237); prod_bg = cover(Image.open(f'{B}fr/n5/0237.jpg'), int(W * 1.1), int(H * 1.1)).filter(ImageFilter.GaussianBlur(26))
prod_bg = ImageEnhance.Brightness(prod_bg).enhance(0.5).convert('RGBA')
grad = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(grad)
for y in range(H): d.line((0, y, W, y), fill=(int(70 + 30 * y / H), int(14 + 10 * y / H), int(28 + 14 * y / H), 255))
emb = Embers(40, seed=5)
def base(t):
    for a, b, n in SEG:
        if a <= t < b: break
    if n == 'n1a': return clipf('n1', t, a, b, 1, 237)
    if n == 'n1b': return clipf('n1', t, a, b, 50, 237)
    if n in ('n2', 'n3', 'n4', 'n5'): return clipf(n, t, a, b)
    if n == 'still':
        p = ease_in_out_sine((t - a) / (b - a)); s = 1.0 + 0.12 * p; w, h = int(W * s), int(H * s)
        return ripe.resize((w, h), Image.LANCZOS).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    fr = (prod_bg.crop((54, 96, 54 + W, 96 + H)) if n == 'prod' else grad.copy())
    emb.draw(fr, t, color=(255, 170, 190), alpha=0.7)
    k = entrance(t, a + 0.3, 0.6); dy, sc, ang = idle(t, 0.9, amp=7)
    img, y = (BIG, 960) if n == 'prod' else (END, 980)
    place(fr, img, W / 2, y + 240 * (1 - k) + dy, (0.7 + 0.3 * k) * sc, ang, clamp(k * 1.4)); return fr
fH = font('Inter-ExtraBold.otf', 130); fB = font('Inter-ExtraBold.otf', 90); fM = font('Inter-ExtraBold.otf', 66)
fP = font('Inter-ExtraBold.otf', 52); fS = font('Inter-Bold.otf', 42); fT = font('Inter-Medium.otf', 30)
RED = (190, 20, 50, 240); GREEN = (20, 110, 60, 240); DARK = (15, 15, 15, 220); GOLD = (255, 214, 110)
L = []
def add(s, e, ly, y): L.append((s, e, ly, y))
e = SEG[0][1]; add(0.1, e, text_layer('LA FRUTA QUE', fB), 220); add(0.9, e, text_layer('HUELE A QUESO', fH, fill=GOLD), 340)
add(0.5, e, text_layer('Recreación hecha con IA', fT, pill=(0, 0, 0, 150), pad=(22, 10)), 1580)
a, e, _ = SEG[1]; add(at('noni') - 0.1, e, text_layer('NONI', fH, fill=GOLD), 230); add(at('viene') - 0.1, e, text_layer('Del sudeste de Asia a todo el Pacífico', fS, pill=GREEN), 400)
add(at('hawái') - 0.1, e, text_layer('Hawái: NONI  ·  Tahití: NONO', fS, pill=DARK), 500)
a, e, _ = SEG[2]; add(at('morinda') - 0.1, e, text_layer('Morinda citrifolia', fM, fill=GOLD), 240); add(at('pariente') - 0.1, e, text_layer('Pariente del café', fP, pill=GREEN), 360)
add(at('árbol') - 0.1, e, text_layer('Da fruta todo el año', fS, pill=DARK), 470)
a, e, _ = SEG[3]; add(a + 0.2, SEG[4][1], text_layer('VERDE  →  CASI BLANCA', fP, pill=GREEN), 260)
a, e, _ = SEG[4]; add(at('fruta', 35) - 0.1, e, text_layer('"LA FRUTA\nDEL QUESO"', fH, fill=GOLD), 380)
a, e, _ = SEG[5]; add(at('tintes') - 0.1, e, text_layer('TINTES ROJOS Y AMARILLOS', fP, pill=RED), 260); add(at('raíz') + 0.6, e, text_layer('hechos con su raíz', fS, pill=DARK), 370)
a, e, _ = SEG[6]; add(at('jugo') - 0.1, t_ent - 0.1, text_layer('Bebida tradicional\ndel Pacífico Sur', fM, pill=GREEN), 240)
add(t_ent, e, text_layer('¿CÓMO SE TOMA ALGO\nQUE HUELE ASÍ?', fM), 240)
a, e, _ = SEG[7]; add(a + 0.2, e, text_layer('DXN', fH, fill=GOLD), 160); add(at('morinzhi') - 0.1, e, text_layer('MORINZHI', fB), 330)
add(at('concentrado') - 0.1, e, text_layer('Concentrado de noni + Jamaica', fP, pill=RED), 1390)
add(at('disimula') - 0.1, e, text_layer('La Jamaica disimula su olor (según DXN)', fS, pill=DARK), 1500)
a, e, _ = SEG[8]; add(a + 0.2, T, text_layer('¿TE ANIMARÍAS\nA PROBARLA?', fB), 200); add(at('cuéntame') - 0.1, T, text_layer('Cuéntame a qué te imaginas que sabe', fS, pill=RED), 1440)
add(a + 1.0, T, text_layer('Este producto no es un medicamento.\nEl consumo de este producto es responsabilidad\nde quien lo recomienda y de quien lo usa.', fT, pill=(0, 0, 0, 160), pad=(26, 12)), 1650)
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1): caps[i][1] = caps[i + 1][0] if caps[i + 1][0] - caps[i][1] < 0.6 else caps[i][1] + 0.25
KEY = {'QUESO', 'POLINESIOS', 'CANOAS', 'NONI', 'ASIA', 'PACÍFICO', 'HAWÁI', 'TAHITÍ', 'NONO', 'MORINDA', 'CITRIFOLIA', 'CAFÉ', 'AÑO', 'VERDE', 'BLANCA',
       'AÑEJO', 'TINTES', 'ROJOS', 'AMARILLOS', 'RAÍZ', 'TRADICIONAL', 'DXN', 'MORINZHI', 'JAMAICA', 'ANIMARÍAS', 'SABE'}
fC = font('Inter-ExtraBold.otf', 62)
def draw_caption(fr, txt, t, s):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2
    for w, ww in zip(ws, wd):
        col = (255, 214, 10) if w.strip('¿?¡!.,:"') in KEY else (255, 255, 255)
        d.text((x, 1730 + 30 * (1 - k)), w, font=fC, fill=col, stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
SL = SEG[7][0]
def frame_at(t):
    if SL - 0.4 <= t < SL + 0.4:
        return saber_slash(base(SL - 0.42), base(t if t >= SL else SL + 0.02), (t - SL + 0.4) / 0.8, color=(255, 90, 130))
    fr = base(t)
    for a, _, n in SEG[1:]:
        if n != 'prod' and a <= t < a + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 245, 240, 255)), 0.45 * (1 - (t - a) / 0.1))
    return fr
def compose(t):
    fr = frame_at(t)
    for i, (s, e, ly, y) in enumerate(L): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    for s, e, txt in caps:
        if s <= t < e and t < SEG[8][0]: draw_caption(fr, txt, t, s)
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
