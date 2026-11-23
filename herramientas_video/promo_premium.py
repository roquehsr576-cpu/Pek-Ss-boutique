"""Premium vertical remake of the "Disfruta de un café de mucha altura" reel for Dulce Café.

Usage: promo.py <logo png> <fonts dir>   → raw RGB frames on stdout.
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

LOGO_P, FD = sys.argv[1:3]
W, H, FPS = 1080, 1920, 30
GOLD = (222, 178, 102)
CREAM = (250, 238, 220)
rng = np.random.default_rng(11)
BEAT = 0.6269   # music section starts on a beat

def pulse(t):
    return math.exp(-((t % BEAT) / 0.12))

def back_out(u):
    u = min(1, max(0, u)); c = 1.7
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def window(t, a, b, ramp=0.7):
    return ease((t - a) / ramp) * (1 - ease((t - (b - ramp)) / ramp))

# ---------- roasted beans ----------
def roasted_bean(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx - w / 2) / (w / 2 - 2), (yy - h / 2) / (h / 2 - 2)
    r = nx ** 2 + ny ** 2
    inside = np.clip((1 - r) * 30, 0, 1)
    z = np.sqrt(np.clip(1 - r, 0, 1))
    light = np.clip(0.3 + 0.7 * (z * 0.8 - nx * 0.25 - ny * 0.35), 0, 1)
    lo, hi = np.array([22, 10, 4], np.float32), np.array([112, 60, 28], np.float32)
    rgb = lo + (hi - lo) * light[..., None]
    rgb += (np.exp(-(((nx + 0.38) / 0.18) ** 2 + ((ny + 0.45) / 0.3) ** 2)) * 60)[..., None]
    cx = w / 2 + w * 0.09 * np.sin(np.pi * ny)
    groove = np.exp(-((xx - cx) / (w * 0.035)) ** 2)
    rgb = rgb * (1 - 0.8 * groove[..., None]) + 12 * groove[..., None]
    return Image.fromarray(np.dstack([rgb.clip(0, 255), inside * 255]).astype(np.uint8), "RGBA")

BASE_BEAN = roasted_bean(200, 290)
LAYERS = []  # far → near
for depth, count, size, blur, speed, dim in [(0, 22, 38, 3, 40, 0.45), (1, 14, 80, 0, 120, 0.85), (2, 6, 190, 7, 260, 1.0)]:
    for i in range(count):
        sz = int(size * rng.uniform(0.8, 1.2))
        b = BASE_BEAN.resize((sz, int(sz * 1.45)), Image.LANCZOS)
        if blur: b = b.filter(ImageFilter.GaussianBlur(blur))
        if dim < 1:
            arr = np.asarray(b, np.float32); arr[..., :3] *= dim; b = Image.fromarray(arr.astype(np.uint8), "RGBA")
        rots = [b.rotate(a, resample=Image.BICUBIC, expand=True) for a in range(0, 360, 10)]
        x0 = rng.uniform(-150, 40) if i % 2 else rng.uniform(W - 40, W + 150)
        if depth < 2: x0 = rng.uniform(-50, W + 50)
        LAYERS.append(dict(rots=rots, x=x0, y=rng.uniform(0, H + 400), v=speed * rng.uniform(0.8, 1.2),
                           spin=rng.uniform(-25, 25), ph=rng.uniform(0, 36), sway=rng.uniform(10, 40) if depth < 2 else 12, depth=depth))

# ---------- static pieces ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vign = np.clip(1 - 0.75 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2), 0.25, 1)
BASE = np.stack([28 * vign + 6, 17 * vign + 4, 11 * vign + 3], -1)
GRAIN = [rng.normal(0, 7, (H // 2, W // 2)).astype(np.float32) for _ in range(4)]
GLOW = Image.new("L", (1200, 1200), 0)
gd = ImageDraw.Draw(GLOW)
for r in range(600, 0, -8):
    gd.ellipse([600 - r, 600 - r, 600 + r, 600 + r], fill=int(90 * (1 - r / 600) ** 2))
LOGO = Image.open(LOGO_P).convert("RGBA")

def F(name, size, wght=None):
    f = ImageFont.truetype(f"{FD}/{name}", size)
    if wght: f.set_variation_by_axes([wght])
    return f
SERIF_I = F("PlayfairDisplay.ttf", 96, 500)
SERIF_B = F("PlayfairDisplay.ttf", 150, 800)
SANS = F("Oswald.ttf", 46, 400)

def spaced(d, xy, text, font, fill, track):
    """Draw centred text with extra letter spacing (tracking)."""
    ws = [d.textlength(c, font=font) for c in text]
    total = sum(ws) + track * (len(text) - 1)
    x = xy[0] - total / 2
    for c, w in zip(text, ws):
        d.text((x, xy[1]), c, font=font, fill=fill, anchor="lm"); x += w + track

def line_layer(txt, f, col, y, tr):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tr: spaced(d, (W / 2, y), txt, f, col, tr)
    else: d.text((W / 2, y), txt, font=f, fill=col, anchor="mm")
    sh = im.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.putalpha(sh.getchannel("A").point(lambda v: int(v * 0.8)))
    out.alpha_composite(im)
    box = out.getbbox()
    return out.crop(box), box[:2]

def B(n):  # beats → seconds
    return n * BEAT

# scenes: (start beat, end beat, lines, extra) — lines enter one per half beat
SC = [
    (1, 7, [("Disfruta de un café", SERIF_I, CREAM, 900, 0)], None),
    (7, 13, [("de mucha", SERIF_I, CREAM, 820, 0), ("ALTURA", SERIF_B, GOLD, 980, 18),
             ("1,280 METROS SOBRE EL NIVEL DEL MAR", SANS, CREAM, 1330, 5)], "mountains"),
    (13, 19, [("CULTIVADO A LA SOMBRA EN", SANS, GOLD, 850, 8), ("Tanetze de Zaragoza", SERIF_I, CREAM, 950, 0),
              ("OAXACA", SANS, GOLD, 1050, 14)], None),
    (19, 25, [("Para personas", SERIF_I, CREAM, 800, 0), ("que gustan del", SERIF_I, CREAM, 910, 0),
              ("BUEN CAFÉ", SERIF_B, GOLD, 1050, 10)], "line"),
    (25, 31, [("Un rico café tanetzeño", SERIF_I, CREAM, 860, 0), ("en tu desayuno", SERIF_I, CREAM, 980, 0)], "steam"),
    (31, 37, [("CONSUME", SANS, CREAM, 880, 16), ("Nacional", SERIF_B, GOLD, 1000, 0)], "flag"),
    (37, 45, [("Pide el tuyo…", SERIF_I, CREAM, 760, 0), ("y sabrás por qué", SERIF_I, CREAM, 880, 0),
              ("te decimos que es", SANS, CREAM, 990, 8), ("DE ALTURA", SERIF_B, GOLD, 1130, 12)], "mountains_low"),
]
LINES = [[line_layer(*l) for l in lines] for _, _, lines, _ in SC]
LOGO_T = B(45)
END = B(55.6)

def mountains(d, p, a):
    pts = [(80, 1260), (300, 1110), (420, 1190), (610, 1040), (780, 1170), (900, 1100), (1000, 1180)]
    L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) * p
    out = [pts[0]]
    for i in range(len(pts) - 1):
        s = math.dist(pts[i], pts[i + 1])
        if L >= s: out.append(pts[i + 1]); L -= s
        else:
            f = L / s; out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)); break
    d.line(out, fill=GOLD + (int(230 * a),), width=5, joint="curve")

def hero_logo(cv, lt, cx, cy, final):
    """Coin-style slow turn (one full revolution) while growing to `final` px, then ring and light sweep.
    The artwork itself is never redrawn: only scaled, with light passing over it."""
    spin = ease(lt / 3.0)
    ang = 2 * math.pi * spin
    sz = int(final * (0.42 + 0.58 * ease(lt / 3.0)))
    sx = abs(math.cos(ang))
    a = ease(lt / 0.6)
    # warm halo
    halo = Image.new("L", (sz * 2, sz * 2), 0)
    hd = ImageDraw.Draw(halo)
    for r in range(sz, 0, -10):
        hd.ellipse([sz - r, sz - r, sz + r, sz + r], fill=int(110 * a * (1 - r / sz) ** 2))
    glow = Image.new("RGBA", halo.size, (255, 180, 100, 0)); glow.putalpha(halo)
    cv.alpha_composite(glow, (int(cx - sz), int(cy - sz)))
    if sx > 0.015:
        w_ = max(2, int(sz * sx))
        lg = LOGO.resize((w_, sz), Image.LANCZOS)
        arr = np.asarray(lg, np.float32)
        arr[..., :3] *= 0.5 + 0.5 * sx                      # darker when seen edge-on
        arr[..., 3] *= a
        lg = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
        # light sweep once it faces front
        st = (lt - 3.4) / 0.9
        if 0 < st < 1:
            sh = Image.new("L", lg.size, 0)
            x = -sz * 0.5 + sz * 2.0 * st
            ImageDraw.Draw(sh).polygon([(x, 0), (x + sz * 0.16, 0), (x - sz * 0.24, sz), (x - sz * 0.4, sz)], fill=150)
            sh = sh.filter(ImageFilter.GaussianBlur(sz * 0.03))
            sh = Image.fromarray((np.asarray(sh, np.float32) * np.asarray(lg.getchannel("A"), np.float32) / 255).astype(np.uint8))
            white = Image.new("RGBA", lg.size, (255, 250, 235, 0)); white.putalpha(sh)
            lg.alpha_composite(white)
        cv.alpha_composite(lg, (int(cx - w_ / 2), int(cy - sz / 2)))
    # gold ring draws around it after the turn
    rp = ease((lt - 2.6) / 1.1)
    if rp > 0:
        rr = sz * 0.54
        ring = Image.new("RGBA", cv.size, (0, 0, 0, 0))
        ImageDraw.Draw(ring).arc([cx - rr, cy - rr, cx + rr, cy + rr], -90, -90 + 360 * rp, fill=GOLD + (255,), width=6)
        cv.alpha_composite(ring.filter(ImageFilter.GaussianBlur(6)))
        cv.alpha_composite(ring)

def frame(t):
    g = GRAIN[int(t * 12) % 4]
    g = np.asarray(Image.fromarray(g).resize((W, H), Image.NEAREST))
    base = BASE + g[..., None]
    cv = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    # warm moving light
    lx, ly = W / 2 + 300 * math.sin(t * 0.21), 820 + 260 * math.cos(t * 0.17)
    light = Image.new("RGBA", GLOW.size, (255, 170, 90, 0)); light.putalpha(GLOW)
    cv.alpha_composite(light, (int(lx - 600), int(ly - 600)))
    # falling beans, far to near; the near ones pass in front of the words
    def beans(depths):
        for b in LAYERS:
            if b["depth"] not in depths: continue
            y = (b["y"] + b["v"] * t) % (H + 500) - 250
            x = b["x"] + b["sway"] * math.sin(t * 0.6 + b["ph"])
            spr = b["rots"][int(b["spin"] * t / 10 + b["ph"]) % 36]
            cv.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))
    beans((0, 1))
    d = ImageDraw.Draw(cv)
    for si, ((b0, b1, _, extra), lines) in enumerate(zip(SC, LINES)):
        a, b = B(b0), B(b1)
        if not (a - 0.05 <= t < b): continue
        out = ease((t - (b - 0.32)) / 0.32)
        k = 1 - out
        for i, (im, (x0, y0)) in enumerate(lines):
            tin = a + i * BEAT / 2
            if t < tin: continue
            u = back_out((t - tin) / 0.45)
            side = -1 if (i + si) % 2 == 0 else 1
            dx = side * 420 * (1 - u)
            dy = -160 * out
            lay = im
            if out > 0:
                lay = im.copy(); lay.putalpha(lay.getchannel("A").point(lambda v, k=k: int(v * k)))
            if u < 0.98:                                # motion trail while sliding in
                for g, ga in ((0.35, 0.18), (0.18, 0.32)):
                    gh = im.copy(); gh.putalpha(gh.getchannel("A").point(lambda v, ga=ga: int(v * ga)))
                    cv.alpha_composite(gh, (int(x0 + dx + side * 420 * g * (1 - u)), int(y0 + dy)))
            cv.alpha_composite(lay, (int(x0 + dx), int(y0 + dy - 8 * pulse(t) * (i == len(lines) - 1))))
        k = min(k, ease((t - a) / 0.3))
        if extra == "mountains":
            mountains(d, ease((t - a - BEAT) / 1.6), k)
        elif extra == "line":
            w_ = 300 * ease((t - a - BEAT) / 0.9)
            d.line([(W / 2 - w_, 1150), (W / 2 + w_, 1150)], fill=GOLD + (int(220 * k),), width=4)
        elif extra == "steam":
            for i in range(3):
                pts = [(W / 2 - 60 + i * 60 + 18 * math.sin(j / 5 + t * 1.5 + i), 1330 - j * 12) for j in range(18)]
                d.line(pts, fill=(255, 245, 230, int(110 * k)), width=6, joint="curve")
        elif extra == "mountains_low":
            md = ImageDraw.Draw(cv)
            pts = [(80, 1360), (300, 1250), (420, 1310), (610, 1200), (780, 1300), (900, 1250), (1000, 1310)]
            p_ = ease((t - a - 2 * BEAT) / 1.6)
            n_ = max(2, int(len(pts) * p_))
            md.line(pts[:n_], fill=GOLD + (int(230 * k),), width=5, joint="curve")
        elif extra == "flag":
            w_ = 120 * ease((t - a - BEAT) / 0.8)
            if w_ < 8: continue
            for i, c in enumerate([(0, 104, 71), (245, 245, 240), (206, 17, 38)]):
                x0_ = W / 2 - 1.5 * w_ + i * w_
                d.rectangle([x0_, 1110, x0_ + w_ - 6, 1122], fill=c + (int(255 * k),))
    # whip transition between scenes: a golden sweep with a quick flash
    for b0, _, _, _ in SC[1:] + [(45, 0, 0, 0)]:
        dt = t - B(b0)
        if -0.18 < dt < 0.22:
            q = (dt + 0.18) / 0.4
            sweep = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sweep)
            x = -400 + (W + 800) * q
            sd.polygon([(x - 160, 0), (x + 60, 0), (x + 260, H), (x + 40, H)], fill=(255, 200, 120, 70))
            cv.alpha_composite(sweep.filter(ImageFilter.GaussianBlur(30)))
            if abs(dt) < 0.08:
                cv.alpha_composite(Image.new("RGBA", (W, H), (255, 225, 170, int(60 * (1 - abs(dt) / 0.08)))))
    beans((2,))
    # hero close: the logo turns slowly like a coin as it comes forward, then settles as the star
    if t > LOGO_T:
        lt = t - LOGO_T
        u = ease(lt / 0.8)
        cv.alpha_composite(Image.new("RGBA", (W, H), (10, 5, 2, int(170 * u))))
        hero_logo(cv, lt, W / 2, 860, 740)
        d = ImageDraw.Draw(cv)
        v = ease((lt - 3.3) / 1.0)
        if v > 0:
            spaced(d, (W / 2, 1335), "CAFÉ ORGÁNICO ARTESANAL", SANS, GOLD + (int(255 * v),), 8)
            d.text((W / 2, 1425), "de altura", font=SERIF_I, fill=CREAM + (int(255 * v),), anchor="mm")
    # fade in / out
    fi = ease(t / 0.6); fo = 1 - ease((t - (END - 1.0)) / 1.0)
    z = 1 + 0.018 * pulse(t)
    if t < LOGO_T + 1.5:
        cw, ch = int(W / z), int(H / z)
        cv = cv.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BILINEAR)
    out = cv.convert("RGB")
    if fi * fo < 1:
        out = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out, fi * fo)
    return out

o = sys.stdout.buffer
for n in range(int(END * FPS)):
    o.write(frame(n / FPS).tobytes())
