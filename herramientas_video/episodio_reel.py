"""Educational reel 'El café oscuro NO tiene más cafeína' for Dulce Café: AI illustrations with slow camera moves,
narration-synced captions and a hook headline. Ends where the logo sting takes over.

Usage: reel.py <dir with img*.png> <fonts dir> <logo png>   → raw RGB frames on stdout.
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D, FD, LOGO_P = sys.argv[1:4]
W, H, FPS = 1080, 1920, 30
GOLD = (232, 186, 98)
CREAM = (252, 243, 228)
DARK = (40, 22, 12)
END = 46.1

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def load(name):
    im = Image.open(f"{D}/{name}").convert("RGB")
    sc = max(W / im.width, H / im.height) * 1.12          # room for the camera move
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)

IMGS = {k: load(f"img{k}.png") for k in range(8)}
# (start, end, image, move) — move: zoom in/out and pan direction
SHOTS = [(0.0, 5.66, 0, (1.0, 1.08, 0, -1)), (5.66, 12.2, 1, (1.0, 1.1, 0, 1)), (12.2, 19.98, 2, (1.0, 1.1, 1, 0)),
         (19.98, 28.33, 3, (1.08, 1.0, -1, 0)), (28.33, 34.09, 4, (1.0, 1.08, 0, 1)), (34.09, 36.45, 5, (1.0, 1.06, 0, 0)),
         (36.45, 42.85, 6, (1.0, 1.08, 1, 0)), (42.85, END, 7, (1.0, 1.08, 0, 0))]
XF = 0.35  # crossfade

def shot_frame(img, move, u):
    z0, z1, px, py = move
    z = z0 + (z1 - z0) * ease(u)
    # visible box in image pixels
    vw, vh = img.width / 1.12 / z, img.height / 1.12 / z
    mx, my = (img.width - vw) / 2, (img.height - vh) / 2
    cx = img.width / 2 + px * mx * (ease(u) - 0.5) * 0.9
    cy = img.height / 2 + py * my * (ease(u) - 0.5) * 0.9
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    return img.crop(tuple(int(v) for v in box)).resize((W, H), Image.BILINEAR)

def background(t):
    cur = None
    for i, (a, b, name, mv) in enumerate(SHOTS):
        if a <= t < b + (XF if i < len(SHOTS) - 1 else 0):
            fr = shot_frame(IMGS[name], mv, (t - a) / (b - a + XF))
            if cur is None:
                cur = fr
            else:
                k = ease((t - a) / XF)
                cur = Image.blend(cur, fr, k)
    return cur

# grade: warm tint + vignette + bottom gradient for captions
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1 - 0.55 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2), 0.35, 1)
GRAD = np.clip((yy - 1180) / 500, 0, 1) * 0.72 + np.clip((420 - yy) / 420, 0, 1) * 0.45
SHADE = (VIG * (1 - GRAD))[..., None]
WARM = np.array([1.04, 1.0, 0.94], np.float32)

def grade(im):
    a = np.asarray(im, np.float32) * WARM * SHADE
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")

def F(name, size, w=None):
    f = ImageFont.truetype(f"{FD}/{name}", size)
    if w: f.set_variation_by_axes([w])
    return f
HOOK1 = F("LilitaOne-Regular.ttf", 92)
HOOK2 = F("Anton-Regular.ttf", 150)
STICK = F("Oswald.ttf", 46, 600)
CAP = F("LilitaOne-Regular.ttf", 74)

# narration segments (from the pauses in Set's take) and the words to highlight
SEGS = [(0.00, 2.66, "¿Crees que el café oscuro tiene más cafeína?"), (3.23, 5.30, "Es uno de los mitos más famosos."),
        (5.66, 8.05, "La cafeína casi no se pierde al tostar…"),
        (8.28, 12.20, "así que un grano oscuro y uno claro tienen prácticamente la misma."),
        (12.20, 14.09, "Lo que cambia es el sabor:"),
        (14.44, 19.48, "el tostado oscuro sabe más amargo y ahumado… y por eso se siente “más fuerte”."),
        (19.98, 23.45, "El tostado claro, en cambio, conserva el sabor propio del grano:"),
        (23.87, 26.68, "más aroma, notas dulces y frutales…"), (26.88, 27.89, "el sabor de su origen."),
        (28.33, 29.97, "¿Y de qué depende la cafeína?"), (30.32, 31.05, "De la variedad:"),
        (31.41, 33.88, "el robusta tiene casi el doble que el arábica…"), (34.09, 36.08, "y de cuánto café pones en tu taza."),
        (36.45, 39.30, "Nuestro café es arábica de altura, de tostado claro:"),
        (39.30, 42.85, "para que en cada taza sientas el sabor de la montaña."),
        (43.21, 45.63, "¿Y tú… lo prefieres claro u oscuro?")]
KEYS = {"oscuro", "cafeína", "mitos", "misma", "sabor", "amargo", "ahumado", "claro", "aroma", "dulces", "frutales",
        "origen", "variedad", "robusta", "doble", "arábica", "cuánto", "altura", "montaña"}

def chunks(text):
    words = text.split()
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or (w[-1] in ",:." and len(cur) >= 2):
            out.append(cur); cur = []
    if cur:
        if out and len(cur) == 1: out[-1] += cur
        else: out.append(cur)
    return out

CAPS = []  # (start, end, [(word, t_word)])
for a, b, text in SEGS:
    cs = chunks(text)
    total = sum(len(" ".join(c)) for c in cs)
    x = a
    for c in cs:
        d = (b - a) * len(" ".join(c)) / total
        n = len(" ".join(c)); acc = 0; wt = []
        for w in c:
            wt.append((w, x + d * acc / n)); acc += len(w) + 1
        CAPS.append((x, x + d, wt)); x += d

def draw_caption(cv, t):
    for i, (a, b, wt) in enumerate(CAPS):
        nxt = CAPS[i + 1][0] if i + 1 < len(CAPS) else b + 0.4
        if not (a <= t < min(nxt, b + 0.5)): continue
        d = ImageDraw.Draw(cv)
        ws = [w for w, _ in wt]
        widths = [d.textlength(w, font=CAP) for w in ws]
        gap = 20
        lines, cur, cw = [], [], 0
        for k, w in enumerate(widths):
            if cur and cw + gap + w > 940:
                lines.append(cur); cur, cw = [], 0
            cur.append(k); cw += (gap if cw else 0) + w
        lines.append(cur)
        y = 1500 - (len(lines) - 1) * 46
        for ln in lines:
            lw = sum(widths[k] for k in ln) + gap * (len(ln) - 1)
            x = (W - lw) / 2
            for k in ln:
                w, tw = wt[k]
                if t >= tw:
                    u = ease((t - tw) / 0.12)
                    key = w.strip("¿?¡!.,:…").lower() in KEYS
                    col = GOLD if key else CREAM
                    lift = int(10 * (1 - u))
                    d.text((x, y + lift), w, font=CAP, fill=col + (int(255 * u),), stroke_width=6, stroke_fill=(20, 10, 4, int(230 * u)))
                x += widths[k] + gap
            y += 92
        break

def sticker(text, font, angle):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t_, r, b = d0.textbbox((0, 0), text, font=font)
    im = Image.new("RGBA", (r - l + 70, b - t_ + 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=22, fill=CREAM + (255,))
    d.text((35 - l, 22 - t_), text, font=font, fill=DARK)
    return im.rotate(angle, resample=Image.BICUBIC, expand=True)
STICKER = sticker("más cafeína… es un mito", STICK, 3)

def hook(cv, t):
    """Opening headline in the style of the series cover."""
    if t > 5.5: return
    k = ease(t / 0.25) * (1 - ease((t - 5.1) / 0.4))
    d = ImageDraw.Draw(cv)
    a1 = int(255 * k)
    d.text((W / 2, 300), "El café oscuro", font=HOOK1, fill=CREAM + (a1,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a1))
    u = 1 + 0.25 * (1 - ease((t - 0.15) / 0.3))
    f2 = F("Anton-Regular.ttf", int(150 * u))
    d.text((W / 2, 440), "NO TIENE", font=f2, fill=GOLD + (a1,), anchor="mm", stroke_width=6, stroke_fill=(20, 10, 4, a1))
    if t > 0.7:
        s = STICKER.copy()
        v = ease((t - 0.7) / 0.25) * k
        s.putalpha(s.getchannel("A").point(lambda p: int(p * v)))
        cv.alpha_composite(s, (int((W - s.width) / 2), 560))

LOGO = Image.open(LOGO_P).convert("RGBA").resize((150, 150), Image.LANCZOS)
LOGO.putalpha(LOGO.getchannel("A").point(lambda p: int(p * 0.9)))

TAGS = [(31.4, 34.1, "ROBUSTA ≈ 2× CAFEÍNA"), (36.5, 42.8, "ARÁBICA · TOSTADO CLARO")]
def pin(cv, t):
    """Fact tags shown while Set says them."""
    for a, b, text in TAGS:
        if not (a <= t < b): continue
        k = ease((t - a) / 0.3) * (1 - ease((t - (b - 0.3)) / 0.3))
        s = sticker(text, F("Anton-Regular.ttf", 84), -3)
        s.putalpha(s.getchannel("A").point(lambda p: int(p * k)))
        cv.alpha_composite(s, (int((W - s.width) / 2), int(360 - 30 * (1 - k))))

def frame(t):
    cv = grade(background(t))
    hook(cv, t)
    pin(cv, t)
    if t > 5.3:
        cv.alpha_composite(LOGO, (W - 190, 70))
    draw_caption(cv, t)
    out = cv.convert("RGB")
    if t < 0.25:
        out = Image.blend(Image.new("RGB", (W, H)), out, ease(t / 0.25))
    return out

if __name__ == "__main__":
    o = sys.stdout.buffer
    for n in range(int(END * FPS)):
        o.write(frame(n / FPS).tobytes())
