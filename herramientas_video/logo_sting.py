"""Brand logo sting for Dulce Café: the official logo is revealed untouched (only light passes over it),
with premium effects around it.

Usage: sting.py <logo png> <fonts dir> <width> <height> <seconds>   → raw RGB frames on stdout.
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

LOGO_P, FD = sys.argv[1:3]
W, H, DUR = int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
FPS = 30
GOLD = (222, 178, 102)
CREAM = (250, 238, 220)
rng = np.random.default_rng(5)

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def out_back(u):
    u = min(1, max(0, u)); c = 1.4
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

SIZE = int(min(W, H) * 0.62)
CX, CY = W / 2, H * (0.46 if H > W else 0.47)
LOGO = Image.open(LOGO_P).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS)
LOGO_A = np.asarray(LOGO.getchannel("A"), np.float32) / 255

# background: espresso vignette + film grain
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vign = np.clip(1 - 0.8 * (((xx - CX) / (W * 0.8)) ** 2 + ((yy - CY) / (H * 0.7)) ** 2), 0.2, 1)
BASE = np.stack([30 * vign + 5, 18 * vign + 4, 12 * vign + 3], -1)
GRAIN = [rng.normal(0, 6, (H // 2, W // 2)).astype(np.float32) for _ in range(4)]
GLOW = Image.new("L", (SIZE * 2, SIZE * 2), 0)
gd = ImageDraw.Draw(GLOW)
for r in range(SIZE, 0, -6):
    gd.ellipse([SIZE - r, SIZE - r, SIZE + r, SIZE + r], fill=int(120 * (1 - r / SIZE) ** 2.2))
PARTS = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), r=rng.uniform(1.5, 4.5), v=rng.uniform(15, 45),
              ph=rng.uniform(0, 6.3), a=rng.uniform(80, 200)) for _ in range(70)]
font_path = f"{FD}/Oswald.ttf"
TAG = ImageFont.truetype(font_path, int(SIZE * 0.065)); TAG.set_variation_by_axes([400])
TAG2 = ImageFont.truetype(f"{FD}/PlayfairDisplay.ttf", int(SIZE * 0.085)); TAG2.set_variation_by_axes([500])

def spaced(d, cx, y, text, font, fill, track):
    ws = [d.textlength(c, font=font) for c in text]
    x = cx - (sum(ws) + track * (len(text) - 1)) / 2
    for c, w in zip(text, ws):
        d.text((x, y), c, font=font, fill=fill, anchor="lm"); x += w + track

def frame(t):
    g = np.asarray(Image.fromarray(GRAIN[int(t * 12) % 4]).resize((W, H), Image.NEAREST))
    cv = Image.fromarray((BASE + g[..., None]).clip(0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(cv)
    # drifting gold dust
    for p in PARTS:
        y = (p["y"] - p["v"] * t) % H
        x = p["x"] + 14 * math.sin(t * 0.8 + p["ph"])
        tw = 0.5 + 0.5 * math.sin(t * 3 + p["ph"])
        d.ellipse([x - p["r"], y - p["r"], x + p["r"], y + p["r"]], fill=GOLD + (int(p["a"] * tw * ease(t / 0.8)),))
    # warm glow behind the badge
    gl = ease((t - 0.3) / 1.2)
    light = Image.new("RGBA", GLOW.size, (255, 180, 100, 0)); light.putalpha(GLOW.point(lambda v: int(v * gl)))
    cv.alpha_composite(light, (int(CX - SIZE), int(CY - SIZE)))
    # gold ring draws itself around the badge
    rr = SIZE * 0.535
    sweep = ease((t - 3.0) / 1.1)
    if sweep > 0:
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        rd.arc([CX - rr, CY - rr, CX + rr, CY + rr], -90, -90 + 360 * sweep, fill=GOLD + (255,), width=max(3, SIZE // 120))
        cv.alpha_composite(ring.filter(ImageFilter.GaussianBlur(6)))
        cv.alpha_composite(ring)
        if sweep < 1:  # spark at the drawing tip
            a = math.radians(-90 + 360 * sweep)
            sx, sy = CX + rr * math.cos(a), CY + rr * math.sin(a)
            d = ImageDraw.Draw(cv)
            for k_, rad in ((60, 18), (140, 9), (255, 4)):
                d.ellipse([sx - rad, sy - rad, sx + rad, sy + rad], fill=(255, 235, 190, k_))
    # the logo itself: one slow coin-style turn while it comes forward, never redrawn
    if t > 0.5:
        lt = t - 0.5
        spin = ease(lt / 3.0)
        sz = int(SIZE * (0.45 + 0.55 * spin) * (1 + 0.006 * math.sin(t * 1.6) * ease((lt - 3.2) / 1)))
        sx = abs(math.cos(2 * math.pi * spin))
        if sx > 0.015:
            w_ = max(2, int(sz * sx))
            lg = LOGO.resize((w_, sz), Image.LANCZOS)
            arr = np.asarray(lg, np.float32)
            arr[..., :3] *= 0.5 + 0.5 * sx
            arr[..., 3] *= ease(lt / 0.5)
            lg = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
            st = (lt - 3.3) / 0.9                     # light sweep once it faces front
            if 0 < st < 1:
                sh = Image.new("L", lg.size, 0)
                x = -sz * 0.5 + sz * 2.0 * st
                ImageDraw.Draw(sh).polygon([(x, 0), (x + sz * 0.16, 0), (x - sz * 0.24, sz), (x - sz * 0.4, sz)], fill=150)
                sh = sh.filter(ImageFilter.GaussianBlur(sz * 0.03))
                sh = Image.fromarray((np.asarray(sh, np.float32) * np.asarray(lg.getchannel("A"), np.float32) / 255).astype(np.uint8))
                white = Image.new("RGBA", lg.size, (255, 250, 235, 0)); white.putalpha(sh)
                lg.alpha_composite(white)
            cv.alpha_composite(lg, (int(CX - w_ / 2), int(CY - sz / 2)))
    # tagline
    v = ease((t - 3.8) / 0.9)
    if v > 0:
        d = ImageDraw.Draw(cv)
        y0 = CY + SIZE * 0.66
        spaced(d, CX, y0, "CAFÉ DE ALTURA", TAG, GOLD + (int(255 * v),), int(SIZE * 0.02 + 18 * (1 - v)))
        d.text((CX, y0 + SIZE * 0.13), "Tanetze de Zaragoza, Oaxaca", font=TAG2, fill=CREAM + (int(255 * v),), anchor="mm")
        lw = SIZE * 0.35 * v
        d.line([(CX - lw, y0 + SIZE * 0.065), (CX + lw, y0 + SIZE * 0.065)], fill=GOLD + (int(160 * v),), width=2)
    out = cv.convert("RGB")
    f = ease(t / 0.4) * (1 - ease((t - (DUR - 0.6)) / 0.6))
    if f < 1:
        out = Image.blend(Image.new("RGB", (W, H)), out, f)
    return out

o = sys.stdout.buffer
for n in range(int(DUR * FPS)):
    o.write(frame(n / FPS).tobytes())
