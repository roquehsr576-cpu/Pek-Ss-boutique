# Reel "La receta en números": café de goteo 1:16. Escribe cuadros RGB crudos a stdout.
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
DUR = 44.0
FONTS = sys.argv[1]

# Paleta del logo (sin logo ni nombre en pantalla)
BG = (28, 18, 12)
CREAM = (247, 227, 195)
CARAMEL = (217, 160, 102)
RED = (229, 50, 43)
DIM = (110, 84, 64)

def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}", size)

ANTON = {s: font("Anton-Regular.ttf", s) for s in (40, 56, 64, 72, 88, 110, 150, 300)}
OSW = {s: font("Oswald.ttf", s) for s in (36, 44, 52, 60, 66, 72)}

PHRASES = [
    (0.05, 4.16, "¿Sabías que casi todas las cafeteras de goteo se usan con la misma regla?"),
    (4.55, 7.14, "Por cada gramo de café, 16 de agua."),
    (7.48, 9.97, "Para una taza de 250 mililitros,"),
    (10.08, 11.21, "unos 15 gramos."),
    (11.39, 12.43, "La regla es:"),
    (12.68, 13.92, "1 a 16."),
    (14.44, 16.90, "El error común: medir con cucharadas."),
    (17.27, 21.10, "Una cucharada puede pesar de 5 a 8 gramos, según la molienda."),
    (21.57, 23.06, "Con más agua sale aguado."),
    (23.35, 25.14, "Con menos, demasiado fuerte."),
    (25.52, 27.36, "Si sabe agrio, muele más fino."),
    (27.65, 29.32, "Si sabe amargo, más grueso."),
    (29.80, 31.50, "Para goteo, molienda media."),
    (31.83, 34.40, "Para un litro: unos 62 gramos de café."),
    (34.72, 37.01, "No es la cafetera, es la proporción."),
    (37.38, 40.28, "1 a 16, molienda media y una báscula."),
    (40.70, 41.98, "¿Tú cuánto café le pones?"),
]
KEYS = {"regla", "16", "250", "mililitros", "15", "gramos", "cucharadas", "5", "8", "aguado", "fuerte",
        "agrio", "fino", "amargo", "grueso", "media", "62", "proporción", "báscula", "1", "gramo"}

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def prog(t, a, d=0.5):
    return ease((t - a) / d)

def lerp(a, b, k):
    return a + (b - a) * k

def col(c, k):
    return tuple(int(v * k) for v in c)

def word_times(a, b, text):
    words = text.split()
    w = [len(x) + 2 for x in words]
    tot, acc, out = sum(w), 0, []
    for word, n in zip(words, w):
        out.append((word, a + (b - a) * acc / tot))
        acc += n
    return out

WORDS = [(word_times(a, b, s), a, b) for a, b, s in PHRASES]

def wrap(words, f, maxw):
    lines, cur = [], []
    for item in words:
        test = " ".join(x[0] for x in cur + [item])
        if cur and f.getlength(test) > maxw:
            lines.append(cur)
            cur = [item]
        else:
            cur.append(item)
    if cur:
        lines.append(cur)
    return lines

def subtitles(d, t):
    for wt, a, b in WORDS:
        if a - 0.05 <= t <= b + 0.35:
            f = OSW[72]
            lines = wrap(wt, f, 900)
            y = 250
            for line in lines:
                total = f.getlength(" ".join(x[0] for x in line))
                x = (W - total) / 2
                for word, ws in line:
                    k = clamp((t - ws) / 0.12)
                    if k > 0:
                        bare = word.strip("¿?,.:").lower()
                        c = RED if bare in KEYS else CREAM
                        d.text((x, y + (1 - k) * 14), word, font=f, fill=col(c, k))
                    x += f.getlength(word + " ")
                y += 100
            return

def ctext(d, x, y, s, f, c):
    w = f.getlength(s)
    d.text((x - w / 2, y), s, font=f, fill=c)

def chip(d, cx, cy, s, f, c, k=1.0):
    w = f.getlength(s) + 60
    h = f.size + 40
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, outline=col(c, k), width=5)
    bb = f.getbbox(s)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=col(c, k))

def cafetera(d, cx, cy, s, c, w=6):
    # Cafetera de goteo en líneas: cuerpo, depósito, jarra
    d.rounded_rectangle((cx - 50 * s, cy - 90 * s, cx + 50 * s, cy - 50 * s), radius=10 * s, outline=c, width=w)
    d.line((cx + 40 * s, cy - 50 * s, cx + 40 * s, cy + 90 * s), fill=c, width=w)
    d.line((cx - 50 * s, cy + 90 * s, cx + 50 * s, cy + 90 * s), fill=c, width=w)
    d.polygon((cx - 40 * s, cy - 50 * s, cx + 20 * s, cy - 50 * s, cx - 10 * s, cy - 20 * s), outline=c, width=w)
    d.rounded_rectangle((cx - 40 * s, cy + 10 * s, cx + 20 * s, cy + 85 * s), radius=12 * s, outline=c, width=w)
    d.line((cx - 10 * s, cy - 15 * s, cx - 10 * s, cy + 5 * s), fill=c, width=max(2, w // 2))

def cuchara(d, cx, cy, s, c, heap, k):
    d.ellipse((cx - 60 * s, cy - 30 * s, cx + 60 * s, cy + 30 * s), outline=c, width=6)
    d.line((cx + 58 * s, cy, cx + 200 * s, cy + 30 * s), fill=c, width=8)
    if heap > 0:
        h = heap * k
        d.pieslice((cx - 55 * s, cy - h * s, cx + 55 * s, cy + h * s), 180, 360, fill=col(CARAMEL, 0.8))

def bascula(d, cx, cy, s, c):
    d.rounded_rectangle((cx - 110 * s, cy - 20 * s, cx + 110 * s, cy + 60 * s), radius=14 * s, outline=c, width=6)
    d.line((cx - 130 * s, cy - 30 * s, cx + 130 * s, cy - 30 * s), fill=c, width=6)
    d.rounded_rectangle((cx - 50 * s, cy + 5 * s, cx + 50 * s, cy + 40 * s), radius=6 * s, outline=c, width=4)

def scene(d, t):
    cx, cy = W / 2, 1050
    # 1. Gancho: cuadrícula de cafeteras que se llena
    if t < 4.45:
        n = 20
        shown = int(clamp(t / 3.4) * n) + 1
        for i in range(min(n, shown)):
            r, c = divmod(i, 4)
            x, y = 200 + c * 227, 640 + r * 230
            k = clamp((t - i * 3.4 / n) / 0.25)
            cafetera(d, x, y, 0.8, col(CARAMEL if i % 7 else CREAM, k), 5)
        return
    # 2. 1 g de café -> 16 g de agua
    if t < 7.35:
        k1, k2 = prog(t, 4.6), prog(t, 5.9)
        ctext(d, cx, 650, "CAFÉ", OSW[52], col(CARAMEL, k1))
        ctext(d, cx, 720, "1 g", ANTON[150], col(CREAM, k1))
        if k2 > 0:
            v = int(round(lerp(0, 16, clamp((t - 5.9) / 0.8))))
            ctext(d, cx, 1040, "AGUA", OSW[52], col(CARAMEL, k2))
            ctext(d, cx, 1110, f"{v} g", ANTON[300], col(CREAM, k2))
        return
    # 3. Una taza: 250 ml y 15 g
    if t < 12.5:
        k = prog(t, 7.4)
        lvl = clamp((t - 7.6) / 2.2)
        top, bot, l, r = 640, 1160, 330, 750
        d.line((l, top, l + 30, bot), fill=col(CREAM, k), width=8)
        d.line((r, top, r - 30, bot), fill=col(CREAM, k), width=8)
        d.line((l + 30, bot, r - 30, bot), fill=col(CREAM, k), width=8)
        d.arc((r - 40, 760, r + 110, 980), -90, 90, fill=col(CREAM, k), width=8)
        wy = bot - (bot - top - 40) * lvl
        d.polygon((l + 30 * (wy - top) / (bot - top) + 8, wy, r - 30 * (wy - top) / (bot - top) - 8, wy, r - 38, bot - 8, l + 38, bot - 8),
                  fill=col(CARAMEL, 0.55 * k))
        ml = int(round(250 * lvl))
        ctext(d, cx, 1230, f"{ml} ml", ANTON[150], col(CREAM, k))
        k2 = prog(t, 10.1)
        if k2 > 0:
            g = int(round(15 * clamp((t - 10.1) / 0.7)))
            chip(d, cx, 1530, f"{g} g de café", ANTON[88], CARAMEL, k2)
        return
    # 4. La regla gigante
    if t < 14.35:
        k = prog(t, 12.55, 0.35)
        s = 1 + 0.06 * (1 - k)
        f = ANTON[300]
        ctext(d, cx, 820 - 20 * (s - 1) * 10, "1 : 16", f, col(CREAM, k))
        ctext(d, cx, 1180, "CAFÉ  :  AGUA", OSW[52], col(CARAMEL, k))
        return
    # 5. Mito: la cucharada no es medida
    if t < 21.4:
        k = prog(t, 14.5)
        cuchara(d, 300, 820, 1.6, col(CREAM, k), 26, prog(t, 17.5))
        cuchara(d, 300, 1160, 1.6, col(CREAM, k), 44, prog(t, 18.0))
        if t > 18.9:
            ctext(d, 860, 760, "5 g", ANTON[110], col(CREAM, prog(t, 18.9, 0.3)))
        if t > 19.4:
            ctext(d, 860, 1100, "8 g", ANTON[110], col(CREAM, prog(t, 19.4, 0.3)))
        kk = prog(t, 16.0)
        ctext(d, cx, 1420, "1 CUCHARADA", ANTON[110], col(CARAMEL, kk))
        if t > 16.4:
            x = lerp(270, 810, prog(t, 16.4, 0.35))
            d.line((270, 1490, x, 1490), fill=RED, width=12)
        return
    # 6. Zona correcta 1:15 a 1:17
    if t < 25.4:
        k = prog(t, 21.45)
        x0, x1, y = 140, 940, 980
        def px(r):
            return x0 + (r - 12) / 8 * (x1 - x0)
        d.rounded_rectangle((px(15), y - 50, px(17), y + 50), radius=18, fill=col((60, 44, 30), k), outline=col(CARAMEL, k), width=4)
        d.line((x0, y, x1, y), fill=col(CREAM, k), width=6)
        for r in range(12, 21):
            d.line((px(r), y - 20, px(r), y + 20), fill=col(CREAM, k), width=4)
            if r in (12, 15, 16, 17, 20):
                ctext(d, px(r), y + 40, f"1:{r}", OSW[44], col(CREAM if r == 16 else DIM, k))
        if t < 23.2:
            m = lerp(16, 19.5, prog(t, 21.8, 0.9))
            lab = "AGUADO"
        else:
            m = lerp(19.5, 12.7, prog(t, 23.3, 1.0))
            lab = "MUY FUERTE"
        bad = m < 15 or m > 17
        c = RED if bad else CREAM
        d.polygon((px(m) - 26, y - 110, px(m) + 26, y - 110, px(m), y - 62), fill=c)
        if bad:
            lx = clamp(px(m), 60 + ANTON[88].getlength(lab) / 2, W - 60 - ANTON[88].getlength(lab) / 2)
            ctext(d, lx, y - 230, lab, ANTON[88], c)
        ctext(d, cx, 1220, "ZONA IDEAL: 1:15 a 1:17", OSW[52], col(CARAMEL, k))
        return
    # 7. Molienda: slider fino -> grueso
    if t < 31.7:
        k = prog(t, 25.5)
        x0, x1, y = 160, 920, 1150
        d.line((x0, y, x1, y), fill=col(CREAM, k), width=8)
        ctext(d, x0 + 30, y + 50, "FINO", OSW[52], col(CREAM, k))
        ctext(d, x1 - 60, y + 50, "GRUESO", OSW[52], col(CREAM, k))
        if t < 27.6:
            v = lerp(0.5, 0.15, prog(t, 26.4, 0.8)); lab, lc = "¿AGRIO?", RED
        elif t < 29.7:
            v = lerp(0.15, 0.85, prog(t, 27.8, 0.9)); lab, lc = "¿AMARGO?", RED
        else:
            v = lerp(0.85, 0.5, prog(t, 29.9, 0.7)); lab, lc = "GOTEO: MEDIA", CARAMEL
        kx = lerp(x0, x1, v)
        d.ellipse((kx - 34, y - 34, kx + 34, y + 34), fill=CREAM)
        ctext(d, cx, 1330, lab, ANTON[110], col(lc, k))
        # partículas del tamaño que marca el slider
        r = lerp(5, 26, v)
        rng = np.random.default_rng(7)
        for i in range(26):
            px_, py_ = rng.uniform(150, 930), rng.uniform(620, 980)
            rr = r * rng.uniform(0.7, 1.2)
            d.ellipse((px_ - rr, py_ - rr, px_ + rr, py_ + rr), fill=col(CARAMEL, 0.85 * k))
        return
    # 8. Barras: 250 ml, 500 ml, 1 litro
    if t < 34.6:
        data = [("250 ml", 15), ("500 ml", 31), ("1 litro", 62)]
        base = 1350
        for i, (lab, g) in enumerate(data):
            k = prog(t, 31.9 + i * 0.5, 0.6)
            x = 230 + i * 310
            h = 9.5 * g * k
            c = RED if i == 2 else CARAMEL
            d.rounded_rectangle((x - 80, base - h, x + 80, base), radius=14, fill=col(c, 0.9 if k else 0))
            if k > 0:
                ctext(d, x, base - h - 110, f"{int(round(g * k))} g", ANTON[88], col(CREAM, k))
                ctext(d, x, base + 25, lab, OSW[44], col(CREAM, k))
        return
    # 9. No es la cafetera
    if t < 37.25:
        k = prog(t, 34.7)
        cafetera(d, cx, 900, 2.2, col(CREAM, k), 10)
        if t > 35.1:
            p = prog(t, 35.1, 0.35)
            d.line((cx - 260, 620, lerp(cx - 260, cx + 260, p), lerp(620, 1180, p)), fill=RED, width=18)
            d.line((cx + 260, 620, lerp(cx + 260, cx - 260, p), lerp(620, 1180, p)), fill=RED, width=18)
        if t > 36.0:
            ctext(d, cx, 1330, "ES LA PROPORCIÓN", ANTON[110], col(CARAMEL, prog(t, 36.0, 0.4)))
        return
    # 10. Tarjeta resumen para guardar
    k = prog(t, 37.3)
    d.rounded_rectangle((110, 560, 970, 1650), radius=40, outline=col(CARAMEL, k), width=5)
    ctext(d, cx, 610, "CAFÉ DE GOTEO", OSW[52], col(CARAMEL, k))
    chip(d, cx, 820, "1 : 16", ANTON[150], CREAM, prog(t, 37.4))
    chip(d, cx, 1040, "15 g por taza", ANTON[72], CREAM, prog(t, 38.4))
    chip(d, cx, 1210, "molienda media", ANTON[72], CREAM, prog(t, 38.9))
    kb = prog(t, 39.4)
    if kb > 0:
        bascula(d, cx, 1420, 1.2, col(CREAM, kb))
        ctext(d, cx, 1530, "y una báscula", OSW[44], col(CREAM, kb))

def bg_array():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.45 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2
    return np.stack([np.full((H, W), c, np.float32) * v for c in BG], -1)

BGA = bg_array()

def frame(t):
    g = Image.new("RGB", (W, H), (0, 0, 0))
    scene(ImageDraw.Draw(g), t)
    small = g.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    s = Image.new("RGB", (W, H), (0, 0, 0))
    subtitles(ImageDraw.Draw(s), t)
    out = BGA + np.asarray(g, np.float32) + 0.6 * np.asarray(small, np.float32)
    sa = np.asarray(s, np.float32)
    mask = sa.max(-1, keepdims=True) > 0
    out = np.where(mask, np.maximum(out, sa), out)
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    if len(sys.argv) > 4:
        Image.fromarray(frame(float(sys.argv[4]))).save(sys.argv[5])
        sys.exit()
    start, end = float(sys.argv[2]), float(sys.argv[3])
    for i in range(int(start * FPS), int(end * FPS)):
        sys.stdout.buffer.write(frame(i / FPS).tobytes())
