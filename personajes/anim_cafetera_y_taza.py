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

SET, KATE = load(f"{D}/aud/set.mp3"), load(f"{D}/aud/kate.mp3")
SET9 = load(f"{D}/aud/set9.mp3")  # re-recorded closing line: an open question
# segments of each take, split on the long pauses
SEG = {"S1": (SET, 0.0, 2.95), "S3": (SET, 4.57, 6.98), "S5": (SET, 7.89, 9.20), "S6": (SET, 10.02, 13.41),
       "S8": (SET, 14.57, 17.14), "S9": (SET9, 0.0, 3.1),
       "K2": (KATE, 0.0, 4.03), "K4": (KATE, 5.07, 9.87), "K7": (KATE, 10.90, 13.33), "K8": (KATE, 14.31, 17.17)}
TEXT = {"S1": "Buenos días, querida taza. ¿Cómo amaneciste?",
        "K2": "Un poco cansada… hay días en que cuesta empezar.",
        "S3": "Permíteme servirte un café recién hecho.",
        "K4": "Mmm… este aroma me eleva. Tu café me aviva el espíritu.",
        "S6": "¿Sabes? Sin ti… yo solo preparo el café.",
        "K7": "Y yo sin ti… estaría vacía.",
        "S8": "Porque el mejor café… es el que se comparte.",
        "S9": "Y tú… ¿con quién te tomas tu primera taza?"}

# dialogue order, with the pause that precedes each line
ORDER = [("S1", 1.3), ("K2", 0.35), ("S3", 0.35), ("K4", 1.6), ("S5", 0.15), ("S6", 0.5), ("K7", 0.3),
         ("S8", 0.45), ("S9", 1.3)]
T = {}
t = 0.0
for key, gap in ORDER:
    t += gap
    _, a, b = SEG[key]
    T[key] = (t, t + (b - a))
    if key == "S8":  # both say it together
        _, ka, kb = SEG["K8"]
        T["K8"] = (t, t + (kb - ka))
        t = max(t + (b - a), t + (kb - ka))
    else:
        t += b - a
END = t + 3.2

tracks = {"S": np.zeros(int(END * SR) + SR, np.float32), "K": np.zeros(int(END * SR) + SR, np.float32)}
for key, (start, stop) in T.items():
    src, a, b = SEG[key]
    clip = src[int(a * SR):int(b * SR)].copy()
    fade = min(len(clip) // 4, int(0.03 * SR))
    clip[:fade] *= np.linspace(0, 1, fade); clip[-fade:] *= np.linspace(1, 0, fade)
    i = int(start * SR)
    tracks[key[0]][i:i + len(clip)] += clip
mix = np.stack([tracks["S"], tracks["K"]], 1).sum(1)
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

# ---------- living background: colours follow the mood of each scene ----------
MOODS = [  # (time, top colour, bottom colour)
    (0.0, (255, 214, 150), (246, 168, 118)),            # sunrise greeting
    (T["K2"][0], (216, 198, 214), (186, 164, 190)),     # sleepy, muted
    (T["S3"][0], (240, 192, 132), (206, 140, 88)),      # caramel pour
    (T["K4"][0] + 0.8, (252, 204, 212), (234, 146, 168)),  # rosy aroma
    (T["S6"][0], (255, 218, 146), (232, 158, 82)),      # golden message
    (T["S9"][0], (244, 196, 146), (204, 132, 82)),
    (END - 3.0, (78, 48, 32), (34, 20, 14)),            # dark coffee close
]
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

def frame(t):
    n = min(int(t * FPS), len(ENV["S"]) - 1)
    es, ek = ENV["S"][n], ENV["K"][n]
    cv, shade = background(t)
    d = ImageDraw.Draw(cv)
    cv.alpha_composite(LOGO_TOP, ((W - LOGO_TOP.width) // 2, 30))

    # --- moka pot ---
    m = dict(dx=0, dy=0, rot=0, sx=1, sy=1)
    enter = ease(t / 1.2)
    m["dx"] += 650 * (1 - enter); m["dy"] -= 40 * abs(math.sin(t * 9)) * (1 - enter)
    s3a, s3b = T["S3"]
    pour = window(t, s3a + 0.8, s3b + 1.5, 0.6)
    m["dx"] += 20 * pour; m["dy"] -= 260 * pour; m["rot"] += 35 * pour
    # --- cup ---
    c = dict(dx=0, dy=0, rot=0, sx=1, sy=1)
    k2a, k2b = T["K2"]
    tired = window(t, k2a - 0.2, k2b + 0.3)
    c["sy"] -= 0.06 * tired; c["sx"] += 0.03 * tired; c["rot"] += 4 * tired
    k4a, k4b = T["K4"]
    lift = window(t, k4a + 0.6, T["S5"][1] + 0.3, 0.5)
    c["dy"] -= 60 * lift
    s8a, s8b = T["S8"]
    together = window(t, s8a - 0.3, T["S9"][0] + 0.4)
    c["dx"] += 30 * together; c["rot"] -= 6 * together
    m["dx"] -= 30 * together; m["rot"] += 6 * together
    clink_t = s8b + 0.25
    clink = math.exp(-max(0, t - clink_t) * 6) if t >= clink_t else 0
    c["dy"] -= 40 * clink; m["dy"] -= 40 * clink
    # talking and breathing
    for o, e, ph in ((m, es, 0), (c, ek, 1.7)):
        o["dy"] -= 22 * e
        o["sy"] *= 1 + 0.05 * e + 0.012 * math.sin(t * 2.4 + ph)
        o["sx"] *= 1 - 0.02 * e
        o["rot"] += 2.5 * e * math.sin(t * 11 + ph)

    # shadows stay on the ground
    for (x, _), o, w_ in ((CUP_AT, c, 360), (MOKA_AT, m, 300)):
        k = max(0.4, 1 - abs(o["dy"]) / 250)
        d.ellipse([x + o["dx"] - w_ * k / 2, GROUND - 18, x + o["dx"] + w_ * k / 2, GROUND + 22], fill=shade + (255,))

    cup_pt = place(cv, CUP, CUP_AT, **c)
    moka_pt = place(cv, MOKA, MOKA_AT, **m)
    d = ImageDraw.Draw(cv)

    # coffee stream while the pot is tipped
    if pour > 0.85:
        sx_, sy_ = moka_pt(0.03, 0.22)
        ex, ey = cup_pt(0.5, 0.1)
        pts = []
        for i in range(21):
            u = i / 20
            x = sx_ + (ex - sx_) * u + 10 * math.sin(t * 20 + u * 6) * u
            y = sy_ + (ey - sy_) * u * u + (ey - sy_) * 0.0
            pts.append((x, y))
        d.line(pts, fill=(92, 52, 30, 255), width=16, joint="curve")
    # heart-shaped steam while the cup is enjoying the aroma
    sa, sb = T["K4"][0] - 0.2, T["S6"][0] + 0.5
    if sa < t < sb:
        mx, my = cup_pt(0.5, 0.05)
        for i in range(5):
            age = (t - sa - i * 0.55) % 2.75
            if t - sa < i * 0.55: continue
            a = int(220 * (1 - age / 2.75) * window(t, sa, sb, 0.4))
            heart(d, mx + 45 * math.sin(age * 3 + i), my - 70 - age * 130, 34 + 10 * age, (255, 255, 255, a) if i % 2 else (236, 90, 110, a))
    # "¡Uuulalá!" in the style of the original post
    s5a, s5b = T["S5"]
    if s5a - 0.1 < t < s5b + 1.2:
        u = ease((t - s5a + 0.1) / 0.25)
        f = ImageFont.truetype(SERIF, int(110 * (0.6 + 0.4 * u)))
        lay = Image.new("RGBA", (900, 220), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((20, 40), "¡UUULALÁ!", font=f, fill=RED + (int(255 * u),))
        lay = lay.rotate(-8, resample=Image.BICUBIC, expand=True)
        cv.alpha_composite(lay, ((W - lay.width) // 2 + 20, 520))
    # "¡clin!" sparkle
    if clink_t < t < clink_t + 1.0:
        u = ease((t - clink_t) / 0.2) * (1 - ease((t - clink_t - 0.6) / 0.4))
        x0, y0 = W / 2 + 10, 860
        for k in range(8):
            ang = k * math.pi / 4
            r1, r2 = 50 + 60 * (t - clink_t), 100 + 80 * (t - clink_t)
            d.line([(x0 + r1 * math.cos(ang), y0 + r1 * math.sin(ang)), (x0 + r2 * math.cos(ang), y0 + r2 * math.sin(ang))],
                   fill=(255, 230, 120, int(255 * u)), width=8)
        f = ImageFont.truetype(SERIF, 70)
        d.text((x0 - d.textlength("¡clin!", font=f) / 2, y0 - 160), "¡clin!", font=f, fill=RED + (int(255 * u),))

    # dialogue bubbles (also work as subtitles with the sound off)
    for key, (a, b) in T.items():
        if key in TEXT and a - 0.1 <= t < b + 0.35:
            if key == "S8":
                tail = W // 2
            elif key[0] == "S":
                tail = int(moka_pt(0.4, 0.0)[0])
            else:
                tail = int(cup_pt(0.5, 0.0)[0])
            bubble(cv, TEXT[key], tail, a - 0.1, t)
            break

    # closing card
    s9a, _ = T["S9"]
    endu = ease((t - (END - 3.0)) / 0.6)
    if endu > 0:
        ov = Image.new("RGBA", (W, H), (40, 24, 16, int(200 * endu)))
        cv.alpha_composite(ov)
        sz = int(560 * (0.85 + 0.15 * endu))
        lg = LOGO.resize((sz, sz), Image.LANCZOS)
        lg.putalpha(Image.eval(lg.getchannel("A"), lambda a: int(a * endu)))
        cv.alpha_composite(lg, ((W - sz) // 2, 500))
        d = ImageDraw.Draw(cv)
        for i, (txt, f, col) in enumerate([("El mejor café", TITLE_FONT, (250, 214, 150)), ("es el que se comparte", SMALL_FONT, (255, 240, 225)),
                                            ("Café de altura · Tanetze de Zaragoza", SMALL_FONT, (230, 190, 150))]):
            y = 1130 + [0, 120, 200][i]
            d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=col + (int(255 * endu),))
    return cv.convert("RGB")

out = sys.stdout.buffer
for i in range(int(END * FPS)):
    out.write(frame(i / FPS).tobytes())
print(f"{END:.2f}", file=sys.stderr)
