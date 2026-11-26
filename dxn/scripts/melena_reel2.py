"""Educational reel "Lo que nadie te dice de la melena de león: Ganoderma vs. melena de león" (DXN page): AI illustrations with slow
camera moves, narration-synced captions and a hook headline. No logo.

Usage: gano_reel.py <dir with img*.png> <fonts dir>   → raw RGB frames on stdout.
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D, FD = sys.argv[1:3]
W, H, FPS = 1080, 1920, 30
GOLD = (232, 186, 98)
CREAM = (252, 243, 228)
DARK = (40, 22, 12)
END = 82.6

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def load(name):
    im = Image.open(f"{D}/{name}").convert("RGB")
    sc = max(W / im.width, H / im.height) * 1.12          # room for the camera move
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)

IMGS = {k: load(f"img{k}.png") for k in range(11)}
# (start, end, image, move) — move: zoom in/out and pan direction
SHOTS = [(0.0, 7.30, 0, (1.0, 1.08, 0, 0)), (7.30, 15.40, 1, (1.0, 1.1, 0, 0)), (15.40, 27.68, 2, (1.0, 1.12, 0, 0)),
         (27.68, 35.91, 3, (1.0, 1.1, 0, 0)), (35.91, 39.31, 4, (1.12, 1.2, 0, 0)), (39.31, 44.44, 5, (1.0, 1.1, 0, 1)),
         (44.44, 53.05, 6, (1.0, 1.12, 1, 0)), (53.05, 60.92, 7, (1.0, 1.1, 0, 0)), (60.92, 68.92, 8, (1.0, 1.1, 0, 0)),
         (68.92, 76.35, 9, (1.0, 1.12, 0, -1)), (76.35, END, 10, (1.0, 1.08, 0, 0))]
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

# narration segments (from the pauses in the Faraón 3 take) and the words to highlight
SEGS = [(0.00, 1.91, "Uno parece de madera barnizada…"), (2.35, 2.86, "el otro,"), (3.09, 4.23, "una barba blanca."),
        (4.68, 6.85, "Y los dos son hongos famosos."), (7.30, 10.39, "El Ganoderma y la melena de león tienen algo en común:"),
        (10.75, 13.00, "los dos crecen en árboles de madera dura,"), (13.22, 14.69, "y ayudan a descomponerla."),
        (15.40, 16.17, "Ronda uno:"), (16.54, 17.21, "la forma."),
        (17.77, 21.71, "El Ganoderma tiene un sombrero en forma de abanico, con un tallo de lado."),
        (22.20, 25.20, "La melena de león no tiene ni sombrero ni tallo:"), (25.50, 27.00, "solo espinas que cuelgan."),
        (27.68, 28.52, "Ronda dos:"), (28.82, 29.49, "el tacto."), (30.01, 31.35, "El Ganoderma es duro,"),
        (31.65, 32.62, "casi como madera."), (33.03, 35.19, "La melena es suave y esponjosa."), (35.91, 36.73, "Antes de seguir:"),
        (37.22, 38.79, "¿tú cuál crees que se come fresco?"), (39.31, 40.45, "La melena de león."),
        (40.89, 44.03, "Cuando está joven y blanca, se cocina como cualquier hongo."),
        (44.44, 47.54, "El Ganoderma es tan duro y amargo, que no se come así:"), (47.93, 49.49, "se rebana, se seca…"),
        (49.78, 51.53, "y se hierve por mucho tiempo,"), (51.78, 52.34, "como un té."), (53.05, 53.95, "Ronda cuatro:"),
        (54.26, 54.93, "el nombre."), (55.41, 57.83, "Ganoderma significa “piel brillante”."),
        (58.26, 60.25, "Hericium significa “erizo”."), (60.92, 61.99, "Y la ronda cinco:"),
        (62.43, 66.05, "el Ganoderma suelta sus esporas por poritos debajo del sombrero."), (66.47, 67.05, "La melena…"),
        (67.38, 68.27, "por sus espinas."), (68.92, 69.66, "Un dato más:"),
        (70.02, 73.02, "en el Reino Unido, la melena de león es tan escasa,"), (73.24, 75.67, "que arrancarla está prohibido por la ley."),
        (76.35, 76.83, "¿Y tú…"), (77.13, 78.68, "cuál te llama más la atención:"), (79.11, 79.88, "el brillante…"),
        (80.28, 80.94, "o el peludo?")]
KEYS = {"barnizada", "barba", "blanca", "famosos", "común", "dura", "descomponerla", "forma", "abanico", "tallo", "espinas",
        "tacto", "duro", "madera", "suave", "esponjosa", "fresco", "joven", "cocina", "amargo", "seca", "té", "nombre",
        "brillante", "erizo", "esporas", "poritos", "reino", "unido", "escasa", "prohibido", "ley", "peludo", "ganoderma"}

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
STICKER = sticker("Lo que nadie te dice", STICK, 3)

def hook(cv, t):
    """Opening headline in the style of the series cover."""
    if t > 4.5: return
    k = ease(t / 0.25) * (1 - ease((t - 4.1) / 0.4))
    d = ImageDraw.Draw(cv)
    a1 = int(255 * k)
    d.text((W / 2, 300), "DOS HONGOS FAMOSOS…", font=HOOK1, fill=CREAM + (a1,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a1))
    u = 1 + 0.25 * (1 - ease((t - 0.15) / 0.3))
    f2 = F("Anton-Regular.ttf", int(112 * u))
    d.text((W / 2, 440), "¿CUÁL ES CUÁL?", font=f2, fill=GOLD + (a1,), anchor="mm", stroke_width=6, stroke_fill=(20, 10, 4, a1))
    if t > 0.7:
        s = STICKER.copy()
        v = ease((t - 0.7) / 0.25) * k
        s.putalpha(s.getchannel("A").point(lambda p: int(p * v)))
        cv.alpha_composite(s, (int((W - s.width) / 2), 540))

TAGS = [(4.6, 7.2, "GANODERMA  VS.  MELENA"), (10.75, 15.3, "LOS DOS: MADERA DURA"), (15.40, 27.6, "RONDA 1: ABANICO vs. POMPÓN"),
        (27.68, 35.8, "RONDA 2: DURO vs. SUAVE"), (35.91, 39.2, "¿CUÁL SE COME FRESCO?"), (39.31, 44.4, "RONDA 3: SE COCINA…"),
        (44.44, 52.9, "…O SE HIERVE COMO TÉ"), (53.05, 60.8, "RONDA 4: BRILLO vs. ERIZO"), (60.92, 68.8, "RONDA 5: POROS vs. ESPINAS"),
        (70.02, 76.2, "REINO UNIDO: ¡PROHIBIDO!")]
def pin(cv, t):
    """Fact tags shown while the narrator says them."""
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
    draw_caption(cv, t)
    out = cv.convert("RGB")
    if t < 0.25:
        out = Image.blend(Image.new("RGB", (W, H)), out, ease(t / 0.25))
    return out

if __name__ == "__main__":
    o = sys.stdout.buffer
    for n in range(int(END * FPS)):
        o.write(frame(n / FPS).tobytes())
