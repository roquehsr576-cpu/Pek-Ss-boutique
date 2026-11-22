import sys, subprocess, math, json
from collections import deque
import numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; B = R + 'pizarra/'; FD = R + 'fonts_dl/'
words = [w for w in json.load(open(B + 'words_hacha.json'))['words'] if w.get('type') == 'word']
T = math.ceil(words[-1]['end'] + 3.5)
def at(txt, after=0.0):
    for w in words:
        if w['start'] >= after and w['text'].lower().strip('¿?¡!.,:') == txt: return w['start']
    raise SystemExit('no ' + txt)
def KB(sz): return ImageFont.truetype(FD + 'fontsource-kalam-5.3.0/files/kalam-latin-700-normal.woff', sz)
def KR(sz): return ImageFont.truetype(FD + 'fontsource-kalam-5.3.0/files/kalam-latin-400-normal.woff', sz)
WHITE = (238, 238, 230); YEL = (255, 222, 90)
# pizarron negro carbon
rng = np.random.default_rng(3)
n = np.asarray(Image.fromarray(np.clip(rng.normal(0, 1, (H // 4, W // 4)) * 6 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3)), np.float32)
yy, xx = np.mgrid[0:H, 0:W]; vig = 1 - 0.4 * (((xx - W / 2) / (W / 1.3)) ** 2 + ((yy - H / 2) / (H / 1.3)) ** 2)
base = np.zeros((H, W, 3), np.float32); base[:] = (30, 32, 34); base *= (1 + 0.22 * (n - 128)[..., None] / 128) * vig[..., None]
sm = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sm)
for _ in range(12):
    x, y = rng.integers(0, W), rng.integers(0, H); d.ellipse((x - 240, y - 70, x + 240, y + 70), fill=int(rng.integers(8, 20)))
base += np.asarray(sm.filter(ImageFilter.GaussianBlur(45)), np.float32)[..., None] * 0.5
BOARD = np.clip(base, 0, 255)
def bfs_rank(mask, step=2, left=False):
    h, w = mask.shape; s = mask[::step, ::step]; hh, ww = s.shape
    rank = np.full((hh, ww), np.inf); seen = np.zeros_like(s, bool); k = 0
    pts = np.argwhere(s); pts = pts[np.lexsort((pts[:, 0], pts[:, 1]))] if left else pts[np.lexsort((pts[:, 1], pts[:, 0]))]
    for sy, sx in pts:
        if seen[sy, sx]: continue
        q = deque([(sy, sx)]); seen[sy, sx] = True
        while q:
            y, x = q.popleft(); rank[y, x] = k; k += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < hh and 0 <= nx < ww and s[ny, nx] and not seen[ny, nx]: seen[ny, nx] = True; q.append((ny, nx))
    full = np.repeat(np.repeat(rank, step, 0), step, 1)[:h, :w]; full[~mask] = np.inf
    return full / max(1, k)
def img_item(path, size, cx, cy):
    im = Image.open(path).convert('L'); r = size / max(im.size); im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS).point(lambda v: 0 if v < 70 else v)
    a = np.asarray(im, np.float32) / 255; return dict(a=a, r=bfs_rank(a > 0.3), x=int(cx - a.shape[1] / 2), y=int(cy - a.shape[0] / 2), col=WHITE)
def txt_item(txt, f, cx, y, col=WHITE):
    lines = txt.split('\n'); dd = ImageDraw.Draw(Image.new('L', (1, 1))); tw = int(max(dd.textlength(l, font=f) for l in lines)) + 24; th = int(f.size * 1.35 * len(lines)) + 10
    im = Image.new('L', (tw, th), 0); di = ImageDraw.Draw(im)
    for i, l in enumerate(lines): di.text(((tw - dd.textlength(l, font=f)) / 2, i * f.size * 1.35), l, font=f, fill=255)
    a = np.asarray(im, np.float32) / 255; xs = np.tile(np.arange(tw), (th, 1)) / tw; ys = np.repeat(np.arange(th)[:, None], tw, 1) // int(f.size * 1.35)
    r = np.where(a > 0.3, (ys + xs) / len(lines), np.inf)
    return dict(a=a, r=r, x=int(cx - tw / 2), y=y, col=col)
def line_item(x0, y0, length, col=YEL, vertical=False):
    if vertical:
        a = np.zeros((length, 30), np.float32)
        for y in range(length): xv = int(15 + 3 * math.sin(y / 30)); a[y, xv - 5:xv + 5] = 1
        a[length - 60:, :] = 0
        for i in range(60): a[length - 60 + i, max(0, 15 - (60 - i) // 2):15 + (60 - i) // 2] = 0; a[length - 60 + i, max(0, 15 - i // 2 - 2):15 - i // 2 + 3] = 1; a[length - 60 + i, 15 + i // 2 - 3:min(30, 15 + i // 2 + 2)] = 1
        r = np.where(a > 0, np.repeat(np.arange(length)[:, None], 30, 1) / length, np.inf)
    else:
        a = np.zeros((26, length), np.float32)
        for x in range(length): yv = int(13 + 5 * math.sin(x / 45)); a[yv - 5:yv + 5, x] = 1
        r = np.where(a > 0, np.tile(np.arange(length), (26, 1)) / length, np.inf)
    return dict(a=a, r=r, x=int(x0), y=int(y0), col=col)
# --- escenas: (inicio, fin, [(t0, t1, item)]) ---
S = []
def scene(a, b, items): S.append((a, b, items))
tS2 = at('el'); tS3 = at('hasta'); tS4 = at('al'); tS5 = at('no', at('esfuerzo')); tS6 = at('y', at('filo')); f1 = at('uno'); f2 = at('dos'); f3 = at('tres'); f4 = at('cuatro'); f5 = at('cinco', f4); tS12 = at('mi')
scene(0, tS2 - 0.1, [(0.2, 3.6, img_item(B + 'd1.png', 980, W / 2, 960)), (3.7, 4.7, txt_item('¿POR QUÉ?', KB(150), W / 2, 230, YEL))])
scene(tS2 - 0.1, tS3 - 0.1, [(at('primer') - 0.1, at('cinco') + 0.2, txt_item('DÍA 1:  35 árboles', KB(110), W / 2, 420)),
                             (at('luego') - 0.1, at('treinta', at('luego')) + 0.4, txt_item('DÍA 2:  30', KB(110), W / 2, 620)),
                             (at('luego', at('treinta', at('luego'))) - 0.1, at('menos', 9) + 0.4, txt_item('DÍA 3:  menos...', KB(110), W / 2, 820)),
                             (at('llegaba') - 0.1, at('almuerzo') + 0.3, txt_item('+ horas\nsin almuerzo', KR(90), W / 2, 1080)),
                             (at('aun') - 0.2, at('llegaba', at('aun')) + 0.3, line_item(W - 70, 400, 860, YEL, True))])
scene(tS3 - 0.1, tS4 - 0.1, [(tS3, at('cuándo'), img_item(B + 'd3.png', 980, W / 2, 1050)), (at('cuándo'), at('hacha') + 0.2, txt_item('¿Cuándo afilaste\ntu hacha?', KB(110), W / 2, 230, YEL))])
scene(tS4 - 0.1, tS5 - 0.1, [(tS4, at('afilarla') + 0.1, img_item(B + 'lenador.png', 760, W / 2, 560)), (at('afilarla') + 0.1, at('terminó'), txt_item('10 MIN', KB(120), W / 2 + 330, 150, YEL)),
                             (at('terminó'), at('esfuerzo') + 0.6, img_item(B + 'd5.png', 760, W / 2, 1380))])
scene(tS5 - 0.1, tS6 - 0.1, [(tS5, at('esfuerzo', tS5) + 0.4, txt_item('NO LE FALTABA\nESFUERZO.', KB(130), W / 2, 560)), (at('le', at('esfuerzo', tS5)) - 0.1, at('filo') + 0.4, txt_item('LE FALTABA\nFILO.', KB(170), W / 2, 960, YEL)),
                             (at('filo') + 0.4, at('filo') + 0.9, line_item(W / 2 - 300, 1400, 600))])
scene(tS6 - 0.1, f1 - 0.1, [(tS6, at('tuya'), txt_item('¿Cómo afilas\nla tuya?', KR(110), W / 2, 420)), (at('aquí') - 0.1, at('formas') + 0.5, txt_item('5 FORMAS DE\nAFILAR TU HACHA', KB(130), W / 2, 900, YEL))])
FORMS = [(f1, f2, 'icon2', '10 MIN AL DÍA', 'de aprender algo de lo tuyo', 'libro'), (f2, f3, 'icon1', 'PREGUNTA A QUIEN\nYA LO LOGRÓ', 'hazlo como lo hacen los grandes', 'hazlo'),
         (f3, f4, 'icon3', 'SI NO FUNCIONA,\nNO LO REPITAS IGUAL', 'cambia la información', 'resultados'), (f4, f5, 'icon4', 'DESCANSA', 'hasta la mejor hacha se desgasta', 'hasta'),
         (f5, tS12, 'icon5', 'RODÉATE DE GENTE\nQUE TE AFILE', 'un buen equipo te hace mejor', 'un')]
for i, (a, b, ic, t1, t2, w2) in enumerate(FORMS):
    scene(a - 0.1, b - 0.1, [(a, a + 0.6, txt_item(str(i + 1), KB(260), W / 2, 180, YEL)), (a + 0.4, a + 2.0, img_item(B + ic + '.png', 520, W / 2, 760)),
                             (a + 1.9, a + 3.4, txt_item(t1, KB(100), W / 2, 1100)), (at(w2, a) - 0.1, min(b - 0.3, at(w2, a) + 1.6), txt_item(t2, KR(70), W / 2, 1400, YEL))])
scene(tS12 - 0.1, T, [(tS12, at('lectura') + 0.3, img_item(B + 'd7.png', 760, W / 2, 900)), (at('mi') + 0.1, at('hacha', tS12) + 0.4, txt_item('Mi momento de\nafilar el hacha', KR(90), W / 2, 220)),
                      (at('cuál') - 0.1, at('hoy') + 0.3, txt_item('¿CUÁL VAS A\nEMPEZAR HOY?', KB(110), W / 2, 1220, YEL)),
                      (at('mándale') - 0.1, at('filo', at('mándale')) + 0.3, txt_item('Mándale este video a quien\ncorta con el hacha sin filo', KR(64), W / 2, 1560))])
hand = chroma_cut(B + 'mano.png'); hand = hand.resize((int(hand.width * 0.62), int(hand.height * 0.62)), Image.LANCZOS)
ha = np.asarray(hand.split()[-1]); tip = np.argwhere(ha[:, : hand.width // 3] > 128); TIPY, TIPX = tip[tip[:, 1].argmin()]
logo = Image.open(R + 'clip/dxn-logo.png').convert('RGBA').resize((150, 145), Image.LANCZOS)
lb = Image.new('RGBA', (180, 175)); m = Image.new('L', (180, 175), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 179, 174), 26, fill=240); lb.paste((255, 255, 255, 255), (0, 0), m); lb.alpha_composite(logo, (15, 15))
grains = {}
def scene_at(t):
    for i, (a, b, it) in enumerate(S):
        if a <= t < b: return i
    return len(S) - 1
_h = [W + 200.0, H + 300.0]
REST = (W - 120, H - 260)
def compose(t):
    si = scene_at(t); a, b, items = S[si]; arr = BOARD.copy(); active = None
    fade = clamp((b - t) / 0.25) if si < len(S) - 1 else 1.0
    for t0, t1, it in items:
        if t < t0: continue
        p = clamp((t - t0) / (t1 - t0)); A, Rk = it['a'], it['r']; vis = A * (Rk <= p)
        key = id(it)
        if key not in grains: grains[key] = 0.75 + 0.25 * np.random.default_rng(len(grains)).random(A.shape)
        h, w = vis.shape; x0, y0 = it['x'], it['y']; X0, Y0 = max(0, x0), max(0, y0); X1, Y1 = min(W, x0 + w), min(H, y0 + h)
        if X1 <= X0 or Y1 <= Y0: continue
        sub = (vis * grains[key])[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None] * fade
        sl = arr[Y0:Y1, X0:X1]; sl[:] = sl * (1 - sub) + np.array(it['col'], np.float32) * sub
        if p < 1:
            m_ = (Rk <= p) & (Rk > p - 0.015); pts = np.argwhere(m_)
            if len(pts): yy_, xx_ = pts[len(pts) // 2]; active = (x0 + xx_, y0 + yy_)
    fr = Image.fromarray(arr.astype(np.uint8)).convert('RGBA')
    tgt = active if active else REST; k = 0.45 if active else 0.12
    _h[0] += (tgt[0] - _h[0]) * k; _h[1] += (tgt[1] - _h[1]) * k
    if t > T - 1.2: _h[0] += (W + 500 - _h[0]) * 0.15; _h[1] += (H + 500 - _h[1]) * 0.15
    fr.alpha_composite(hand, (int(_h[0] - TIPX), int(_h[1] - TIPY + 4 * math.sin(t * 23))))
    if t >= T - 3.0:
        kk = entrance(t, T - 3.0, 0.6); place(fr, lb, W / 2, 1810, 0.45 + 0.3 * kk, 0, clamp(kk * 1.4))
    return fr
if sys.argv[1] == 'info': print('T', T, [(round(a, 1), round(b, 1)) for a, b, _ in S]); sys.exit()
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = []
    for tt in ts:
        for k in range(int(tt * FPS) - 8, int(tt * FPS)): compose(k / FPS)
        ims.append(compose(tt).convert('RGB').resize((216, 384)))
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n_ in range(max(0, int(round(lo * FPS)) - 20), int(round(lo * FPS))): compose(n_ / FPS)
for n_ in range(int(round(lo * FPS)), int(round(min(hi, T) * FPS))): p.stdin.write(compose(n_ / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
