import sys, subprocess, math, random
from collections import deque
import numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; B = R + 'pizarra/'
FD = R + 'fonts_dl/'
fK = ImageFont.truetype(FD + 'fontsource-kalam-5.3.0/files/kalam-latin-700-normal.woff', 120)
fK2 = ImageFont.truetype(FD + 'fontsource-kalam-5.3.0/files/kalam-latin-400-normal.woff', 66)
T = 13.0
# --- pizarron ---
rng = np.random.default_rng(3)
n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
board = Image.fromarray(np.clip(n * 6 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
base = np.zeros((H, W, 3), np.float32); base[:] = (34, 46, 40)
bn = (np.asarray(board, np.float32) - 128) / 128
yy, xx = np.mgrid[0:H, 0:W]; vig = 1 - 0.45 * (((xx - W / 2) / (W / 1.3)) ** 2 + ((yy - H / 2) / (H / 1.3)) ** 2)
base = base * (1 + 0.25 * bn[..., None]) * vig[..., None]
# manchas de gis borrado
sm = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sm)
for _ in range(14):
    x, y = rng.integers(0, W), rng.integers(0, H); d.ellipse((x - 220, y - 60, x + 220, y + 60), fill=int(rng.integers(10, 28)))
sm = np.asarray(sm.filter(ImageFilter.GaussianBlur(40)), np.float32)
base = base + sm[..., None] * 0.6
BOARD = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
# --- trazos: orden de revelado por recorrido (BFS) ---
def order_mask(mask, start='top', step=2):
    """mask: np.bool (h,w). Devuelve rank (float, inf=no trazo) usando BFS sobre una version reducida."""
    h, w = mask.shape; sm_ = mask[::step, ::step]; hh, ww = sm_.shape
    rank = np.full((hh, ww), np.inf); seen = np.zeros_like(sm_, bool); k = 0
    pts = np.argwhere(sm_)
    if start == 'left': pts = pts[np.lexsort((pts[:, 0], pts[:, 1]))]
    else: pts = pts[np.lexsort((pts[:, 1], pts[:, 0]))]
    for sy, sx in pts:
        if seen[sy, sx]: continue
        q = deque([(sy, sx)]); seen[sy, sx] = True
        while q:
            y, x = q.popleft(); rank[y, x] = k; k += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < hh and 0 <= nx < ww and sm_[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
    full = np.repeat(np.repeat(rank, step, 0), step, 1)[:h, :w]
    full[~mask] = np.inf
    return full / max(1, k)
def layer_from(img_l, x0, y0):
    """img_l: L image of chalk lines -> (alpha np, rank np, offset)."""
    a = np.asarray(img_l, np.float32) / 255
    return a
# dibujo del leñador
dib = Image.open(B + 'lenador.png').convert('L').resize((980, 980), Image.LANCZOS)
dib = dib.point(lambda v: 0 if v < 70 else v)
DA = np.asarray(dib, np.float32) / 255; DR = order_mask(DA > 0.3)
DX, DY = (W - 980) // 2, 470
def text_mask(txt, f):
    tw = int(ImageDraw.Draw(Image.new('L', (1, 1))).textlength(txt, font=f)) + 20; th = int(f.size * 1.5)
    im = Image.new('L', (tw, th), 0); ImageDraw.Draw(im).text((10, 0), txt, font=f, fill=255)
    a = np.asarray(im, np.float32) / 255; r = order_mask(a > 0.3, 'left', 1)
    # suavizar orden de izquierda a derecha para que parezca escritura
    xs = np.tile(np.arange(a.shape[1]), (a.shape[0], 1)) / a.shape[1]
    r = np.where(np.isfinite(r), 0.85 * xs + 0.15 * r, np.inf)
    return a, r
TA, TR = text_mask('AFILA TU HACHA', fK); TX, TY = (W - TA.shape[1]) // 2, 210
SA, SR = text_mask('El éxito ama la preparación', fK2); SX, SY = (W - SA.shape[1]) // 2, 1520
UL = np.zeros((24, TA.shape[1] - 60), np.float32)
for x in range(UL.shape[1]): yv = int(12 + 5 * math.sin(x / 40)); UL[max(0, yv - 4):yv + 4, x] = 1
ULR = np.where(UL > 0, np.tile(np.arange(UL.shape[1]), (UL.shape[0], 1)) / UL.shape[1], np.inf); ULX, ULY = TX + 30, TY + 175
# segmentos de dibujo: (inicio, fin, alpha, rank, x, y)
PARTS = [(0.6, 6.6, DA, DR, DX, DY), (6.8, 9.0, TA, TR, TX, TY), (9.2, 11.0, SA, SR, SX, SY), (11.1, 11.6, UL, ULR, ULX, ULY)]
hand = chroma_cut(B + 'mano.png'); hand = hand.resize((int(hand.width * 0.62), int(hand.height * 0.62)), Image.LANCZOS)
ha = np.asarray(hand.split()[-1]); tip = np.argwhere(ha[:, : hand.width // 3] > 128)
TIPY, TIPX = tip[tip[:, 1].argmin()]  # punta del gis = pixel mas a la izquierda
CH = (240, 240, 232)
def tip_pos(t):
    for a, b, A, Rk, x0, y0 in PARTS:
        if a <= t < b:
            p = (t - a) / (b - a); m = (Rk <= p) & (Rk > p - 0.012)
            pts = np.argwhere(m)
            if len(pts): yy_, xx_ = pts[len(pts) // 2]; return x0 + xx_, y0 + yy_, True
            return None
    return None
_last = [W + 300, H + 400]
def compose(t):
    arr = np.asarray(BOARD).astype(np.float32).copy()
    for a, b, A, Rk, x0, y0 in PARTS:
        if t < a: continue
        p = clamp((t - a) / (b - a)); vis = A * (Rk <= p)
        h, w = vis.shape; sl = arr[y0:y0 + h, x0:x0 + w, :3]
        grain = 0.75 + 0.25 * np.random.default_rng(int(x0 + y0)).random((h, w))
        al = (vis * grain)[..., None]; sl[:] = sl * (1 - al) + np.array(CH) * al
    fr = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    tp = tip_pos(t)
    if tp:
        tx, ty, _ = tp; _last[0] += (tx - _last[0]) * 0.5; _last[1] += (ty - _last[1]) * 0.5
    else:
        if t < 0.6: _last[0], _last[1] = W + 300 - (W + 300 - DX - 300) * ease_out_cubic(t / 0.6), H + 300 - (H + 300 - DY) * ease_out_cubic(t / 0.6)
        elif t > 11.6: k = ease_in_cubic(clamp((t - 11.6) / 0.8)); _last[0] += (W + 400 - _last[0]) * k; _last[1] += (H + 400 - _last[1]) * k
    wob = 4 * math.sin(t * 23)
    fr.alpha_composite(hand, (int(_last[0] - TIPX), int(_last[1] - TIPY + wob)))
    return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = []
    for tt in ts:
        for k in range(int(tt * FPS) - 5, int(tt * FPS)): compose(k / FPS)
        ims.append(compose(tt).convert('RGB').resize((216, 384)))
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
out = sys.argv[1]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
drawing = []
for n in range(int(T * FPS)):
    t = n / FPS; p.stdin.write(compose(t).convert('RGB').tobytes()); drawing.append(1 if tip_pos(t) else 0)
p.stdin.close(); p.wait(); open(out + '.act', 'w').write(''.join(map(str, drawing))); print('ok')
