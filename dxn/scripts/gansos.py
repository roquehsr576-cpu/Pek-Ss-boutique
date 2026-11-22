import sys, json, subprocess, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; B = R + 'gansos/'
words = [w for w in json.load(open(B + 'words3.json'))['words'] if w.get('type') == 'word']
T = math.ceil(words[-1]['end'] + 4.0)
def at(txt, after=0.0):
    for w in words:
        if w['start'] >= after and w['text'].lower().strip('¿?¡!.,:') == txt: return w['start']
    raise SystemExit('no ' + txt)
IMG = {'des': B + 'g0_desierto.png', 'cel': B + 'g1_celular.png', 'com': B + 'g2_comida.png', 'mon': B + 'g3_montana.png', 'gv': B + 'g4_gansos.png', 'gc': B + 'g5_gansos_cerca.png',
       'team': R + 'clip/l1.png', 'fam': R + 'clip/m1.png', 'ofi': R + 'clip/m6.png', 'cafe': R + 'clip/m2.png'}
ST = {}
def kb(k, p, z0, z1, oy=0.0):
    if k not in ST: ST[k] = Image.open(IMG[k]).convert('RGB')
    im = ST[k]; s = z0 + (z1 - z0) * p; base = cover(im, int(W * s), int(H * s))
    x = (base.width - W) / 2; y = (base.height - H) / 2 + oy * (base.height - H) * (p - 0.5)
    return base.crop((int(x), int(y), int(x) + W, int(y) + H)).convert('RGBA')
t1 = at('paso'); t2 = at('paso', t1 + 1); t3 = at('paso', t2 + 1); tav = at('y', at('desierto')); tal = at('al', at('midieron')); tse = at('se', at('energía')); tas = at('así'); tno = at('no', at('solitario'))
tun = at('un', at('familia')); tyo = at('yo'); tq = at('y', at('volar', tyo)); tnad = at('nadie', t3)
SEG = [(0, at('son') - 0.2, 'des', 1, 140), (at('son') - 0.2, t1 - 0.2, 'gv', 1, 120),
       (t1 - 0.2, t2 - 0.2, 'cel', 1, 237), (t2 - 0.2, t3 - 0.2, 'com', 1, 237),
       (t3 - 0.2, tnad - 0.2, 'mon', 1, 237), (tnad - 0.2, tav - 0.2, 'des', 120, 237), (tav - 0.2, tal - 0.2, 'gv', 1, 150), (tal - 0.2, tse - 0.2, 'diag', 0, 0), (tse - 0.2, tas - 0.2, 'gc', 1, 237),
       (tas - 0.2, tno - 0.2, 'team', 1, 237), (tno - 0.2, tun - 0.2, 'fam', 1, 237), (tun - 0.2, tyo - 0.2, 'ofi', 1, 237), (tyo - 0.2, tq - 0.2, 'cafe', 1, 237), (tq - 0.2, T, 'gv', 1, 150)]
FR = {'des': B + 'fr/m0', 'cel': B + 'fr/m1', 'com': B + 'fr/m2', 'mon': B + 'fr/m3', 'gv': B + 'fr/m4', 'gc': B + 'fr/m5', 'team': R + 'clip/fr/a1', 'fam': R + 'clip/fr/b1', 'ofi': R + 'clip/fr/b6', 'cafe': R + 'clip/fr/b2'}
sky = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(sky)
for y in range(H): d.line((0, y, W, y), fill=(int(40 + 200 * y / H), int(70 + 90 * y / H), int(140 - 40 * y / H), 255))
def bird(dr, x, y, s, flap, col=(20, 20, 30, 255)):
    wy = 30 * s * flap
    dr.polygon([(x - 70 * s, y - wy), (x - 10 * s, y + 6 * s), (x, y - 4 * s), (x + 10 * s, y + 6 * s), (x + 70 * s, y - wy), (x + 8 * s, y + 18 * s), (x - 8 * s, y + 18 * s)], fill=col)
def diag(t, a, b):
    fr = sky.copy(); dr = ImageDraw.Draw(fr); p = (t - a) / (b - a)
    pos = [(0, 0)] + [(sgn * i, i) for i in range(1, 5) for sgn in (-1, 1)]
    cx, cy0 = W / 2, 620
    lead = int(p * 3) % 3  # rotate lead visually
    for j, (ix, iy) in enumerate(pos):
        x = cx + ix * 120; y = cy0 + iy * 135 + 8 * math.sin(t * 3 + j)
        flap = math.sin(t * 7 + j * 0.6)
        k = entrance(t, a + 0.15 * j, 0.4)
        if k <= 0: continue
        bird(dr, x, y + 60 * (1 - k), 1.3, flap, (255, 214, 90, 255) if j == 0 else (25, 25, 40, 255))
        if j > 0 and t > a + 1.4:
            px = x - (0.5 if ix < 0 else -0.5) * 105 * 0.7; ar = clamp((t - a - 1.4) / 0.6)
            dr.line((px, y - 70, px + (20 if ix < 0 else -20), y - 20), fill=(120, 220, 255, int(220 * ar)), width=6)
    return fr
def base(t):
    for a, b, k, z0, z1 in SEG:
        if a <= t < b: break
    if k == 'diag': return diag(t, a, b)
    i = int(z0 + (z1 - z0) * clamp((t - a) / (b - a)))
    return Image.open(f'{FR[k]}/{max(1, min(237, i)):04d}.jpg').convert('RGBA')
fH = font('Inter-ExtraBold.otf', 110); fBig = font('Inter-ExtraBold.otf', 260); fB = font('Inter-ExtraBold.otf', 80); fM = font('Inter-ExtraBold.otf', 60)
fP = font('Inter-ExtraBold.otf', 48); fS = font('Inter-Bold.otf', 40); fT = font('Inter-Medium.otf', 28)
GOLD = (255, 214, 90); DARK = (10, 10, 20, 215); GREEN = (25, 120, 70, 235); RED = (200, 25, 40, 240)
L = []
def add(s, e, ly, y): L.append((s, e, ly, y))
add(0.1, at('son') - 0.2, text_layer('¿QUIERES MEJORAR\nTUS HÁBITOS?', fB, stroke=8), 240)
add(at('no') - 0.1, at('son') - 0.2, text_layer('No empieces por la comida...', fM, fill=GOLD, stroke=7), 480)
add(at('empieza') - 0.1, at('son') - 0.2, text_layer('EMPIEZA POR ESTO', fP, pill=RED), 600)
add(at('son') - 0.1, t1 - 0.2, text_layer('3 PASOS', fH, stroke=8), 260)
add(at('último') - 0.2, t1 - 0.2, text_layer('El último te lo enseñan\nunas aves', fS, pill=RED), 430)
for (ts, te, n, title, chips) in [(t1, t2, '1', 'CUIDA LO QUE CONSUMES', [('comes', 'Lo que comes'), ('ves', 'Lo que ves'), ('escuchas', 'Lo que escuchas'), ('menos', 'Menos noticias negativas'), ('más', 'Más personas que te sumen')]),
                                   (t2, t3, '2', 'ELIGE COMIDA REAL', [('natural', 'Más natural'), ('procesado', 'Menos procesado'), ('olvides', 'Y no olvides el agua')]),
                                   (t3, tnad, '3', 'AGUANTA EL PROCESO', [('cambiar', 'Cambiar es incómodo...')])]:
    e = te - 0.2; add(ts - 0.1, e, text_layer(n, fBig, fill=GOLD, stroke=10), 120); add(ts + 0.3, e, text_layer(title, fP, pill=GREEN), 430)
    for i, (w, lab) in enumerate(chips): add(at(w, ts) - 0.2, e, text_layer(lab, fS, pill=DARK), 560 + i * 95)
add(tnad - 0.1, tav - 0.2, text_layer('NADIE ENCUENTRA\nSU PARAÍSO...', fB, stroke=8), 260); add(at('sin', tnad) - 0.1, tav - 0.2, text_layer('sin antes cruzar\nsu desierto', fM, fill=GOLD, stroke=7), 500)
add(tav - 0.1, tal - 0.2, text_layer('¿Y LAS AVES?', fH, stroke=8), 260); add(at('forma') - 0.2, tal - 0.2, text_layer('Vuelan en forma de V', fM, fill=GOLD, stroke=7), 420)
add(at('casualidad') - 0.2, tal - 0.2, text_layer('No es casualidad', fS, pill=DARK), 540)
add(tal - 0.1, tse - 0.2, text_layer('Cada ave aprovecha el aire\nque mueve la de adelante', fS, pill=DARK), 1250)
add(at('gasta') - 0.2, tse - 0.2, text_layer('= GASTA MENOS ENERGÍA', fM, fill=GOLD, stroke=7), 1400)
add(tse - 0.1, tas - 0.2, text_layer('SE TURNAN EL LUGAR\nDE ENFRENTE', fB, stroke=8), 220); add(at('nadie', tse) - 0.2, tas - 0.2, text_layer('Nadie compite: se cuidan', fM, fill=GOLD, stroke=7), 470)
add(at('científicos') - 0.2, tas - 0.2, text_layer('Fuentes: Nature 2001 y 2014 · PNAS 2015', fT, pill=(0, 0, 0, 140), pad=(18, 8)), 1560)
add(tas + 1.2, tno - 0.2, text_layer('EL TRABAJO EN EQUIPO', fM, stroke=7), 220); add(at('rinde') - 0.2, tno - 0.2, text_layer('rinde más frutos que el\nesfuerzo en solitario', fP, pill=GREEN), 330)
add(tno - 0.1, tun - 0.2, text_layer('NO COMPITAS POR ENVIDIA', fM, stroke=7), 220); add(at('cuida', tno) - 0.2, tun - 0.2, text_layer('Cuida a tus socios,\namigos y familia', fP, pill=GREEN), 330)
add(tun - 0.1, tyo - 0.2, text_layer('UN EQUIPO SÓLIDO', fB, fill=GOLD, stroke=8), 220); add(at('vale', tun) - 0.2, tyo - 0.2, text_layer('vale más que cualquier cosa', fP, pill=DARK), 350)
add(at('café', tyo) - 0.2, tq - 0.2, text_layer('Mi momento antes de salir a volar', fS, pill=DARK), 1300)
add(tq - 0.1, T, text_layer('¿Y TÚ, QUIÉN ES\nTU EQUIPO?', fB, stroke=8), 240); add(at('cuéntame') - 0.1, T, text_layer('Cuéntame en los comentarios', fS, pill=RED), 1440)
add(0.5, T, text_layer('Imágenes creadas con IA', fT, pill=(0, 0, 0, 110), pad=(16, 7)), 1866)
pack = Image.open(R + 'carrusel/prod/black.png').convert('RGBA'); pack.thumbnail((330, 430), Image.LANCZOS)
logo = Image.open(R + 'clip/dxn-logo.png').convert('RGBA').resize((110, 106), Image.LANCZOS)
lb = Image.new('RGBA', (130, 126)); m = Image.new('L', (130, 126), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 129, 125), 20, fill=230); lb.paste((255, 255, 255, 255), (0, 0), m); lb.alpha_composite(logo, (10, 10))
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1): caps[i][1] = caps[i + 1][0] if caps[i + 1][0] - caps[i][1] < 0.6 else caps[i][1] + 0.25
KEY = {'PARAÍSO', 'DESIERTO', 'HÁBITOS', 'ESTO', 'COMIDA', 'PASOS', 'AVES', 'CONSUMES', 'VES', 'ESCUCHAS', 'COMIDA', 'REAL', 'AGUA', 'PROCESO', 'GANSOS', 'V', 'CIENTÍFICOS', 'ENERGÍA',
       'TURNAN', 'CUIDAN', 'EQUIPO', 'FRUTOS', 'ENVIDIA', 'SOCIOS', 'AMIGOS', 'FAMILIA', 'SÓLIDO', 'GANODERMA', 'VOLAR'}
fC = font('Inter-ExtraBold.otf', 60)
def draw_caption(fr, txt, t, s):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2
    for w, ww in zip(ws, wd):
        col = (255, 214, 10) if w.strip('¿?¡!.,:') in KEY else (255, 255, 255)
        d.text((x, 1700 + 30 * (1 - k)), w, font=fC, fill=col, stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
def compose(t):
    fr = base(t)
    for a, _, k, _, _ in SEG[1:]:
        if a <= t < a + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 250, 235, 255)), 0.4 * (1 - (t - a) / 0.1))
    if SEG[12][0] <= t < SEG[12][1]:
        k = entrance(t, at('café', tyo) - 0.1, 0.5); dy, sc, ang = idle(t, 1, amp=6); place(fr, pack, W - 220, 1110 + 160 * (1 - k) + dy, (0.75 + 0.25 * k) * sc, ang + 5, clamp(k * 1.4))
    for i, (s, e, ly, y) in enumerate(L): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    for s, e, txt in caps:
        if s <= t < e and t < tq - 0.2: draw_caption(fr, txt, t, s)
    fr.alpha_composite(lb, (W - 160, 40)); return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(min(hi, T) * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
