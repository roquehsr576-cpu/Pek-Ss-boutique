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

W, H, FPS = 1080, 1920, 30
GOLD = (240, 196, 102)
CREAM = (255, 246, 232)
DARK = (34, 20, 10)
END = 134.0
FIN = 129.4   # closing card

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def load(name):
    im = Image.open(f"{D}/{name}.png").convert("RGB")
    sc = max(W / im.width, H / im.height) * 1.12
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)

NAMES = ["nubes", "cup", "sierra_oscura", "pinos", "ladera", "valle", "camino", "platanar", "verdes", "rojas",
         "secado", "pradera", "sierra"]
IMGS = {n: load(n) for n in NAMES}
CARDS = Cards(W, H, FD, Image.open(f"{D}/secado.png"))

SHOTS = [(0.0, 6.2, "nubes", (1.0, 1.08, 0, 0)), (6.2, 11.3, "cup", (1.0, 1.07, 1, 0)),
         (11.3, 18.3, "sierra_oscura", (1.0, 1.08, -1, 0)), (18.3, 24.7, "pinos", (1.0, 1.07, 0, 1)),
         (24.7, 32.2, "#fecha", None), (32.2, 43.8, "#pagan", None), (43.8, 48.8, "#piden", None),
         (48.8, 52.1, "ladera", (1.0, 1.07, 1, 0)), (52.1, 54.0, "valle", (1.0, 1.06, -1, 0)),
         (54.0, 56.1, "camino", (1.0, 1.08, 0, 0)), (56.1, 59.0, "platanar", (1.0, 1.07, 1, 0)),
         (59.0, 64.0, "verdes", (1.0, 1.08, 0, 1)), (64.0, 66.7, "rojas", (1.0, 1.08, -1, 0)),
         (66.7, 68.4, "secado", (1.0, 1.07, 1, 0)), (68.4, 71.0, "pradera", (1.0, 1.06, -1, 0)),
         (71.0, 75.7, "pinos", (1.0, 1.08, 1, 0)), (75.7, 82.2, "sierra_oscura", (1.0, 1.08, 0, 0)),
         (82.2, 89.4, "camino", (1.0, 1.07, -1, 0)), (89.4, 95.7, "sierra", (1.0, 1.08, 1, 0)),
         (95.7, 100.5, "valle", (1.0, 1.07, 0, 1)), (100.5, 104.2, "cup", (1.0, 1.08, -1, 0)),
         (104.2, 106.9, "rojas", (1.0, 1.08, 1, 0)), (106.9, 110.9, "cup", (1.0, 1.06, 0, 0)),
         (110.9, 115.2, "secado", (1.0, 1.08, -1, 0)), (115.2, 119.9, "pradera", (1.0, 1.07, 1, 0)),
         (119.9, 124.3, "ladera", (1.0, 1.08, 0, 1)), (124.3, END, "nubes", (1.0, 1.10, 0, 0))]
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
    if name.startswith("#"):
        return getattr(CARDS, name[1:])((t - a) / (b - a), t - a)
    fr = grade(shot_frame(IMGS[name], punched(mv, a, t), (t - a) / (b - a)))
    # crossfade from the previous photo shot (cards cut hard, like a news insert)
    if i > 0 and t - a < XF and not SHOTS[i - 1][2].startswith("#"):
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
        "lástima", "respeto", "reconocimiento", "oportunidades", "mesa"}

# captions straight from the word timestamps, dropping the emotion tags
WORDS = [(w["text"], w["start"], w["end"]) for w in json.load(open(f"{D}/words.json"))["words"]
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
    if t > 6.1: return
    k = 1 - ease((t - 5.7) / 0.4)
    d = ImageDraw.Draw(cv)
    a = int(255 * k)
    d.text((W / 2, 280), "El verdadero", font=HOOK1, fill=CREAM + (a,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a))
    u = 1 + 0.06 * (1 - ease(t / 0.2))
    d.text((W / 2, 420), "PRECIO", font=F("Anton-Regular.ttf", int(160 * u)), fill=GOLD + (a,), anchor="mm",
           stroke_width=6, stroke_fill=(20, 10, 4, a))
    d.text((W / 2, 560), "del café", font=HOOK1, fill=CREAM + (a,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a))
    cv.alpha_composite(fade(STICKER, k), (int((W - STICKER.width) / 2), 650))

TAGS = [(89.6, 95.6, "DE CHIAPAS A OAXACA"), (95.8, 100.4, "IDENTIDAD · CULTURA · SUSTENTO")]
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
    d = ImageDraw.Draw(cv)
    for j, line in enumerate(["El verdadero valor del café", "comienza en las manos", "de quien lo cultiva."]):
        kk = ease((t - FIN - 0.2 * j) / 0.5)
        d.text((W / 2, 760 + 90 * j), line, font=SERIF, fill=CREAM + (int(255 * kk),), anchor="mm")
    kq = ease((t - FIN - 1.4) / 0.6)
    d.line([(W / 2 - 160, 1050), (W / 2 + 160, 1050)], fill=GOLD + (int(255 * kq),), width=3)
    for j, line in enumerate(["¿Sabías cuánto recibe", "quien cultiva tu café?"]):
        d.text((W / 2, 1140 + 70 * j), line, font=QF, fill=GOLD + (int(255 * kq),), anchor="mm")

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
