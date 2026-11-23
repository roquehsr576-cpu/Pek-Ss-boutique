"""Animated dialogue reel: the moka pot and the cup from Dulce Café's viral post.

Usage: anim.py <dir>   (dir holds cup.png, moka.png, logo.png, aud/set.mp3, aud/kate.mp3)
Writes <dir>/voices.wav and streams raw RGB frames to stdout.
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = sys.argv[1]
W, H, FPS, SR = 1080, 1920, 30, 44100
BG = (248, 196, 149)
RED = (206, 28, 36)
INK = (70, 45, 35)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


CLIPS = {"K1": (load(f"{D}/v1.mp3"), 1.5, "Mmm… ¡qué rico cafecito!"),
         "S2": (load(f"{D}/v2.mp3"), 6.0, "¿Y eso qué es, mijita?"),
         "K3": (load(f"{D}/v3.mp3"), 8.6, "…¿Té?"),
         "S4": (load(f"{D}/v4.mp3"), 11.0, "Aquí se toma café de altura, mija.")}
T, TEXT = {}, {}
for k, (x, st, txt) in CLIPS.items():
    T[k] = (st, st + len(x) / SR); TEXT[k] = txt
END = T["S4"][1] + 3.6
tracks = {"S": np.zeros(int(END * SR) + SR, np.float32), "K": np.zeros(int(END * SR) + SR, np.float32)}
for k, (x, st, _) in CLIPS.items():
    i = int(st * SR); tracks[k[0]][i:i + len(x)] += x
mix = tracks["S"] + tracks["K"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", f"{D}/voices.wav"],
               input=mix.astype(np.float32).tobytes(), check=True)
def envelope(x):
    hop = SR // FPS
    n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    e = e / (np.percentile(e[e > 1e-4], 95) + 1e-6)
    out = np.zeros_like(e); acc = 0
    for i, v in enumerate(np.clip(e, 0, 1)):  # fast attack, soft release
        acc = v if v > acc else acc * 0.8 + v * 0.2
        out[i] = acc
    return out
ENV = {"S": envelope(tracks["S"]), "K": envelope(tracks["K"])}

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def window(t, a, b, ramp=0.35):
    """0 → 1 → 0 across [a, b] with soft edges."""
    return ease((t - a) / ramp) * (1 - ease((t - (b - ramp)) / ramp))

# ---------- assets ----------
CUP = Image.open(f"{D}/cup.png").convert("RGBA")
MOKA = Image.open(f"{D}/moka.png").convert("RGBA")
CUP = CUP.resize((int(CUP.width * 1.45), int(CUP.height * 1.45)), Image.LANCZOS)
MOKA = MOKA.resize((int(MOKA.width * 1.4), int(MOKA.height * 1.4)), Image.LANCZOS)
LOGO = Image.open(f"{D}/logo_hd.png").convert("RGBA")
GROUND = 1460
LOGO_TOP = LOGO.resize((290, 290), Image.LANCZOS)
CUP_AT, MOKA_AT = (285, GROUND), (800, GROUND)

def place(canvas, img, anchor, dx=0, dy=0, rot=0, sx=1, sy=1):
    """Paste img with its bottom-centre at anchor, after scale and rotation about that point.
    Returns a function that maps image-local points to canvas points."""
    w, h = max(1, int(img.width * sx)), max(1, int(img.height * sy))
    im = img.resize((w, h), Image.BILINEAR) if (sx, sy) != (1, 1) else img
    pad = Image.new("RGBA", (2 * max(w, h), 2 * max(w, h)), (0, 0, 0, 0))
    cx, cy = pad.width // 2, pad.height // 2
    pad.alpha_composite(im, (cx - w // 2, cy - h))
    pad = pad.rotate(rot, resample=Image.BICUBIC, center=(cx, cy))
    ax, ay = anchor[0] + dx, anchor[1] + dy
    canvas.alpha_composite(pad, (int(ax - cx), int(ay - cy)))
    r = math.radians(-rot)
    def to_canvas(px, py):  # px,py as fractions of the original image
        x, y = (px - 0.5) * w, (py - 1) * h
        return (ax + x * math.cos(r) - y * math.sin(r), ay + x * math.sin(r) + y * math.cos(r))
    return to_canvas

def heart(d, cx, cy, s, fill):
    pts = [(cx + s * 16 * math.sin(a) ** 3 / 16,
            cy - s * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16)
           for a in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(pts, fill=fill)

def wrap(text, font, maxw, d):
    lines, cur = [], ""
    for w_ in text.split():
        t_ = (cur + " " + w_).strip()
        if d.textlength(t_, font=font) <= maxw: cur = t_
        else: lines.append(cur); cur = w_
    return lines + [cur]

BUBBLE_FONT = ImageFont.truetype(SERIF, 52)
def bubble(canvas, text, tail_x, t_in, t):
    d0 = ImageDraw.Draw(canvas)
    lines = wrap(text, BUBBLE_FONT, 820, d0)
    lh = 66; bw = 900; bh = len(lines) * lh + 70
    im = Image.new("RGBA", (bw + 20, bh + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tx = min(max(tail_x - (W - bw) // 2, 120), bw - 120)
    d.polygon([(tx - 40, bh - 8), (tx + 40, bh - 8), (tx + 10, bh + 80)], fill=(255, 255, 255, 255), outline=INK)
    d.rounded_rectangle([4, 4, bw, bh], radius=60, fill=(255, 255, 255, 255), outline=INK, width=5)
    d.polygon([(tx - 34, bh - 12), (tx + 34, bh - 12), (tx + 10, bh + 70)], fill=(255, 255, 255, 255))
    for i, l in enumerate(lines):
        d.text(((bw - d.textlength(l, font=BUBBLE_FONT)) / 2 + 4, 36 + i * lh), l, font=BUBBLE_FONT, fill=RED)
    u = ease((t - t_in) / 0.18)
    s = 0.85 + 0.15 * u
    im = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
    im.putalpha(Image.eval(im.getchannel("A"), lambda a: int(a * u)))
    top = 330 + (bh + 90) * (1 - s) / 2
    canvas.alpha_composite(im, (int((W - im.width) / 2), int(top)))


TITLE_FONT = ImageFont.truetype(SERIF, 96)
MOODS = [(0.0, (255, 214, 150), (246, 168, 118)), (T["S2"][0] - 0.3, (240, 200, 160), (214, 150, 100)),
         (T["K3"][0], (224, 204, 214), (190, 164, 186)), (T["S4"][0], (240, 192, 132), (206, 140, 88)),
         (END - 3.2, (78, 48, 32), (34, 20, 14))]
def mood(t):
    for (t0, a0, b0), (t1, a1, b1) in zip(MOODS, MOODS[1:]):
        if t < t1:
            u = ease((t - (t1 - 0.9)) / 0.9)
            return [tuple(x + (y - x) * u for x, y in zip(p, q)) for p, q in ((a0, a1), (b0, b1))]
    return [MOODS[-1][1], MOODS[-1][2]]

YF = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
rng = np.random.default_rng(3)
GLOW = Image.new("L", (900, 900), 0)
gd = ImageDraw.Draw(GLOW)
for r in range(450, 0, -6):
    gd.ellipse([450 - r, 450 - r, 450 + r, 450 + r], fill=int(70 * (1 - r / 450) ** 1.6))
def bean_sprite(sz):
    b = Image.new("RGBA", (sz, int(sz * 1.4)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.ellipse([2, 2, sz - 2, int(sz * 1.4) - 2], fill=(74, 42, 24, 255))
    bd.line([(sz / 2 + sz * 0.08 * math.sin(i / 10 * 2 * math.pi), 6 + (sz * 1.4 - 12) * i / 10) for i in range(11)],
            fill=(30, 16, 10, 255), width=max(2, sz // 9))
    return b
BEANS = []
for i in range(16):
    sz = int(rng.uniform(26, 70))
    spr = bean_sprite(sz)
    BEANS.append(dict(rot=[spr.rotate(a, resample=Image.BICUBIC, expand=True) for a in range(0, 360, 15)],
                      x=rng.uniform(0, W), y=rng.uniform(0, H), v=rng.uniform(30, 70) * sz / 50,
                      spin=rng.uniform(-40, 40), ph=rng.uniform(0, 6.3), a=rng.uniform(0.18, 0.35)))
BOKEH = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), r=rng.uniform(20, 70), v=rng.uniform(10, 30), ph=rng.uniform(0, 6.3))
         for _ in range(18)]

def background(t):
    top, bot = mood(t)
    top, bot = np.array(top, np.float32), np.array(bot, np.float32)
    g = (top * (1 - YF) + bot * YF).repeat(W, 1)
    cv = Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert("RGBA")
    # slow drifting light
    gx, gy = W / 2 + 260 * math.sin(t * 0.35), 700 + 200 * math.cos(t * 0.27)
    light = Image.new("RGBA", GLOW.size, (255, 246, 220, 0)); light.putalpha(GLOW)
    cv.alpha_composite(light, (int(gx - 450), int(gy - 450)))
    d = ImageDraw.Draw(cv)
    for b in BOKEH:
        y = (b["y"] - b["v"] * t) % (H + 200) - 100
        x = b["x"] + 30 * math.sin(t * 0.6 + b["ph"])
        d.ellipse([x - b["r"], y - b["r"], x + b["r"], y + b["r"]], fill=(255, 250, 235, 34))
    for b in BEANS:
        y = (b["y"] - b["v"] * t) % (H + 200) - 100
        x = b["x"] + 40 * math.sin(t * 0.5 + b["ph"])
        spr = b["rot"][int((b["spin"] * t + b["ph"] * 57) // 15) % 24]
        if b["a"] < 1:
            spr = spr.copy(); spr.putalpha(Image.eval(spr.getchannel("A"), lambda v, k=b["a"]: int(v * k)))
        cv.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))
    return cv, tuple(int(c * 0.7) for c in bot)

SMALL_FONT = ImageFont.truetype(SERIF, 44)
POV_FONT = ImageFont.truetype(SERIF, 62)
CUP = Image.open(f"{D}/taza.png").convert("RGBA")
CUP = CUP.resize((int(CUP.width * 1.45), int(CUP.height * 1.45)), Image.LANCZOS)
AB = Image.open(f"{D}/abuelita.png").convert("RGBA")
AB = AB.resize((int(AB.width * 1.4), int(AB.height * 1.4)), Image.LANCZOS)
JAR = Image.open(f"{D}/frasco.png").convert("RGBA")
JAR = JAR.resize((int(JAR.width * 1.5), int(JAR.height * 1.5)), Image.LANCZOS)
LOGO = Image.open(f"{D}/logo_hd.png").convert("RGBA")
GROUND = 1460
LOGO_TOP = LOGO.resize((290, 290), Image.LANCZOS)
CUP_AT, MOKA_AT = (290, GROUND), (850, GROUND)
def place(canvas, img, anchor, dx=0, dy=0, rot=0, sx=1, sy=1):
    """Paste img with its bottom-centre at anchor, after scale and rotation about that point.
    Returns a function that maps image-local points to canvas points."""
    w, h = max(1, int(img.width * sx)), max(1, int(img.height * sy))
    im = img.resize((w, h), Image.BILINEAR) if (sx, sy) != (1, 1) else img
    pad = Image.new("RGBA", (2 * max(w, h), 2 * max(w, h)), (0, 0, 0, 0))
    cx, cy = pad.width // 2, pad.height // 2
    pad.alpha_composite(im, (cx - w // 2, cy - h))
    pad = pad.rotate(rot, resample=Image.BICUBIC, center=(cx, cy))
    ax, ay = anchor[0] + dx, anchor[1] + dy
    canvas.alpha_composite(pad, (int(ax - cx), int(ay - cy)))
    r = math.radians(-rot)
    def to_canvas(px, py):  # px,py as fractions of the original image
        x, y = (px - 0.5) * w, (py - 1) * h
        return (ax + x * math.cos(r) - y * math.sin(r), ay + x * math.sin(r) + y * math.cos(r))
    return to_canvas

def heart(d, cx, cy, s, fill):
    pts = [(cx + s * 16 * math.sin(a) ** 3 / 16,
            cy - s * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16)
           for a in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(pts, fill=fill)

def wrap(text, font, maxw, d):
    lines, cur = [], ""
    for w_ in text.split():
        t_ = (cur + " " + w_).strip()
        if d.textlength(t_, font=font) <= maxw: cur = t_
        else: lines.append(cur); cur = w_
    return lines + [cur]

BUBBLE_FONT = ImageFont.truetype(SERIF, 52)
def bubble(canvas, text, tail_x, t_in, t):
    d0 = ImageDraw.Draw(canvas)
    lines = wrap(text, BUBBLE_FONT, 820, d0)
    lh = 66; bw = 900; bh = len(lines) * lh + 70
    im = Image.new("RGBA", (bw + 20, bh + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tx = min(max(tail_x - (W - bw) // 2, 120), bw - 120)
    d.polygon([(tx - 40, bh - 8), (tx + 40, bh - 8), (tx + 10, bh + 80)], fill=(255, 255, 255, 255), outline=INK)
    d.rounded_rectangle([4, 4, bw, bh], radius=60, fill=(255, 255, 255, 255), outline=INK, width=5)
    d.polygon([(tx - 34, bh - 12), (tx + 34, bh - 12), (tx + 10, bh + 70)], fill=(255, 255, 255, 255))
    for i, l in enumerate(lines):
        d.text(((bw - d.textlength(l, font=BUBBLE_FONT)) / 2 + 4, 36 + i * lh), l, font=BUBBLE_FONT, fill=RED)
    u = ease((t - t_in) / 0.18)
    s = 0.85 + 0.15 * u
    im = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
    im.putalpha(Image.eval(im.getchannel("A"), lambda a: int(a * u)))
    top = 330 + (bh + 90) * (1 - s) / 2
    canvas.alpha_composite(im, (int((W - im.width) / 2), int(top)))


def pov(cv):
    d = ImageDraw.Draw(cv)
    lines = ["POV: tu abuelita te ve", "tomando café soluble"]
    y = 1560
    for l in lines:
        w = d.textlength(l, font=POV_FONT)
        d.text(((W - w) / 2, y), l, font=POV_FONT, fill=(255, 255, 255), stroke_width=7, stroke_fill=(70, 40, 25))
        y += 82

def frame(t):
    n = min(int(t * FPS), len(ENV["S"]) - 1)
    es, ek = ENV["S"][n], ENV["K"][n]
    cv, shade = background(t)
    d = ImageDraw.Draw(cv)
    cv.alpha_composite(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 30))
    # abuelita enters
    s2a, s2b = T["S2"]; k3a, k3b = T["K3"]; s4a, s4b = T["S4"]
    m = dict(dx=0, dy=0, rot=0, sx=1, sy=1)
    ent = ease((t - (s2a - 1.1)) / 0.9)
    m["dx"] += 700 * (1 - ent); m["dy"] -= 40 * abs(math.sin(t * 9)) * (1 - ent) * (ent > 0)
    # stern lean forward while asking
    stern = window(t, s2a - 0.2, k3b + 0.2)
    m["rot"] += 6 * stern; m["dx"] -= 10 * stern
    pour = window(t, s4a + 0.4, s4b + 0.9, 0.6)
    m["dx"] -= 120 * pour; m["dy"] -= 260 * pour; m["rot"] += 35 * pour
    # cup
    c = dict(dx=0, dy=0, rot=0, sx=1, sy=1)
    happy = window(t, T["K1"][0] - 0.1, T["K1"][1] + 0.2)
    c["rot"] -= 4 * happy * math.sin(t * 3)
    caught = window(t, s2a, k3b + 0.6)
    c["sy"] -= 0.07 * caught; c["sx"] += 0.03 * caught; c["dx"] -= 20 * caught
    joy = window(t, s4b - 0.4, END - 3.0)
    c["dy"] -= 50 * joy * abs(math.sin(t * 5))
    for o, e, ph in ((m, es, 0), (c, ek, 1.7)):
        o["dy"] -= 22 * e
        o["sy"] *= 1 + 0.05 * e + 0.012 * math.sin(t * 2.4 + ph)
        o["sx"] *= 1 - 0.02 * e
        o["rot"] += 2.5 * e * math.sin(t * 11 + ph)
    for (x, _), o, w_, on in ((CUP_AT, c, 360, 1), (MOKA_AT, m, 300, ent > 0.02)):
        if not on: continue
        k = max(0.4, 1 - abs(o["dy"]) / 250)
        d.ellipse([x + o["dx"] - w_ * k / 2, GROUND - 18, x + o["dx"] + w_ * k / 2, GROUND + 22], fill=shade + (255,))
    # jar: in hand, then hidden behind the cup, then gone
    hide = ease((t - (k3a - 0.5)) / 0.5)
    jar_on = t < s4a + 0.5
    cup_w, cup_h = CUP.width, CUP.height
    def jar_pos():
        hx, hy = CUP_AT[0] + c["dx"] + cup_w * 0.43, CUP_AT[1] + c["dy"] - cup_h * 0.52
        bx, by = CUP_AT[0] + c["dx"] - cup_w * 0.05, CUP_AT[1] - cup_h * 0.55
        return hx + (bx - hx) * hide, hy + (by - hy) * hide
    if jar_on and hide > 0.5:
        jx, jy = jar_pos(); cv.alpha_composite(JAR, (int(jx - JAR.width / 2), int(jy - JAR.height / 2)))
    cup_pt = place(cv, CUP, CUP_AT, **c)
    if jar_on and hide <= 0.5:
        jx, jy = jar_pos()
        jr = JAR.rotate(-8 * math.sin(t * 3) * happy, resample=Image.BICUBIC, expand=True)
        cv.alpha_composite(jr, (int(jx - jr.width / 2), int(jy - jr.height / 2)))
    moka_pt = place(cv, AB, MOKA_AT, **m) if ent > 0.02 else None
    d = ImageDraw.Draw(cv)
    # sweat drop on the cup when caught
    if caught > 0.3 and t < k3b + 0.6:
        sx_, sy_ = cup_pt(0.82, 0.25)
        dy = 30 * ((t * 1.2) % 1)
        a = int(255 * caught)
        d.ellipse([sx_ - 16, sy_ + dy - 10, sx_ + 16, sy_ + dy + 26], fill=(150, 205, 245, a), outline=(60, 90, 140, a), width=4)
        d.polygon([(sx_ - 14, sy_ + dy + 2), (sx_ + 14, sy_ + dy + 2), (sx_, sy_ + dy - 30)], fill=(150, 205, 245, a))
    # stern "!" over the abuelita
    if moka_pt and s2a - 0.1 < t < s2b + 0.4:
        u = ease((t - s2a + 0.1) / 0.2)
        x0, y0 = moka_pt(0.85, -0.08)
        f = ImageFont.truetype(SERIF, int(120 * (0.7 + 0.3 * u)))
        d.text((x0, y0 - 60), "!", font=f, fill=RED + (int(255 * u),), stroke_width=4, stroke_fill=(255, 255, 255, int(255 * u)))
    # coffee stream
    if moka_pt and pour > 0.85:
        sx_, sy_ = moka_pt(0.08, 0.27)
        ex, ey = cup_pt(0.5, 0.1)
        pts = [(sx_ + (ex - sx_) * (i / 20) + 10 * math.sin(t * 20 + i / 20 * 6) * (i / 20), sy_ + (ey - sy_) * (i / 20) ** 2) for i in range(21)]
        d.line(pts, fill=(92, 52, 30, 255), width=16, joint="curve")
    # happy hearts after the real coffee
    sa, sb = s4b - 0.6, END - 3.0
    if sa < t < sb:
        mx, my = cup_pt(0.5, 0.05)
        for i in range(5):
            if t - sa < i * 0.45: continue
            age = (t - sa - i * 0.45) % 2.2
            a = int(220 * (1 - age / 2.2) * window(t, sa, sb, 0.3))
            heart(d, mx + 45 * math.sin(age * 3 + i), my - 70 - age * 130, 34 + 10 * age, (255, 255, 255, a) if i % 2 else (236, 90, 110, a))
    for key, (a, b) in T.items():
        if a - 0.1 <= t < b + 0.35:
            tail = int((moka_pt(0.45, 0.0) if key[0] == "S" else cup_pt(0.5, 0.0))[0])
            bubble(cv, TEXT[key], tail, a - 0.1, t)
            break
    endu = ease((t - (END - 3.2)) / 0.6)
    if endu < 1:
        pov(cv)
    if endu > 0:
        ov = Image.new("RGBA", (W, H), (40, 24, 16, int(215 * endu)))
        cv.alpha_composite(ov)
        sz = int(560 * (0.85 + 0.15 * endu))
        lg = LOGO.resize((sz, sz), Image.LANCZOS)
        lg.putalpha(Image.eval(lg.getchannel("A"), lambda a: int(a * endu)))
        cv.alpha_composite(lg, ((W - sz) // 2, 500))
        d = ImageDraw.Draw(cv)
        for i, (txt, f, col) in enumerate([("Las abuelitas saben", ImageFont.truetype(SERIF, 80), (250, 214, 150)), ("Café de altura · Tanetze de Zaragoza", SMALL_FONT, (230, 190, 150))]):
            y = 1130 + [0, 140][i]
            d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=col + (int(255 * endu),))
    return cv.convert("RGB")

out = sys.stdout.buffer
for i in range(int(END * FPS)):
    out.write(frame(i / FPS).tobytes())
print(f"{END:.2f}", file=sys.stderr)
