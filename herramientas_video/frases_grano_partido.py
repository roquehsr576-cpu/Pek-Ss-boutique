"""Beat-synced kinetic-typography reel built from Dulce Café's "La vida es como una taza de café" post.

Usage: kinetic.py <post image> <logo png> <fonts dir>   → raw RGB frames on stdout.
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

POST, LOGO_P, FD = sys.argv[1:4]
W, H, FPS = 1080, 1920, 30
BEAT = 0.6269                       # music section starts on a beat
CREAM = (255, 244, 228)
GOLD = (247, 190, 62)
DARK = (48, 26, 14)

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def back_out(u):
    u = min(1, max(0, u)); c = 2.2
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

def pulse(t):
    return math.exp(-((t % BEAT) / 0.12))

# ---------- background built from the post itself ----------
post = Image.open(POST).convert("RGB")

def without_text(im):
    """Paint over the light lettering (and the logo) with the surrounding wood, so the blurred
    background shows no ghost text."""
    a = np.asarray(im, np.float32)
    mx, mn = a.max(-1), a.min(-1)
    m = (mx > 170) & (mx - mn < 70)
    m[120:380, 580:910] = True                     # logo badge
    mimg = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
    keep = 1 - np.asarray(mimg, np.float32)[..., None] / 255
    fill = a.copy()
    for r in (8, 24, 60):                          # normalised blur pulls colour in from the edges
        num = np.asarray(Image.fromarray((fill * keep).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32)
        den = np.asarray(Image.fromarray((keep[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32)[..., None] / 255
        est = num / np.maximum(den, 1e-3)
        fill = fill * keep + est * (1 - keep)
    return Image.fromarray(fill.clip(0, 255).astype(np.uint8))

clean = without_text(post)
cover = clean.resize((int(post.width * H / post.height), H), Image.LANCZOS)
blur = cover.filter(ImageFilter.GaussianBlur(22))
blur = Image.blend(blur, Image.new("RGB", blur.size, (20, 10, 4)), 0.42)
BG = blur.resize((int(blur.width * 1.12), int(H * 1.12)), Image.BILINEAR)

def fade_mask(w, h, sides):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = np.ones((h, w), np.float32)
    f = 0.35
    if "r" in sides: m *= np.clip((w - xx) / (w * f), 0, 1)
    if "l" in sides: m *= np.clip(xx / (w * f), 0, 1)
    if "b" in sides: m *= np.clip((h - yy) / (h * f), 0, 1)
    if "t" in sides: m *= np.clip(yy / (h * f), 0, 1)
    return Image.fromarray((m * 255).astype(np.uint8))

CORNERS = []
for box, sc, pos, sides in [((0, 0, 560, 330), 1.35, (0, 0), "rb"), ((900, 0, 1500, 330), 1.35, (W - 810, 0), "lb"),
                            ((0, 1120, 1500, 1257), 0.95, (W / 2 - 712, H - 130), "t"),
                            ((0, 880, 250, 1257), 1.4, (0, H - 528), "rt"), ((1250, 880, 1500, 1257), 1.4, (W - 350, H - 528), "lt")]:
    im = post.crop(box)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS).convert("RGBA")
    im.putalpha(fade_mask(im.width, im.height, sides))
    CORNERS.append((im, pos))

LOGO = Image.open(LOGO_P).convert("RGBA")

# ---------- text ----------
F = {
    "bold": (f"{FD}/LilitaOne-Regular.ttf", 118),
    "big": (f"{FD}/LilitaOne-Regular.ttf", 150),
    "rough": (f"{FD}/RubikDirt-Regular.ttf", 112),
    "script": (f"{FD}/GreatVibes-Regular.ttf", 150),
    "punch": (f"{FD}/Anton-Regular.ttf", 190),
}
_font_cache = {}
def font(style):
    if style not in _font_cache:
        path, size = F[style]
        _font_cache[style] = ImageFont.truetype(path, size)
    return _font_cache[style]

_sprite_cache = {}
PREFIX = {}
def sprite(word, style, key):
    """Render one word; key=True gives it a tilted gold label."""
    k = (word, style, key)
    if k in _sprite_cache: return _sprite_cache[k]
    f = font(style)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t_, r, b = tmp.textbbox((0, 0), word, font=f)
    pad = 34 if key else 18
    im = Image.new("RGBA", (r - l + pad * 2, b - t_ + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ends = [pad - l + f.getlength(word[:i]) for i in range(len(word) + 1)]
    ends[-1] = im.width
    if key:
        d.rounded_rectangle([4, 8, im.width - 4, im.height - 4], radius=28, fill=GOLD + (255,))
        d.text((pad - l, pad - t_), word, font=f, fill=DARK)
        w0 = im.width
        im = im.rotate(-3, resample=Image.BICUBIC, expand=True)
        ends = [e + (im.width - w0) / 2 for e in ends]; ends[-1] = im.width
    else:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 5, pad - t_ + 7), word, font=f, fill=(0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(4))
        im.alpha_composite(sh)
        ImageDraw.Draw(im).text((pad - l, pad - t_), word, font=f, fill=CREAM, stroke_width=3, stroke_fill=(60, 32, 16))
    ends[0] = 0
    _sprite_cache[k] = im
    PREFIX[id(im)] = ends
    return im

# Each scene: (first beat, length in beats, lines); a line is a list of (word, style, keyword?)
def L(text, style="bold", keys=()):
    return [(w, style, w.strip("¿?¡!.,…:").upper() in keys) for w in text.split()]

SCENES = [  # calm pacing: each phrase gets 7-12 beats; starts are filled in below
    (0, 0, [L("¡OYE,", "punch"), L("TÚ!", "punch", keys=("TÚ",))]),
    (0, 0, [L("Sí, tú…", "script"), L("con tu cafecito", "bold"), L("en la mano", "bold")]),
    (0, 0, [L("La vida es como", "bold"), L("UNA TAZA", "big", keys=("TAZA",)), L("DE CAFÉ", "big")]),
    (0, 0, [L("Todo está", "script"), L("en cómo la", "rough"), L("PREPARAS", "big", keys=("PREPARAS",))]),
    (0, 0, [L("pero sobre todo", "rough"), L("en cómo la", "rough"), L("TOMAS", "punch", keys=("TOMAS",))]),
    (0, 0, [L("Hay días que salen", "bold"), L("CARGADITOS…", "big", keys=("CARGADITOS",))]),
    (0, 0, [L("y otros…", "script"), L("medio amargos.", "bold")]),
    (0, 0, [L("¿Te salió", "bold"), L("amarga?", "script")]),
    (0, 0, [L("¡Ponle", "bold"), L("ACTITUD!", "punch", keys=("ACTITUD",))]),
    (0, 0, [L("Porque la actitud", "bold"), L("es como el", "rough"), L("AROMA:", "big", keys=("AROMA",))]),
    (0, 0, [L("se nota", "script"), L("desde lejos.", "bold")]),
    (0, 0, [L("Sé", "bold"), L("POSITIVO", "big", keys=("POSITIVO",))]),
    (0, 0, [L("y cosas", "bold"), L("BUENAS", "big", keys=("BUENAS",)), L("pasarán", "script")]),
    (0, 0, [L("Una taza", "script"), L("a la vez.", "script")]),
    (0, 0, [L("Y tú…", "script"), L("¿cómo cambia tu día", "bold"), L("después del", "rough"),
             L("PRIMER", "big", keys=("PRIMER",)), L("SORBO?", "big", keys=("SORBO",))]),
]
INTRO = 6
LENGTHS = [7, 9, 10, 10, 10, 9, 9, 8, 9, 10, 9, 8, 10, 9, 12]
_b = INTRO
for i, nb in enumerate(LENGTHS):
    SCENES[i] = (_b, nb, SCENES[i][2]); _b += nb
OUTRO = _b
END = (OUTRO + 11.3) * BEAT

LAYOUT = []
for b0, nb, lines in SCENES:
    rows = []
    for line in lines:
        sps = [sprite(w, s, k) for w, s, k in line]
        rows.append(sps)
    total_h = sum(max(s.height for s in r) - 10 for r in rows)
    y = 1010 - total_h / 2
    words = []
    for r in rows:
        rh = max(s.height for s in r) - 10
        rw = sum(s.width for s in r) - 8 * (len(r) - 1)
        x = (W - rw) / 2
        for s in r:
            words.append((s, x + s.width / 2, y + rh / 2))
            x += s.width - 8
        y += rh
    LAYOUT.append((b0 * BEAT, (b0 + nb) * BEAT, words))

def roasted_bean(w, h):
    """A shaded roasted coffee bean, returned as its two halves split along the crease."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx - w / 2) / (w / 2 - 4), (yy - h / 2) / (h / 2 - 4)
    r = nx ** 2 + ny ** 2
    inside = np.clip((1 - r) * 40, 0, 1)
    z = np.sqrt(np.clip(1 - r, 0, 1))
    light = np.clip(0.35 + 0.65 * (z * 0.8 - nx * 0.25 - ny * 0.35), 0, 1)
    lo, hi = np.array([26, 12, 5], np.float32), np.array([118, 64, 30], np.float32)
    rgb = lo + (hi - lo) * light[..., None]
    spec = np.exp(-(((nx + 0.38) / 0.18) ** 2 + ((ny + 0.45) / 0.3) ** 2)) * 55
    rgb += spec[..., None]
    crease_x = w / 2 + w * 0.09 * np.sin(np.pi * ny)            # S-shaped groove
    dist = np.abs(xx - crease_x)
    groove = np.exp(-(dist / (w * 0.035)) ** 2)
    rgb = rgb * (1 - 0.75 * groove[..., None]) + np.array([20, 10, 4], np.float32) * 0.75 * groove[..., None]
    rim = np.exp(-((dist - w * 0.05) / (w * 0.02)) ** 2) * 35
    rgb += rim[..., None]
    rgba = np.dstack([rgb.clip(0, 255), inside * 255]).astype(np.uint8)
    full = Image.fromarray(rgba, "RGBA")
    left = full.copy(); right = full.copy()
    lm = (xx < crease_x).astype(np.float32) * inside
    left.putalpha(Image.fromarray((lm * 255).astype(np.uint8)))
    right.putalpha(Image.fromarray(((1 - (xx < crease_x)) * inside * 255).astype(np.uint8)))
    return full, left, right, crease_x[:, 0]
BW, BH = 520, 760
BEAN_FULL, BEAN_L, BEAN_R, CREASE = roasted_bean(BW, BH)

def crack(cv, dt, k):
    """Scene entrance: a roasted bean drops in, cracks along its crease and splits open,
    its halves flying apart while ground coffee falls from the split."""
    if dt < 0 or dt > 2.4: return
    cx, cy = W / 2, 1010
    tilt = 18 if k % 2 == 0 else -18
    if dt < 0.3:                                    # drop in with a little bounce
        sc = 0.55 + 0.45 * back_out(dt / 0.3)
        im = BEAN_FULL.resize((int(BW * sc), int(BH * sc)), Image.BILINEAR).rotate(tilt, resample=Image.BICUBIC, expand=True)
        jx = 6 * math.sin(dt * 90) if dt > 0.2 else 0
        cv.alpha_composite(im, (int(cx - im.width / 2 + jx), int(cy - im.height / 2)))
        if dt > 0.2:                                # glowing crack line
            g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
            ImageDraw.Draw(g).line([(CREASE[y], y) for y in range(20, BH - 20, 10)], fill=(255, 210, 120, 255), width=10)
            g = g.filter(ImageFilter.GaussianBlur(5)).rotate(tilt, resample=Image.BICUBIC, expand=True)
            cv.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
        return
    u = ease((dt - 0.3) / 0.9)
    a = 1 - ease((dt - 0.8) / 0.5)
    if a > 0:
        for half, sgn in ((BEAN_L, -1), (BEAN_R, 1)):
            im = half.rotate(tilt + sgn * 40 * u, resample=Image.BICUBIC, expand=True)
            if a < 1:
                im.putalpha(Image.eval(im.getchannel("A"), lambda v, a=a: int(v * a)))
            cv.alpha_composite(im, (int(cx - im.width / 2 + sgn * 760 * u), int(cy - im.height / 2 + 260 * u * u)))
    # ground coffee falling out of the split
    rng_ = np.random.default_rng(100 + k)
    n = 420
    x0 = cx + rng_.normal(0, 40, n); y0 = cy + rng_.uniform(-BH / 2.4, BH / 2.4, n)
    vx = rng_.normal(0, 150, n); vy = rng_.uniform(-160, 50, n)
    sz = rng_.uniform(1.5, 6, n)
    col = rng_.integers(0, 3, n)
    pal = [(58, 30, 14), (92, 52, 26), (128, 78, 40)]
    tt = dt - 0.3
    d = ImageDraw.Draw(cv)
    fade = 1 - ease((dt - 1.6) / 0.8)
    for i in range(n):
        x = x0[i] + vx[i] * tt; y = y0[i] + vy[i] * tt + 0.5 * 700 * tt * tt
        if y > H: continue
        r_ = sz[i]
        d.ellipse([x - r_, y - r_, x + r_, y + r_], fill=pal[col[i]] + (int(235 * fade),))

def draw_scene(cv, t):
    for k, (t0, t1, words) in enumerate(LAYOUT):
        if not (t0 <= t < t1): continue
        start = t0 + 0.45
        nchar = sum(len(PREFIX[id(s)]) - 1 for s, _, _ in words)
        step = min(0.14, (t1 - start - 1.4) / max(1, nchar))
        shown = (t - start) / step
        out = ease((t - (t1 - 0.5)) / 0.5)            # gentle exit
        c = 0
        for i, (s, cx, cy) in enumerate(words):
            ends = PREFIX[id(s)]
            n = len(ends) - 1
            kk = min(n, shown - c); c += n
            if kk <= 0: break
            cut = s.width if kk >= n else int(ends[int(kk)] + (ends[int(kk) + 1] - ends[int(kk)]) * (kk % 1))
            im = s.crop((0, 0, max(1, cut), s.height))
            a = 1 - out
            if a < 1:
                im = im.copy(); im.putalpha(Image.eval(im.getchannel("A"), lambda v, a=a: int(v * a)))
            done = shown >= nchar
            bump = 14 * pulse(t) if done and i == len(words) - 1 else 0
            cv.alpha_composite(im, (int(cx - s.width / 2), int(cy - s.height / 2 - bump - 40 * out)))
        crack(cv, t - t0, k)

def background(t):
    z = 1 + 0.025 * pulse(t)
    ox = (BG.width - W) / 2 + 90 * math.sin(t * 0.25)
    oy = (BG.height - H) / 2 + 40 * math.cos(t * 0.2)
    cw, ch = W / z, H / z
    box = (ox + (W - cw) / 2, oy + (H - ch) / 2, ox + (W + cw) / 2, oy + (H + ch) / 2)
    cv = BG.crop(tuple(int(v) for v in box)).resize((W, H), Image.BILINEAR).convert("RGBA")
    for i, (im, (x, y)) in enumerate(CORNERS):
        dx = 10 * math.sin(t * 0.8 + i)
        dy = 8 * math.cos(t * 0.7 + i * 1.7)
        cv.alpha_composite(im, (int(x + dx), int(y + dy)))
    return cv

def frame(t):
    cv = background(t)
    # intro: the original post punches in, then makes room for the words
    if t < INTRO * BEAT + 0.6:
        u = back_out(t / 0.45)
        k = 1 - ease((t - INTRO * BEAT) / 0.6)
        w = int(1040 * (0.5 + 0.5 * u))
        p = post.resize((w, int(w * post.height / post.width)), Image.LANCZOS).convert("RGBA")
        p.putalpha(int(255 * k))
        cv.alpha_composite(p, ((W - p.width) // 2, (H - p.height) // 2))
    draw_scene(cv, t)
    # small logo badge stays on top once the words start
    if INTRO * BEAT <= t < OUTRO * BEAT:
        lg = LOGO.resize((230, 230), Image.LANCZOS)
        cv.alpha_composite(lg, ((W - 230) // 2, int(90 + 6 * math.sin(t * 2))))
    if t >= OUTRO * BEAT:
        u = back_out((t - OUTRO * BEAT) / 0.5)
        sz = int(560 * (0.3 + 0.7 * u) * (1 + 0.03 * pulse(t)))
        lg = LOGO.resize((sz, sz), Image.LANCZOS)
        cv.alpha_composite(lg, ((W - sz) // 2, int(560 - sz / 2 + 280)))
        d = ImageDraw.Draw(cv)
        for i, (txt, st, col) in enumerate([("Una taza. Una actitud.", "bold", CREAM),
                                             ("Café orgánico artesanal de altura", "rough", GOLD)]):
            if t < OUTRO * BEAT + 0.4 + i * 0.35: continue
            f = ImageFont.truetype(F[st][0], 70 if i == 0 else 54)
            y = 1240 + i * 110
            d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=col, stroke_width=3, stroke_fill=(50, 26, 12))
    return cv.convert("RGB")

out = sys.stdout.buffer
for n in range(int(END * FPS)):
    out.write(frame(n / FPS).tobytes())
print(f"{END:.2f}", file=sys.stderr)
