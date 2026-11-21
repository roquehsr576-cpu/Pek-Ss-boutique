import sys, json, subprocess, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; B = R + 'agua/'
raw = [w for w in json.load(open(B + 'words.json'))['words'] if w.get('type') == 'word']
words = []
for w in raw:
    if w['text'].startswith('%') and words: words[-1] = dict(words[-1], text=words[-1]['text'] + w['text'], end=w['end'])
    else: words.append(dict(w))
T = 79.0
def at(txt, after=0.0):
    for w in words:
        if w['start'] >= after and w['text'].lower().strip('¿?¡!.,:%') == txt: return w['start']
    raise SystemExit('no ' + txt)
STILL = {k: Image.open(B + k + '.png').convert('RGB') for k in ['w1', 'w2', 'w3', 'w4']}
def kb(k, p, z0, z1, ox=0.0):
    im = STILL[k]; s = z0 + (z1 - z0) * p; bw = int(W * s); base = cover(im, bw, int(H * s))
    x = (base.width - W) / 2 + ox * (base.width - W) * (p - 0.5); y = (base.height - H) / 2
    return base.crop((int(x), int(y), int(x) + W, int(y) + H)).convert('RGBA')
def splash(p): i = int(1 + clamp(p) * 236); return Image.open(f'{B}fr/splash/{i:04d}.jpg').convert('RGBA')
grad = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(grad)
for y in range(H): d.line((0, y, W, y), fill=(int(6 + 10 * y / H), int(60 + 50 * y / H), int(120 + 60 * y / H), 255))
emb = Embers(45, seed=4)
t_org = at('tus'); t_beb = at('un', 20); t_per = at('y', 26); t_agu = at('el', 39.5); t_tres = at('tres'); t_dos = at('dos'); t_t3 = at('tres', 50.5); t_rec = at('el', 54.5); t_dato = at('y', 58.9); t_cuan = at('tú') - 0.2; t_teaser = at('quédate') - 0.15
SEG = [(0, t_org - 2.2, 'splash'), (t_org - 2.2, t_beb - 0.15, 'organs'), (t_beb - 0.15, t_per - 0.15, 'baby'), (t_per - 0.15, t_agu - 0.15, 'w2'),
       (t_agu - 0.15, t_tres - 0.15, 'w3'), (t_tres - 0.15, t_dos - 0.15, 'w1'), (t_dos - 0.15, t_t3 - 0.15, 'w2b'), (t_t3 - 0.15, t_rec - 0.15, 'splash2'),
       (t_rec - 0.15, t_dato - 0.15, 'splash3'), (t_dato - 0.15, t_cuan - 0.15, 'dato'), (t_cuan - 0.15, T, 'w4')]
fH = font('Inter-ExtraBold.otf', 120); fBig = font('Inter-ExtraBold.otf', 260); fB = font('Inter-ExtraBold.otf', 84); fM = font('Inter-ExtraBold.otf', 60)
fP = font('Inter-ExtraBold.otf', 50); fS = font('Inter-Bold.otf', 40); fT = font('Inter-Medium.otf', 28); fS2 = font('Inter-Bold.otf', 38)
BLUE = (10, 110, 200, 235); DARK = (8, 25, 45, 215); AQUA = (120, 220, 255); WHITE = (255, 255, 255)
ORG = [('PULMONES', 83, at('pulmones')), ('MÚSCULOS Y RIÑONES', 79, at('músculos')), ('CEREBRO Y CORAZÓN', 73, at('cerebro')), ('HUESOS', 31, at('huesos'))]
lblc = {}
def bar(fr, t, s, name, pct, y):
    k = entrance(t, s, 0.45)
    if k <= 0: return
    d = ImageDraw.Draw(fr); x0 = 520 + 150 * (1 - k); a = int(255 * clamp(k * 1.5))
    d.rounded_rectangle((x0, y, x0 + 530, y + 140), 26, fill=(8, 25, 45, int(200 * clamp(k * 1.5))))
    d.text((x0 + 24, y + 16), name, font=fS2, fill=(255, 255, 255, a))
    p = ease_out_cubic(clamp((t - s - 0.2) / 1.0)) * pct / 100
    d.rounded_rectangle((x0 + 24, y + 86, x0 + 360, y + 116), 15, fill=(255, 255, 255, 60))
    if p > 0.03: d.rounded_rectangle((x0 + 24, y + 86, x0 + 24 + 336 * p, y + 116), 15, fill=(80, 200, 255, 255))
    d.text((x0 + 378, y + 62), f'{int(round(p * 100))}%', font=fM, fill=(120, 220, 255, a))
FX = 290
def body_mask():
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse((FX - 85, 430, FX + 85, 610), fill=255); d.rectangle((FX - 30, 600, FX + 30, 650), fill=255)
    d.rounded_rectangle((FX - 120, 640, FX + 120, 1070), 60, fill=255)
    d.rounded_rectangle((FX - 178, 655, FX - 128, 1070), 25, fill=255); d.rounded_rectangle((FX + 128, 655, FX + 178, 1070), 25, fill=255)
    d.rounded_rectangle((FX - 110, 1030, FX - 12, 1520), 40, fill=255); d.rounded_rectangle((FX + 12, 1030, FX + 110, 1520), 40, fill=255)
    return m
BODY = body_mask(); BODY_EDGE = BODY.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
ORGANS = {0: [('e', (FX - 95, 690, FX - 15, 860)), ('e', (FX + 15, 690, FX + 95, 860))],
          1: [('e', (FX - 100, 1080, FX - 22, 1280)), ('e', (FX + 22, 1080, FX + 100, 1280)), ('e', (FX - 70, 910, FX - 30, 975)), ('e', (FX + 30, 910, FX + 70, 975))],
          2: [('e', (FX - 62, 465, FX + 62, 560)), ('e', (FX + 8, 770, FX + 62, 825))],
          3: [('l', (FX - 61, 1060, FX - 61, 1490)), ('l', (FX + 61, 1060, FX + 61, 1490)), ('l', (FX - 153, 680, FX - 153, 1040)), ('l', (FX + 153, 680, FX + 153, 1040)),
              ('l', (FX, 650, FX, 1030))]}
def figure(fr, t, a):
    k = clamp((t - a) / 0.6)
    if k <= 0: return
    lvl = 1520 - (1520 - 430) * 0.6 * ease_out_cubic(clamp((t - a - 0.3) / 2.0))
    water = Image.new('RGBA', (W, H)); wd = ImageDraw.Draw(water)
    wd.polygon([(x, lvl + 10 * math.sin(x / 40 + t * 4)) for x in range(0, 620, 10)] + [(620, H), (0, H)], fill=(70, 190, 255, 200))
    glass = Image.new('RGBA', (W, H), (255, 255, 255, int(45 * k)))
    fr.alpha_composite(Image.composite(glass, Image.new('RGBA', (W, H)), BODY))
    fr.alpha_composite(Image.composite(water, Image.new('RGBA', (W, H)), BODY.point(lambda v: int(v * k))))
    fr.alpha_composite(Image.composite(Image.new('RGBA', (W, H), (255, 255, 255, int(230 * k))), Image.new('RGBA', (W, H)), BODY_EDGE))
    act = None
    for i, (_, _, s) in enumerate(ORG):
        if t >= s - 0.2: act = i
    ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
    for i, shapes in ORGANS.items():
        on = (i == act); pul = 0.5 + 0.5 * math.sin(t * 6) if on else 0
        col = (255, 230, 90, int(200 + 55 * pul)) if on else (255, 255, 255, 70 if act is not None and i < act else 0)
        for kind, box in shapes:
            if kind == 'e': od.ellipse(box, fill=col, outline=(255, 255, 255, 200) if on else None, width=4)
            else: od.line(box, fill=col, width=14)
    fr.alpha_composite(ov.filter(ImageFilter.GaussianBlur(2)))
def drop(fr, t, s, pct, cx, cy, r):
    m = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(m)
    dd.ellipse((cx - r, cy - r * 0.2, cx + r, cy + r * 1.8), fill=255); dd.polygon([(cx, cy - r * 1.6), (cx - r * 0.98, cy + r * 0.5), (cx + r * 0.98, cy + r * 0.5)], fill=255)
    top, bot = cy - r * 1.6, cy + r * 1.8; lvl = bot - (bot - top) * pct * ease_out_cubic(clamp((t - s) / 1.6))
    water = Image.new('RGBA', (W, H)); wd = ImageDraw.Draw(water)
    pts = [(x, lvl + 14 * math.sin(x / 70 + t * 4)) for x in range(0, W + 20, 20)] + [(W, H), (0, H)]
    wd.polygon(pts, fill=(80, 200, 255, 255))
    shell = Image.new('RGBA', (W, H), (255, 255, 255, 50)); fr.alpha_composite(Image.composite(shell, Image.new('RGBA', (W, H)), m))
    fr.alpha_composite(Image.composite(water, Image.new('RGBA', (W, H)), m))
STATES = [('SÓLIDA', 'hielo', 'sólida', 210), ('LÍQUIDA', 'agua', 'líquida', 540), ('GAS', 'vapor', 'gas', 870)]
def estados(fr, t):
    d = ImageDraw.Draw(fr)
    for name, sub, wd_, x in STATES:
        s = at(wd_) - 0.15; k = entrance(t, s, 0.5)
        if k <= 0: continue
        dy, sc, ang = idle(t, x, amp=6); cy = 950 + 160 * (1 - k) + dy; a = int(255 * clamp(k * 1.5)); r = 120 * (0.7 + 0.3 * k)
        if name == 'SÓLIDA':
            d.rounded_rectangle((x - r, cy - r, x + r, cy + r), 30, fill=(200, 240, 255, a), outline=(255, 255, 255, a), width=6)
            d.line((x - r * 0.6, cy - r * 0.6, x - r * 0.1, cy - r * 0.6), fill=(255, 255, 255, a), width=10)
        elif name == 'LÍQUIDA':
            d.ellipse((x - r, cy - r * 0.4, x + r, cy + r * 1.2), fill=(80, 200, 255, a)); d.polygon([(x, cy - r * 1.3), (x - r * 0.95, cy + r * 0.25), (x + r * 0.95, cy + r * 0.25)], fill=(80, 200, 255, a))
        else:
            for ox, oy, rr in [(-55, 20, 70), (40, 0, 85), (0, -60, 70), (95, 40, 55), (-95, 50, 50)]:
                d.ellipse((x + ox - rr, cy + oy - rr, x + ox + rr, cy + oy + rr), fill=(235, 245, 255, int(a * 0.9)))
        tl = text_layer(name, fP, fill=(255, 255, 255)); place(fr, tl, x, cy + 230, 1, 0, clamp(k * 1.5))
        tl2 = text_layer(sub, fS, fill=AQUA); place(fr, tl2, x, cy + 300, 1, 0, clamp(k * 1.5))
def base(t):
    for a, b, n in SEG:
        if a <= t < b: break
    p = ease_in_out_sine((t - a) / (b - a))
    if n == 'splash': return splash((t - a) / (b - a))
    if n == 'splash2': return splash(0.55 + 0.45 * (t - a) / (b - a))
    if n == 'splash3': return splash(0.3 + 0.3 * (t - a) / (b - a))
    if n == 'dato':
        fr = grad.copy(); emb.draw(fr, t, color=(200, 240, 255), alpha=0.6); estados(fr, t); return fr
    if n in ('organs', 'baby'):
        fr = grad.copy(); emb.draw(fr, t, color=(200, 240, 255), alpha=0.6)
        if n == 'organs':
            figure(fr, t, a + 0.3)
            for i, (nm, pc, s) in enumerate(ORG): bar(fr, t, s - 0.2, nm, pc, 560 + i * 200)
        else: drop(fr, t, a + 0.6, 0.78, W / 2, 930, 260)
        return fr
    if n == 'w2': return kb('w2', p, 1.0, 1.12)
    if n == 'w2b': return kb('w2', p, 1.15, 1.25, 0.6)
    if n == 'w3': return kb('w3', p, 1.12, 1.0)
    if n == 'w1': return kb('w1', p, 1.0, 1.12)
    return kb('w4', p, 1.0, 1.1)
L = []
def add(s, e, ly, y): L.append((s, e, ly, y))
e = SEG[0][1]; add(0.2, t_teaser, text_layer('TU CUERPO ES', fB), 260)
add(t_teaser + 0.1, e, text_layer('QUÉDATE\nAL FINAL', fH, fill=AQUA, stroke=10), 480)
add(at('dato') - 0.1, e, text_layer('Te tengo un dato que casi nadie sabe', fS, pill=BLUE), 820)
add(at('regular') - 0.2, t_tres - 0.2, text_layer('El dato final ya viene...', fS, pill=(200, 30, 60, 235)), 1460)
add(at('recurso') + 0.4, t_dato - 0.15, text_layer('Ahora sí: el dato...', fS, pill=(200, 30, 60, 235)), 1460)
a0, e0, _ = SEG[9]
add(a0 + 0.1, e0, text_layer('EL DATO QUE', fB), 170); add(a0 + 0.5, e0, text_layer('CASI NADIE SABE', fB, fill=AQUA), 270)
add(at('única') - 0.1, e0, text_layer('El agua es la única sustancia natural\nen la Tierra en sus 3 estados', fS, pill=BLUE), 410)
add(at('sólida') + 0.5, e0, text_layer('Fuente: USGS', fT, pill=(0, 0, 0, 140), pad=(20, 8)), 1570)
add(t_org - 2.0, SEG[1][1], text_layer('Y NO ESTÁ REPARTIDA IGUAL', fP, pill=BLUE), 200)
add(t_org - 1.6, SEG[1][1], text_layer('Agua en cada parte del cuerpo', fS, fill=AQUA), 310)
add(t_org - 1.0, SEG[1][1], text_layer('Fuente: USGS · Mitchell et al., 1945', fT, pill=(0, 0, 0, 140), pad=(20, 8)), 1570)
a, e, _ = SEG[2]; add(a + 0.1, e, text_layer('RECIÉN NACIDO', fB, fill=WHITE), 240); add(a + 2.6, e, text_layer('≈ 78% AGUA', fH, fill=AQUA), 1420)
a, e, _ = SEG[3]
for i, (wd_, lab) in enumerate([('respirar', 'AL RESPIRAR'), ('sudar', 'AL SUDAR'), ('moverte', 'AL MOVERTE')]): add(at(wd_) - 0.3, at('por') - 0.2, text_layer(lab, fP, pill=BLUE), 300 + i * 115)
add(at('por') - 0.1, e, text_layer('EL AGUA NO SE GUARDA', fM), 280); add(at('repone') - 0.2, e, text_layer('SE REPONE', fH, fill=AQUA), 400)
a, e, _ = SEG[4]; add(at('regular') - 0.2, e, text_layer('Regula la temperatura del cuerpo', fS, pill=DARK), 300); add(at('lubrica') - 0.2, e, text_layer('Lubrica las articulaciones', fS, pill=DARK), 400)
add(t_tres - 0.1, t_dos - 0.15, text_layer('3 HÁBITOS SENCILLOS', fP, pill=BLUE), 230)
add(at('uno') - 0.1, t_dos - 0.15, text_layer('1', fBig, fill=AQUA, stroke=10), 330); add(at('vaso') - 0.1, t_dos - 0.15, text_layer('Un vaso al despertar', fM, pill=DARK), 640)
add(t_dos - 0.1, t_t3 - 0.15, text_layer('2', fBig, fill=AQUA, stroke=10), 230); add(at('botella') - 0.4, t_t3 - 0.15, text_layer('Lleva tu botella contigo', fM, pill=DARK), 540)
add(t_t3 - 0.1, t_rec - 0.15, text_layer('3', fBig, fill=AQUA, stroke=10), 230); add(at('calor') - 0.2, t_rec - 0.15, text_layer('Con calor o más movimiento,\ntoma un poco más', fP, pill=DARK), 540)
a, e, _ = SEG[8]; add(a + 0.1, e, text_layer('EL AGUA', fH), 280); add(at('recurso') - 0.1, e, text_layer('el recurso natural que tu\ncuerpo usa todos los días', fP, pill=BLUE), 440)
a = SEG[10][0]; add(at('cuántos') - 0.1, T, text_layer('¿CUÁNTOS VASOS\nLLEVAS HOY?', fB), 220); add(at('cuéntame') - 0.1, T, text_layer('Cuéntame en los comentarios', fS, pill=BLUE), 1440)
add(0.5, T, text_layer('Imágenes creadas con IA', fT, pill=(0, 0, 0, 120), pad=(18, 8)), 1866)
logo = Image.open(R + 'clip/dxn-logo.png').convert('RGBA').resize((120, 116), Image.LANCZOS)
lb = Image.new('RGBA', (140, 136)); m = Image.new('L', (140, 136), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 139, 135), 22, fill=230)
lb.paste((255, 255, 255, 255), (0, 0), m); lb.alpha_composite(logo, (10, 10)); bigl = Image.open(R + 'clip/dxn-logo.png').convert('RGBA').resize((300, 290), Image.LANCZOS)
blg = Image.new('RGBA', (340, 330)); m2 = Image.new('L', (340, 330), 0); ImageDraw.Draw(m2).rounded_rectangle((0, 0, 339, 329), 40, fill=240); blg.paste((255, 255, 255, 255), (0, 0), m2); blg.alpha_composite(bigl, (20, 20))
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1): caps[i][1] = caps[i + 1][0] if caps[i + 1][0] - caps[i][1] < 0.6 else caps[i][1] + 0.25
KEY = {'AGUA', 'CUERPO', 'MITAD', '60%', '83%', '79', '73', '31%', '78%', 'PULMONES', 'MÚSCULOS', 'RIÑONES', 'CEREBRO', 'CORAZÓN', 'HUESOS', 'BEBÉ', 'RESPIRAR', 'SUDAR',
       'MOVERTE', 'FINAL', 'DATO', 'SÓLIDA', 'LÍQUIDA', 'GAS', 'HIELO', 'VAPOR', 'ESTADOS', 'ÚNICA', 'REPONE', 'TEMPERATURA', 'ARTICULACIONES', 'VASO', 'DESPERTAR', 'BOTELLA', 'CALOR', 'RECURSO', 'NATURAL', 'VASOS', 'HOY'}
fC = font('Inter-ExtraBold.otf', 62)
def draw_caption(fr, txt, t, s):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2
    for w, ww in zip(ws, wd):
        col = (120, 220, 255) if w.strip('¿?¡!.,:') in KEY else (255, 255, 255)
        d.text((x, 1700 + 30 * (1 - k)), w, font=fC, fill=col, stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
def counter(fr, t):
    s = at('60') - 0.4
    if s <= t < t_teaser:
        k = entrance(t, s, 0.5) * (1 - clamp((t - t_teaser + 0.3) / 0.3)); v = int(round(60 * ease_out_cubic(clamp((t - s) / 1.0))))
        ly = text_layer(f'{v}%', fBig, fill=AQUA, stroke=12); place(fr, ly, W / 2, 620 + 80 * (1 - k), 0.8 + 0.2 * k, 0, clamp(k * 1.5))
        ly2 = text_layer('AGUA', fH, stroke=8); place(fr, ly2, W / 2, 860, 1, 0, clamp(k * 1.5))
def compose(t):
    fr = base(t)
    for a, _, n in SEG[1:]:
        if a <= t < a + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (230, 250, 255, 255)), 0.45 * (1 - (t - a) / 0.1))
    counter(fr, t)
    for i, (s, e, ly, y) in enumerate(L): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    if SEG[10][0] + 3.0 <= t: k = entrance(t, SEG[10][0] + 3.0, 0.6); dy, sc, ang = idle(t, 1, amp=5); place(fr, blg, W / 2, 1220 + 150 * (1 - k) + dy, (0.5 + 0.3 * k) * sc, ang, clamp(k * 1.4))
    for s, e, txt in caps:
        if s <= t < e and t < at('cuántos') - 0.1: draw_caption(fr, txt, t, s)
    fr.alpha_composite(lb, (W - 170, 40)); return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(min(hi, T) * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
