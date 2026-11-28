"""Documentary 'El verdadero precio del café' (unbranded, educational). Real photos + data cards,
captions timed from the narration's word timestamps. Raw RGB frames on stdout.

Usage: reel.py <dir with photos, words.json, cards.py> <fonts dir>
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D, FD = sys.argv[1:3]
sys.path.insert(0, D)
from cards import Cards
from mapa import Mapa

W, H, FPS = 1080, 1920, 30
GOLD = (240, 196, 102)
CREAM = (255, 246, 232)
DARK = (34, 20, 10)
END = 141.0
FIN = 136.0   # closing card

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def load(name):
    im = Image.open(f"{D}/{name}.png").convert("RGB")
    sc = max(W / im.width, H / im.height) * 1.12
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)

NAMES = ["cafetal", "cup", "grano", "pinos", "rojas", "sierra_oscura", "nubes", "ladera", "platanar", "valle", "camino",
         "tierra", "verdes", "sierra", "petate", "pradera"]
IMGS = {n: load(n) for n in NAMES}
CARDS = Cards(W, H, FD, Image.open(f"{D}/petate.png"))
MAPA = Mapa(W, H, FD, sys.argv[3] if len(sys.argv) > 3 and sys.argv[3].endswith(".json") else f"{D}/../geo/mx.json")

M = lambda z, px, py: (1.0, z, px, py)
SHOTS = [(0.0, 6.6, "cafetal", M(1.08, 0, -1)), (6.6, 9.6, "cup", M(1.07, 1, 0)), (9.6, 12.4, "grano", M(1.10, 0, 0)),
         (12.4, 15.2, "pinos", M(1.08, -1, 0)), (15.2, 25.8, "@map", None), (25.8, 28.2, "rojas", M(1.08, 1, 0)),
         (28.2, 30.0, "sierra_oscura", M(1.07, -1, 0)), (30.0, 32.1, "nubes", M(1.08, 0, 0)),
         (32.1, 38.6, "#fecha", None), (38.6, 45.9, "#pagan", None), (45.9, 50.2, "#piden", None), (50.2, 60.4, "#veracruz", None),
         (60.4, 62.2, "ladera", M(1.07, 1, 0)), (62.2, 64.0, "platanar", M(1.08, -1, 0)), (64.0, 65.7, "valle", M(1.06, 1, 0)),
         (65.7, 67.5, "camino", M(1.08, 0, 1)), (67.5, 70.3, "tierra", M(1.07, -1, 0)), (70.3, 72.3, "verdes", M(1.08, 0, 1)),
         (72.3, 75.5, "sierra", M(1.07, 1, 0)), (75.5, 78.7, "rojas", M(1.10, -1, 0)), (78.7, 80.7, "pinos", M(1.08, 1, 0)),
         (80.7, 83.4, "petate", M(1.08, 0, 1)), (83.4, 84.5, "cafetal", M(1.10, 1, 0)), (84.5, 85.9, "pradera", M(1.06, -1, 0)),
         (85.9, 90.6, "valle", M(1.08, 0, 0)), (90.6, 93.4, "nubes", M(1.07, 1, 0)), (93.4, 96.1, "grano", M(1.10, -1, 0)),
         (96.1, 99.0, "tierra", M(1.08, 1, 0)), (99.0, 102.2, "cafetal", M(1.08, 0, 1)), (102.2, 105.5, "@map2", None),
         (105.5, 108.6, "ladera", M(1.08, -1, 0)), (108.6, 111.0, "pradera", M(1.07, 1, 0)), (111.0, 113.4, "sierra", M(1.08, 0, 0)),
         (113.4, 116.8, "cup", M(1.07, -1, 0)), (116.8, 119.4, "tierra", M(1.10, 0, 1)), (119.4, 123.0, "grano", M(1.08, 1, 0)),
         (123.0, 125.0, "petate", M(1.07, -1, 0)), (125.0, 127.4, "rojas", M(1.08, 1, 0)), (127.4, 130.5, "pinos", M(1.08, 0, 0)),
         (130.5, 133.2, "ladera", M(1.07, 1, 0)), (133.2, END, "valle", M(1.10, 0, 0))]
XF = 0.35
PUNCH = 2.6

def shot_frame(img, move, u):
    z0, z1, px, py = move
    z = z0 + (z1 - z0) * ease(u)
    vw, vh = img.width / 1.12 / z, img.height / 1.12 / z
    mx, my = (img.width - vw) / 2, (img.height - vh) / 2
    cx = img.width / 2 + px * mx * (ease(u) - 0.5) * 0.9
    cy = img.height / 2 + py * my * (ease(u) - 0.5) * 0.9
    return img.crop(tuple(int(v) for v in (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2))).resize((W, H), Image.BILINEAR)

def punched(move, a, t):
    k = int((t - a) / PUNCH)
    if k % 2 == 0: return move
    z0, z1, px, py = move
    return (z0 * 1.12, z1 * 1.12, -px if px else (1 if k % 4 == 1 else -1), py)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1 - 0.55 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2), 0.35, 1)
GRAD = np.clip((yy - 1180) / 500, 0, 1) * 0.72 + np.clip((420 - yy) / 420, 0, 1) * 0.45
SHADE = (VIG * (1 - GRAD))[..., None]
WARM = np.array([1.04, 1.0, 0.94], np.float32)

def grade(im):
    a = np.asarray(im, np.float32) * WARM * SHADE
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def background(t):
    for i, (a, b, name, mv) in enumerate(SHOTS):
        if a <= t < b: break
    if name == "@map":
        return MAPA.frame(t - a, b - a)
    if name == "@map2":
        return MAPA.frame(t - a, b - a, lights=(0.2, 0.9, 1.9, 2.3), total_at=None, zoom=0)
    if name.startswith("#"):
        return getattr(CARDS, name[1:])(t - a, b - a)
    fr = grade(shot_frame(IMGS[name], punched(mv, a, t), (t - a) / (b - a)))
    # crossfade from the previous photo shot (cards cut hard, like a news insert)
    if i > 0 and t - a < XF and SHOTS[i - 1][2][0] not in "#@":
        pa, pb, pn, pm = SHOTS[i - 1]
        prev = grade(shot_frame(IMGS[pn], punched(pm, pa, t), (t - pa) / (pb - pa)))
        fr = Image.blend(prev, fr, ease((t - a) / XF))
    return fr

def F(name, size, w=None):
    f = ImageFont.truetype(f"{FD}/{name}", size)
    if w: f.set_variation_by_axes([w])
    return f
HOOK1 = F("LilitaOne-Regular.ttf", 88)
STICK = F("Oswald.ttf", 44, 600)
CAP = F("LilitaOne-Regular.ttf", 72)
SERIF = F("PlayfairDisplay.ttf", 64, 600)
QF = F("Oswald.ttf", 52, 500)

KEYS = {"costó", "esfuerzo", "méxico", "calles", "valor", "trabajo", "precio", "justo", "43", "45", "55", "pesos",
        "chiapas", "tapachula", "robusta", "dialogar", "temprano", "montañas", "tierra", "enfermedades", "clima",
        "frutos", "paciencia", "conocimiento", "tradición", "generación", "valiosa", "poco", "nada", "dignamente",
        "oaxaca", "identidad", "cultura", "familias", "cafetería", "manos", "cultiva", "familia", "historia",
        "lástima", "respeto", "reconocimiento", "oportunidades", "mesa", "veracruz", "puebla", "noventa", "cosecha",
        "preocupación", "huatusco", "8", "7", "cereza", "roya", "maduros", "sol", "sustento"}

# captions straight from the word timestamps, dropping the emotion tags
WORDS = [(w["text"], w["start"], w["end"]) for w in json.load(open(f"{D}/words2.json"))["words"]
         if w.get("type", "word") == "word" and not w["text"].startswith("[")]
CAPS, cur = [], []
for k, (w, s, e) in enumerate(WORDS):
    cur.append((w, s, e))
    gap = WORDS[k + 1][1] - e if k + 1 < len(WORDS) else 9
    if len(cur) >= 4 or w[-1] in ",.…?:" or gap > 0.45:
        CAPS.append(cur); cur = []
if cur: CAPS.append(cur)

def draw_caption(cv, t):
    for i, c in enumerate(CAPS):
        a, b = c[0][1], c[-1][2]
        nxt = CAPS[i + 1][0][1] if i + 1 < len(CAPS) else b + 0.6
        if not (a - 0.05 <= t < min(nxt, b + 0.6)): continue
        d = ImageDraw.Draw(cv)
        widths = [d.textlength(w, font=CAP) for w, _, _ in c]
        gap = 20
        lines, ln, cw = [], [], 0
        for k, wd in enumerate(widths):
            if ln and cw + gap + wd > 940:
                lines.append(ln); ln, cw = [], 0
            ln.append(k); cw += (gap if cw else 0) + wd
        lines.append(ln)
        y = 1500 - (len(lines) - 1) * 44
        for ln in lines:
            lw = sum(widths[k] for k in ln) + gap * (len(ln) - 1)
            x = (W - lw) / 2
            for k in ln:
                w, s, _ = c[k]
                if t >= s - 0.05:
                    u = ease((t - s + 0.05) / 0.12)
                    col = GOLD if w.strip("¿?¡!.,:…").lower() in KEYS else CREAM
                    d.text((x, y + int(10 * (1 - u))), w, font=CAP, fill=col + (int(255 * u),), stroke_width=6,
                           stroke_fill=(20, 10, 4, int(230 * u)))
                x += widths[k] + gap
            y += 88
        break

def sticker(text, font, angle):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t_, r, b = d0.textbbox((0, 0), text, font=font)
    im = Image.new("RGBA", (r - l + 70, b - t_ + 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=22, fill=CREAM + (255,))
    d.text((35 - l, 22 - t_), text, font=font, fill=DARK)
    return im.rotate(angle, resample=Image.BICUBIC, expand=True)
STICKER = sticker("les pagan menos de lo que les cuesta", STICK, 3)

def fade(im, k):
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda p: int(p * k))); return im

def hook(cv, t):
    if t > 6.5: return
    k = 1 - ease((t - 6.1) / 0.4)
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(top)
    a = int(255 * k)
    d.text((W / 2, 280), "El verdadero", font=HOOK1, fill=CREAM + (a,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a))
    u = 1 + 0.06 * (1 - ease(t / 0.2))
    d.text((W / 2, 420), "PRECIO", font=F("Anton-Regular.ttf", int(160 * u)), fill=GOLD + (a,), anchor="mm",
           stroke_width=6, stroke_fill=(20, 10, 4, a))
    d.text((W / 2, 560), "del café", font=HOOK1, fill=CREAM + (a,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a))
    top.alpha_composite(fade(STICKER, k), (int((W - STICKER.width) / 2), 650))
    cv.alpha_composite(top)

TAGS = [(25.9, 28.1, "TEMPORADA DE COSECHA"), (70.4, 72.2, "LA ROYA"), (108.7, 113.3, "IDENTIDAD · CULTURA · SUSTENTO")]
def pin(cv, t):
    for a, b, text in TAGS:
        if not (a <= t < b): continue
        k = ease((t - a) / 0.3) * (1 - ease((t - (b - 0.3)) / 0.3))
        s = sticker(text, F("Anton-Regular.ttf", 84 if len(text) <= 20 else 60), -3)
        cv.alpha_composite(fade(s, k), (int((W - s.width) / 2), int(360 - 30 * (1 - k))))

def closing(cv, t):
    if t < FIN: return
    k = ease((t - FIN) / 0.6)
    cv.alpha_composite(Image.new("RGBA", (W, H), (12, 7, 4, int(170 * k))))
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(top)
    for j, line in enumerate(["El verdadero valor del café", "comienza en las manos", "de quien lo cultiva."]):
        kk = ease((t - FIN - 0.2 * j) / 0.5)
        d.text((W / 2, 760 + 90 * j), line, font=SERIF, fill=CREAM + (int(255 * kk),), anchor="mm")
    kq = ease((t - FIN - 1.4) / 0.6)
    d.line([(W / 2 - 160, 1050), (W / 2 + 160, 1050)], fill=GOLD + (int(255 * kq),), width=3)
    for j, line in enumerate(["¿Sabías cuánto recibe", "quien cultiva tu café?"]):
        d.text((W / 2, 1140 + 70 * j), line, font=QF, fill=GOLD + (int(255 * kq),), anchor="mm")
    cv.alpha_composite(top)

def frame(t):
    cv = background(t).convert("RGBA")
    hook(cv, t)
    pin(cv, t)
    if t < FIN: draw_caption(cv, t)
    closing(cv, t)
    return cv.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 3:   # preview stills
        for ts in sys.argv[3].split(","):
            frame(float(ts)).save(f"{D}/prev_{ts}.jpg", quality=80)
        sys.exit()
    o = sys.stdout.buffer
    for n in range(int(END * FPS)):
        o.write(frame(n / FPS).tobytes())
