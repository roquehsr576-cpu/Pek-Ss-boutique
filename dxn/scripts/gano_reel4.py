"""Educational reel "Lo que nadie te dice del Ganoderma: dónde crece" (DXN page): AI illustrations with slow
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
END = 64.0

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def load(name):
    im = Image.open(f"{D}/{name}").convert("RGB")
    sc = max(W / im.width, H / im.height) * 1.12          # room for the camera move
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)

IMGS = {k: load(f"img{k}.png") for k in range(10)}
# (start, end, image, move) — move: zoom in/out and pan direction
SHOTS = [(0.0, 4.49, 0, (1.0, 1.08, 0, -1)), (4.49, 13.06, 1, (1.0, 1.12, 0, 1)), (13.06, 19.82, 2, (1.0, 1.1, 0, 0)),
         (19.82, 24.58, 3, (1.0, 1.08, 1, 0)), (24.58, 29.95, 4, (1.0, 1.12, 0, 1)), (29.95, 35.95, 5, (1.08, 1.0, 0, 0)),
         (35.95, 45.70, 6, (1.0, 1.12, -1, 0)), (45.70, 53.22, 7, (1.0, 1.08, 0, 0)), (53.22, 59.22, 8, (1.0, 1.08, 0, -1)),
         (59.22, END, 9, (1.0, 1.08, 0, 0))]
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
SEGS = [(0.00, 2.13, "Puedes caminar horas por un bosque…"), (2.52, 3.91, "y nunca encontrar uno."),
        (4.49, 7.54, "El Ganoderma no crece en la tierra como otros hongos."),
        (7.93, 12.66, "Crece en troncos y tocones de árboles de madera dura, ya viejos o muertos."),
        (13.06, 16.46, "Es lo que los científicos llaman un hongo de pudrición blanca:"),
        (16.82, 19.44, "puede deshacer la parte más dura de la madera."), (19.82, 21.27, "Así ayuda al bosque:"),
        (21.60, 24.20, "convierte los árboles caídos en tierra nueva."),
        (24.58, 27.86, "Pero en Asia, encontrarlo silvestre siempre fue difícil."), (28.18, 29.61, "Por eso era tan valorado."),
        (29.95, 32.39, "Durante siglos solo se podía recolectar."),
        (32.72, 35.59, "Fue hasta los años setenta cuando se logró cultivarlo."),
        (35.95, 37.91, "Y aquí viene lo que nadie te dice:"),
        (38.26, 41.98, "en México se han registrado más de veinte especies de Ganoderma."),
        (42.26, 45.30, "Solo en Tabasco, un estudio encontró veintiuna."), (45.70, 46.18, "Eso sí:"),
        (46.47, 49.14, "si ves uno, no lo arranques ni lo pruebes."),
        (49.47, 52.91, "Muchas especies se parecen, y solo un experto las distingue."),
        (53.22, 56.43, "Por eso el que se consume hoy viene de cultivos controlados,"),
        (56.64, 58.82, "desde el micelio hasta el hongo maduro."), (59.22, 59.79, "¿Y tú…"),
        (60.10, 62.22, "has visto algún hongo así en un árbol?")]
KEYS = {"bosque", "tierra", "troncos", "tocones", "dura", "muertos", "pudrición", "blanca", "madera", "nueva", "asia",
        "silvestre", "difícil", "valorado", "recolectar", "setenta", "cultivarlo", "méxico", "veinte", "tabasco",
        "veintiuna", "arranques", "pruebes", "experto", "controlados", "micelio", "árbol"}

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
    d.text((W / 2, 300), "CASI NUNCA LO VERÁS…", font=HOOK1, fill=CREAM + (a1,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a1))
    u = 1 + 0.25 * (1 - ease((t - 0.15) / 0.3))
    f2 = F("Anton-Regular.ttf", int(112 * u))
    d.text((W / 2, 440), "EN EL BOSQUE", font=f2, fill=GOLD + (a1,), anchor="mm", stroke_width=6, stroke_fill=(20, 10, 4, a1))
    if t > 0.7:
        s = STICKER.copy()
        v = ease((t - 0.7) / 0.25) * k
        s.putalpha(s.getchannel("A").point(lambda p: int(p * v)))
        cv.alpha_composite(s, (int((W - s.width) / 2), 540))

TAGS = [(7.93, 13.0, "ROBLE · CIRUELO · ARCE"), (13.06, 19.7, "HONGO DE PUDRICIÓN BLANCA"), (24.58, 29.9, "SILVESTRE = ESCASO"),
        (32.72, 35.9, "AÑOS 70: PRIMER CULTIVO"), (38.26, 45.6, "MÉXICO: +20 ESPECIES"), (46.47, 53.1, "NO LO ARRANQUES NI LO PRUEBES")]
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
