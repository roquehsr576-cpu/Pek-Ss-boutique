"""Carrusel 'La historia del ruyi' (4 láminas 1080x1350, sin logo) con las ilustraciones del episodio 3."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
IMG, FD, OUT = sys.argv[1:4]
PW, PH = 1080, 1350
GOLD, CREAM, DARK = (232, 186, 98), (252, 243, 228), (40, 22, 12)
H = lambda s: ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
L = lambda s: ImageFont.truetype(f"{FD}/LilitaOne-Regular.ttf", s)

def bg(name, top=0.75, bot=0.85, fy=0.5):
    im = Image.open(f"{IMG}/{name}").convert("RGB")
    sc = max(PW / im.width, PH / im.height); im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    y0 = int((im.height - PH) * fy); im = im.crop(((im.width - PW) // 2, y0, (im.width - PW) // 2 + PW, y0 + PH))
    yy = np.linspace(0, 1, PH)[:, None, None]
    shade = 1 - np.clip((0.38 - yy) / 0.38, 0, 1) * top - np.clip((yy - 0.6) / 0.4, 0, 1) * bot
    a = np.asarray(im, np.float32) * np.array([1.04, 1, 0.94]) * shade
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")

def wrap(d, txt, f, maxw):
    out, line = [], ""
    for w in txt.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: out.append(line); line = w
    return out + [line]

def block(im, spec, y):
    d = ImageDraw.Draw(im)
    for txt, f, col in spec:
        for ln in wrap(d, txt, f, PW - 140):
            d.text((PW / 2, y), ln, font=f, fill=col, anchor="ma", stroke_width=max(3, f.size // 16), stroke_fill=(20, 10, 4))
            y += int(f.size * 1.15)
        y += int(f.size * 0.3)
    return y

def tag(im, text, y):
    d = ImageDraw.Draw(im); f = L(40)
    w = d.textlength(text, font=f)
    d.rounded_rectangle(((PW - w) / 2 - 28, y, (PW + w) / 2 + 28, y + 64), 20, fill=CREAM)
    d.text((PW / 2, y + 32), text, font=f, fill=DARK, anchor="mm")

def num(im, k):
    ImageDraw.Draw(im).text((PW - 60, PH - 50), f"{k}/4", font=L(34), fill=CREAM + (200,), anchor="rs")

# 1 · gancho
im = bg("img0.png", 0.8, 0.7, 0.45)
tag(im, "Lo que nadie te dice", 70)
block(im, [("IMAGINA LA CHINA", H(104), CREAM), ("DE HACE 300 AÑOS…", H(104), GOLD)], 170)
block(im, [("Un artesano pasa meses tallando un regalo para el cumpleaños del emperador.", L(50), CREAM)], 1080)
num(im, 1); im.convert("RGB").save(f"{OUT}/1.jpg", quality=93)

# 2 · el ruyi
im = bg("img1.png", 0.8, 0.8, 0.35)
block(im, [("No es una joya.", L(64), CREAM), ("Ni una espada.", L(64), CREAM)], 90)
block(im, [("Es un RUYI: un cetro con la punta en forma de hongo lingzhi.", L(52), GOLD)], 1060)
num(im, 2); im.convert("RGB").save(f"{OUT}/2.jpg", quality=93)

# 3 · la entrega
im = bg("img3.png", 0.85, 0.8, 0.5)
block(im, [("Lo entrega con una reverencia.", L(56), CREAM), ("No dice nada… no hace falta.", L(56), CREAM)], 80)
block(im, [("RUYI SIGNIFICA", H(70), CREAM), ("“COMO DESEES”", H(110), GOLD)], 1010)
num(im, 3); im.convert("RGB").save(f"{OUT}/3.jpg", quality=93)

# 4 · hoy
im = bg("img7.png", 0.8, 0.85, 0.5)
block(im, [("Hoy piezas así están en el Met de Nueva York y en el Museo del Palacio en Taipéi…", L(52), CREAM)], 90)
block(im, [("…y casi nadie sabe", L(60), CREAM), ("QUE ESTÁ VIENDO", H(92), GOLD), ("UN HONGO.", H(92), GOLD)], 950)
num(im, 4); im.convert("RGB").save(f"{OUT}/4.jpg", quality=93)
print("ok")
