"""Educational reel "Lo que nadie te dice de la melena de león: no tiene sombrero" (DXN page): AI illustrations with slow
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
END = 73.5

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def load(name):
    im = Image.open(f"{D}/{name}").convert("RGB")
    sc = max(W / im.width, H / im.height) * 1.12          # room for the camera move
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)

IMGS = {k: load(f"img{k}.png") for k in range(12)}
# (start, end, image, move) — move: zoom in/out and pan direction
SHOTS = [(0.0, 5.61, 0, (1.0, 1.08, 0, -1)), (5.61, 12.07, 1, (1.0, 1.1, 1, 0)), (12.07, 17.62, 2, (1.0, 1.12, 0, 1)),
         (17.62, 24.27, 3, (1.0, 1.1, 0, 0)), (24.27, 29.66, 4, (1.08, 1.0, -1, 0)), (29.66, 33.03, 5, (1.15, 1.25, 0, 0)),
         (33.03, 38.89, 6, (1.0, 1.1, 0, -1)), (38.89, 41.59, 7, (1.0, 1.08, 0, 0)), (41.59, 50.11, 8, (1.0, 1.12, 0, 1)),
         (50.11, 58.65, 9, (1.0, 1.1, 0, -1)), (58.65, 66.27, 10, (1.0, 1.08, -1, 0)), (66.27, END, 11, (1.0, 1.08, 0, 0))]
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
SEGS = [(0.00, 1.83, "Este hongo no tiene sombrero…"), (2.32, 2.95, "ni tallo."), (3.38, 4.08, "Y aun así,"), (4.36, 5.09, "es un hongo."),
        (5.61, 9.04, "Cuando piensas en un hongo, te imaginas un sombrerito con su tallo."), (9.51, 11.66, "Este rompe todas las reglas."),
        (12.07, 14.93, "Está hecho de cientos de espinas blancas que cuelgan,"), (15.15, 17.15, "de más de un centímetro cada una."),
        (17.62, 19.04, "Por eso su nombre científico,"), (19.32, 20.74, "Hericium erinaceus,"),
        (20.96, 22.77, "viene del latín para “erizo”…"), (23.06, 23.83, "dos veces."),
        (24.27, 27.61, "Pero en México y en muchos países le decimos de otra forma:"), (28.01, 29.16, "melena de león."),
        (29.66, 30.44, "Antes de seguir:"), (30.85, 32.46, "¿tú ya habías visto un hongo así?"),
        (33.03, 35.13, "En Japón le dicen yamabushitake,"), (35.39, 36.27, "por los yamabushi:"),
        (36.60, 38.50, "monjes ermitaños de las montañas."), (38.89, 39.51, "Y en China,"), (39.80, 41.15, "“hongo cabeza de mono”."),
        (41.59, 44.85, "Crece en árboles de madera dura, como el encino o el maple,"),
        (45.16, 47.48, "casi siempre donde el tronco tiene una herida…"), (47.80, 49.63, "a finales del verano y en otoño."),
        (50.11, 51.49, "Y lo que nadie te dice:"), (51.81, 53.41, "también crece en México."),
        (53.77, 58.21, "Está registrado en los bosques de Hidalgo, en Mineral del Chico y Huasca de Ocampo."),
        (58.65, 59.18, "Eso sí:"), (59.48, 60.10, "si lo ves,"), (60.36, 62.20, "no lo arranques ni lo pruebes."),
        (62.57, 63.66, "Hay hongos parecidos,"), (63.87, 65.75, "y solo un experto los distingue."),
        (66.27, 66.69, "¿Y tú…"), (66.96, 67.83, "cómo le dirías:"), (68.17, 68.72, "erizo,"), (69.00, 69.88, "cabeza de mono…"),
        (70.16, 71.52, "o melena de león?")]
KEYS = {"sombrero", "tallo", "hongo", "reglas", "espinas", "blancas", "centímetro", "hericium", "erinaceus", "erizo",
        "méxico", "melena", "león", "visto", "japón", "yamabushitake", "yamabushi", "monjes", "china", "mono", "dura",
        "encino", "maple", "herida", "otoño", "hidalgo", "arranques", "pruebes", "experto"}

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
    d.text((W / 2, 300), "NO TIENE SOMBRERO…", font=HOOK1, fill=CREAM + (a1,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a1))
    u = 1 + 0.25 * (1 - ease((t - 0.15) / 0.3))
    f2 = F("Anton-Regular.ttf", int(112 * u))
    d.text((W / 2, 440), "¿ENTONCES QUÉ ES?", font=f2, fill=GOLD + (a1,), anchor="mm", stroke_width=6, stroke_fill=(20, 10, 4, a1))
    if t > 0.7:
        s = STICKER.copy()
        v = ease((t - 0.7) / 0.25) * k
        s.putalpha(s.getchannel("A").point(lambda p: int(p * v)))
        cv.alpha_composite(s, (int((W - s.width) / 2), 540))

TAGS = [(5.61, 11.9, "SIN SOMBRERO · SIN TALLO"), (12.07, 17.5, "ESPINAS DE +1 CM"), (19.32, 24.1, "HERICIUM = ERIZO"),
        (28.01, 29.6, "MELENA DE LEÓN"), (29.66, 32.9, "¿YA LO HABÍAS VISTO?"), (33.03, 38.8, "JAPÓN: YAMABUSHITAKE"),
        (38.89, 41.5, "CHINA: “CABEZA DE MONO”"), (45.16, 50.0, "CRECE EN HERIDAS DEL ÁRBOL"), (51.81, 58.5, "TAMBIÉN EN MÉXICO"),
        (60.36, 66.1, "NO LO ARRANQUES NI LO PRUEBES")]
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
