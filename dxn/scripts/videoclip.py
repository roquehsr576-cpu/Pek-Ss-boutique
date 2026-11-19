import sys, json, subprocess, math, random
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; B = R + 'clip/'
words = [w for w in json.load(open(B + 'words.json'))['words'] if w.get('type') == 'word']
T = 138.4
SEG = [(0, 3.0, 'e6', 120, 237), (3.0, 8.5, 'a2', 1, 165), (8.5, 13.2, 'd5', 1, 141), (13.2, 17.8, 'a1', 1, 138),
       (17.8, 22.8, 'e2', 1, 150), (22.8, 27.7, 'e3', 1, 147), (27.7, 29.8, 'e4', 60, 123), (29.8, 32.2, 'e5', 40, 112),
       (32.2, 37.5, 'a3', 1, 159), (37.5, 42.2, 'a1', 1, 141), (42.2, 46.7, 'd1', 1, 135), (46.7, 52.4, 'd3', 1, 171),
       (52.4, 56.5, 'd5', 100, 223), (56.5, 60.5, 'd6', 1, 120), (60.5, 65.3, 'a5', 1, 144), (65.3, 67.4, 'e4', 1, 63),
       (67.4, 69.9, 'e1', 1, 75), (69.9, 74.5, 'a4', 1, 138), (74.5, 78.9, 'd2', 1, 132), (78.9, 83.9, 'd4', 1, 150),
       (83.9, 88.1, 'd5', 1, 126), (88.1, 92.7, 'e6', 1, 138), (92.7, 97.5, 'd6', 90, 237), (97.5, 99.8, 'a3', 120, 189),
       (99.8, 104.3, 'a1', 100, 237), (104.3, 108.4, 'a4', 100, 223), (108.4, 112.4, 'd1', 100, 220), (112.4, 116.5, 'a2', 100, 223),
       (116.5, T, 'end', 0, 0)]
def pk(path, h):
    im = Image.open(path).convert('RGBA'); r = h / im.height; return im.resize((max(1, int(im.width * r)), h), Image.LANCZOS)
P = {'black': R + 'carrusel/prod/black.png', 'cocozhi': R + 'carrusel/prod/cocozhi.png', 'l3en1': R + 'canela/l3en1.png',
     'cereal': R + 'espirulina/prod/FB032.png', 'morinzhi': R + 'noni/prod/FB007.png', 'caps': R + 'espirulina/prod/HF037.png'}
SMALL = {k: pk(v, 380 if k != 'cereal' else 250) for k, v in P.items()}
PACKS = {17.8: ['l3en1'], 22.8: ['black'], 27.7: ['cocozhi'], 29.8: ['cereal', 'morinzhi']}
logo = Image.open(B + 'dxn-logo.png').convert('RGBA'); logo = logo.resize((120, 116), Image.LANCZOS)
lb = Image.new('RGBA', (140, 136), (255, 255, 255, 0)); m = Image.new('L', (140, 136), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 139, 135), 22, fill=225)
lb.paste((255, 255, 255, 255), (0, 0), m); lb.alpha_composite(logo, (10, 10))
END = [pk(P[k], h) for k, h in [('black', 430), ('cocozhi', 430), ('l3en1', 430), ('morinzhi', 470)]] ; END_C = pk(P['cereal'], 300)
grad = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(grad)
for y in range(H): d.line((0, y, W, y), fill=(int(150 - 90 * y / H), int(16 + 6 * y / H), int(28 + 10 * y / H), 255))
emb = Embers(50, seed=9)
def star_shape(r, col=(255, 214, 80, 255)):
    im = Image.new('RGBA', (2 * r + 4, 2 * r + 4)); pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.45
        pts.append((r + 2 + rr * math.cos(a), r + 2 + rr * math.sin(a)))
    dd = ImageDraw.Draw(im); dd.polygon(pts, fill=col, outline=(255, 255, 255, 255)); return im
def crown_shape(w):
    h = int(w * 0.75); im = Image.new('RGBA', (w + 8, h + 8)); dd = ImageDraw.Draw(im); o = 4
    pts = [(o, o + h), (o, o + h * 0.3), (o + w * 0.25, o + h * 0.6), (o + w * 0.5, o), (o + w * 0.75, o + h * 0.6), (o + w, o + h * 0.3), (o + w, o + h)]
    dd.polygon(pts, fill=(255, 200, 40, 255), outline=(150, 90, 0, 255), width=max(2, w // 40))
    dd.rectangle((o, o + h * 0.82, o + w, o + h), fill=(230, 160, 20, 255))
    for cx, cy in [(o, o + h * 0.3), (o + w * 0.5, o), (o + w, o + h * 0.3)]: dd.ellipse((cx - w * 0.07, cy - w * 0.07, cx + w * 0.07, cy + w * 0.07), fill=(220, 30, 60, 255))
    return im
STAR = star_shape(70); CROWN = crown_shape(380); CROWN_S = crown_shape(110)
st_times = [w['start'] for w in words if w['text'].lower().startswith('estrell')]
cr_times = [w['start'] for w in words if w['text'].lower().startswith('coron')]
def effects(fr, t):
    for s in st_times:
        if s <= t < s + 1.3:
            p = (t - s) / 1.3; rnd = random.Random(int(s * 100))
            for i in range(9):
                a = rnd.uniform(0, 2 * math.pi); dist = 150 + 520 * ease_out_cubic(p) * rnd.uniform(0.6, 1.1)
                x = W / 2 + dist * math.cos(a); y = 820 + dist * math.sin(a) * 0.9
                place(fr, STAR, x, y, 0.4 + 0.5 * rnd.random(), p * 300 * (1 if i % 2 else -1), clamp(1.6 - 1.6 * p))
    for s in cr_times:
        if s <= t < s + 1.4:
            p = (t - s) / 1.4; k = ease_out_back(clamp(p / 0.4), 1.8)
            place(fr, CROWN, W / 2, -200 + 820 * k, 0.9, 6 * math.sin(t * 8), clamp(1.5 - 1.5 * clamp((p - 0.6) / 0.4)))
def frame_of(n, t, a, b, f0, f1):
    p = clamp((t - a) / (b - a)); i = int(f0 + p * (f1 - f0))
    return Image.open(f'{B}fr/{n}/{max(1, min(237, i)):04d}.jpg').convert('RGBA')
def base(t):
    for a, b, n, f0, f1 in SEG:
        if a <= t < b: break
    if n == 'end':
        fr = grad.copy(); emb.draw(fr, t, color=(255, 210, 140), alpha=0.8)
        xs = [190, 430, 650, 890]
        for j, (im, x) in enumerate(zip(END, xs)):
            k = entrance(t, a + 0.6 + j * 0.2, 0.55); dy, sc, ang = idle(t, j, amp=6)
            place(fr, im, x, 1050 + 200 * (1 - k) + dy, (0.7 + 0.3 * k) * sc, ang, clamp(k * 1.4))
        k = entrance(t, a + 1.5, 0.55); dy, sc, ang = idle(t, 7, amp=5)
        place(fr, END_C, W / 2, 1390 + 200 * (1 - k) + dy, (0.7 + 0.3 * k) * sc, ang, clamp(k * 1.4))
        return fr
    fr = frame_of(n, t, a, b, f0, f1)
    for s0, keys in PACKS.items():
        if a == s0:
            for j, kk in enumerate(keys):
                k = entrance(t, a + 0.3 + j * 0.25, 0.5); dy, sc, ang = idle(t, j + 1, amp=6)
                x = W - 230 if j == 0 else 230
                place(fr, SMALL[kk], x, 1300 + 160 * (1 - k) + dy, (0.75 + 0.25 * k) * sc, ang + (5 if j == 0 else -5), clamp(k * 1.4))
    return fr
fH = font('Inter-ExtraBold.otf', 140); fB = font('Inter-ExtraBold.otf', 96); fM = font('Inter-ExtraBold.otf', 66)
fP = font('Inter-ExtraBold.otf', 52); fS = font('Inter-Bold.otf', 42); fT = font('Inter-Medium.otf', 28)
RED = (200, 20, 40, 240); GOLD = (255, 214, 90); DARK = (15, 15, 15, 210)
L = []
def add(s, e, ly, y): L.append((s, e, ly, y))
add(6.6, 8.5, text_layer('¡EQUIPO DXN!', fH, fill=GOLD, stroke=10), 700)
add(8.7, 17.6, text_layer('PASITO A PASITO', fB, fill=GOLD, stroke=8), 300); add(9.6, 17.6, text_layer('#PasitoAPasitoDXN', fP, pill=RED), 450)
add(10.6, 17.6, text_layer('¡Aprende el paso y súmate al reto!', fS, pill=DARK), 1450)
add(113.9, 116.5, text_layer('¡EQUIPO DXN!', fH, fill=GOLD, stroke=10), 700)
a = 116.5
add(a + 0.2, T, text_layer('EQUIPO DXN', fH, fill=GOLD, stroke=8), 170); add(a + 0.8, T, text_layer('Pasito a pasito, bonito, bonito', fP, pill=DARK), 360)
add(a + 2.0, T, text_layer('#PasitoAPasitoDXN', fM, pill=RED), 1590)
add(a + 2.8, T, text_layer('Este producto no es un medicamento.\nEl consumo de este producto es responsabilidad\nde quien lo recomienda y de quien lo usa.', fT, pill=(0, 0, 0, 160), pad=(24, 10)), 1730)
add(0.4, a, text_layer('Imágenes creadas con IA', fT, pill=(0, 0, 0, 120), pad=(18, 8)), 1866)
# karaoke lines
lines = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 5 or w['text'][-1] in '.?!' or (len(cur) >= 3 and w['text'][-1] == ','):
        lines.append(cur); cur = []
if cur: lines.append(cur)
spans = []
for i, ln in enumerate(lines):
    s = ln[0]['start'] - 0.15; e = ln[-1]['end'] + 0.35
    if i + 1 < len(lines): e = min(e if lines[i + 1][0]['start'] - ln[-1]['end'] > 0.8 else lines[i + 1][0]['start'] - 0.15, lines[i + 1][0]['start'] - 0.15)
    spans.append((s, e, ln))
fC = font('Inter-ExtraBold.otf', 66)
def karaoke(fr, t):
    for s, e, ln in spans:
        if not (s <= t < e) or s < 3.5 and False: continue
        if t >= 116.5: return
        d = ImageDraw.Draw(fr); ws = [w['text'].upper() for w in ln]; wd = [d.textlength(x + ' ', font=fC) for x in ws]
        while sum(wd) > W - 60 and len(wd) > 0: break
        k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2; y = 1680 + 30 * (1 - k)
        for w, txt, ww in zip(ln, ws, wd):
            sung = t >= w['start']; col = (255, 214, 10) if sung else (255, 255, 255)
            dy = -10 * clamp(1 - (t - w['start']) / 0.2) if sung and t - w['start'] < 0.2 else 0
            d.text((x, y + dy), txt, font=fC, fill=col, stroke_width=7, stroke_fill=(0, 0, 0)); x += ww
def frame_at(t):
    fr = base(t)
    for a, _, n, _, _ in SEG[1:]:
        if a <= t < a + 0.08: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.5 * (1 - (t - a) / 0.08))
    return fr
def compose(t):
    fr = frame_at(t)
    effects(fr, t)
    for i, (s, e, ly, y) in enumerate(L): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    karaoke(fr, t)
    if t < 116.5: fr.alpha_composite(lb, (W - 170, 40))
    return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(min(hi, T) * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
