"""Reel educativo de diabetes (sin productos): clips Veo de fondo + gancho, subtítulos palabra por palabra,
etiquetas, tarjetas de glucosa y las 5 señales. Uso: diab_reel.py <bg.mp4> <fonts> → frames RGB por stdout."""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
BG, FD = sys.argv[1:3]
W, H, FPS = 1080, 1920, 30
END = 77.4
GOLD, CREAM, DARK = (245, 196, 90), (252, 243, 228), (30, 14, 10)
GREEN, AMBER, RED = (86, 190, 110), (240, 170, 50), (220, 70, 60)

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def F(name, size, w=None):
    f = ImageFont.truetype(f"{FD}/{name}", size)
    if w: f.set_variation_by_axes([w])
    return f
HOOK1, CAP, STICK = F("LilitaOne-Regular.ttf", 84), F("LilitaOne-Regular.ttf", 72), F("Oswald.ttf", 44, 600)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1 - 0.5 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2), 0.4, 1)
GRAD = np.clip((yy - 1200) / 480, 0, 1) * 0.7 + np.clip((420 - yy) / 420, 0, 1) * 0.45
SHADE = (VIG * (1 - GRAD))[..., None]

SEGS = [(0.00, 1.79, "Tu sangre puede estar dulce…"), (2.28, 4.07, "y tú no sentir nada."), (4.73, 5.49, "Cuando comes,"),
        (5.67, 8.36, "tu cuerpo convierte parte de la comida en glucosa:"), (8.67, 11.15, "el azúcar que tus células usan como energía."),
        (11.54, 13.47, "Pero la glucosa no entra sola."), (13.84, 15.07, "Necesita una llave:"), (15.48, 16.28, "la insulina."),
        (16.71, 18.96, "La insulina abre la puerta de la célula…"), (19.40, 20.75, "y la glucosa entra."),
        (21.19, 23.23, "En la diabetes, la llave falta…"), (23.56, 25.37, "o la puerta ya no responde bien."),
        (25.70, 28.23, "Entonces el azúcar se queda en la sangre."), (28.59, 29.42, "Y se acumula."), (29.99, 30.78, "Antes de seguir:"),
        (31.15, 32.99, "¿tú sabes cuánto tienes de glucosa?"), (33.40, 34.09, "En ayunas:"), (34.33, 35.92, "menos de 100 es normal."),
        (36.25, 38.08, "De 100 a 125,"), (38.26, 39.35, "es prediabetes."), (39.70, 41.40, "Y 126 o más,"), (41.66, 42.38, "diabetes."),
        (42.79, 46.65, "En México, casi uno de cada cinco adultos vive con diabetes…"),
        (46.99, 49.58, "y uno de cada tres de ellos no lo sabe."), (49.99, 51.96, "Pon atención si tienes mucha sed,"),
        (52.25, 53.16, "orinas seguido,"), (53.42, 54.56, "te sientes cansado,"), (54.87, 55.72, "ves borroso…"),
        (55.99, 57.68, "o tus heridas tardan en sanar."), (58.07, 58.62, "Pero ojo:"),
        (58.89, 61.38, "la prediabetes casi nunca da señales."),
        (61.68, 65.85, "Por eso la única forma de saberlo es con un análisis de glucosa en ayunas."),
        (66.20, 67.72, "Si te identificaste con algo,"), (67.94, 70.38, "hazte el análisis y platícalo con tu médico."),
        (70.75, 71.44, "Es sencillo…"), (71.79, 73.43, "y te puede cambiar la vida."), (73.87, 74.27, "¿Y tú…"),
        (74.55, 76.54, "cuándo fue la última vez que te lo hiciste?")]
KEYS = {"sangre", "dulce", "nada", "glucosa", "energía", "llave", "insulina", "puerta", "célula", "diabetes", "acumula",
        "100", "125", "126", "normal", "prediabetes", "méxico", "cinco", "tres", "sabe", "sed", "seguido", "cansado",
        "borroso", "sanar", "ojo", "señales", "análisis", "médico", "vida", "hiciste"}

def chunks(text):
    out, cur = [], []
    for w in text.split():
        cur.append(w)
        if len(cur) >= 4 or (w[-1] in ",:." and len(cur) >= 2): out.append(cur); cur = []
    if cur:
        if out and len(cur) == 1: out[-1] += cur
        else: out.append(cur)
    return out
CAPS = []
for a, b, text in SEGS:
    cs = chunks(text); total = sum(len(" ".join(c)) for c in cs); x = a
    for c in cs:
        d = (b - a) * len(" ".join(c)) / total; n = len(" ".join(c)); acc = 0; wt = []
        for w in c: wt.append((w, x + d * acc / n)); acc += len(w) + 1
        CAPS.append((x, x + d, wt)); x += d

def draw_caption(cv, t):
    for i, (a, b, wt) in enumerate(CAPS):
        nxt = CAPS[i + 1][0] if i + 1 < len(CAPS) else b + 0.4
        if not (a <= t < min(nxt, b + 0.5)): continue
        d = ImageDraw.Draw(cv); ws = [w for w, _ in wt]; widths = [d.textlength(w, font=CAP) for w in ws]; gap = 18
        lines, cur, cw = [], [], 0
        for k, w in enumerate(widths):
            if cur and cw + gap + w > 960: lines.append(cur); cur, cw = [], 0
            cur.append(k); cw += (gap if cw else 0) + w
        lines.append(cur); y = 1540 - (len(lines) - 1) * 44
        for ln in lines:
            lw = sum(widths[k] for k in ln) + gap * (len(ln) - 1); x = (W - lw) / 2
            for k in ln:
                w, tw = wt[k]
                if t >= tw:
                    u = ease((t - tw) / 0.12); key = w.strip("¿?¡!.,:…").lower() in KEYS
                    d.text((x, y + int(10 * (1 - u))), w, font=CAP, fill=(GOLD if key else CREAM) + (int(255 * u),), stroke_width=6, stroke_fill=(15, 6, 4, int(230 * u)))
                x += widths[k] + gap
            y += 88
        break

def chip(text, font, bg=CREAM, fg=DARK, angle=0, pad=(32, 18)):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, t_, r, b = d0.textbbox((0, 0), text, font=font)
    im = Image.new("RGBA", (r - l + 2 * pad[0], b - t_ + 2 * pad[1]), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=22, fill=bg + (255,))
    d.text((pad[0] - l, pad[1] - t_), text, font=font, fill=fg)
    return im.rotate(angle, resample=Image.BICUBIC, expand=True) if angle else im
def paste(cv, im, x, y, k):
    if k <= 0: return
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda p: int(p * k))); cv.alpha_composite(im, (int(x), int(y)))

STICKER = chip("Prevención · diabetes", STICK, angle=3)
def hook(cv, t):
    if t > 4.6: return
    k = ease(t / 0.25) * (1 - ease((t - 4.2) / 0.4)); a = int(255 * k); d = ImageDraw.Draw(cv)
    d.text((W / 2, 300), "TU SANGRE PUEDE", font=HOOK1, fill=CREAM + (a,), anchor="mm", stroke_width=5, stroke_fill=(15, 6, 4, a))
    d.text((W / 2, 395), "ESTAR DULCE…", font=HOOK1, fill=CREAM + (a,), anchor="mm", stroke_width=5, stroke_fill=(15, 6, 4, a))
    u = 1 + 0.25 * (1 - ease((t - 0.9) / 0.3))
    if t > 0.9:
        d.text((W / 2, 520), "Y NO SENTIR NADA", font=F("Anton-Regular.ttf", int(118 * u)), fill=GOLD + (a,), anchor="mm", stroke_width=6, stroke_fill=(15, 6, 4, a))
    if t > 1.3: paste(cv, STICKER, (W - STICKER.width) / 2, 630, ease((t - 1.3) / 0.25) * k)

TAGS = [(8.67, 11.5, "GLUCOSA = ENERGÍA"), (15.48, 21.1, "INSULINA = LA LLAVE"), (21.19, 25.6, "LA PUERTA NO ABRE"),
        (29.99, 33.3, "¿SABES TU NÚMERO?"), (42.79, 46.9, "CASI 1 DE CADA 5 ADULTOS"), (46.99, 49.9, "1 DE CADA 3 NO LO SABE"),
        (58.07, 66.1, "LA PREDIABETES NO AVISA"), (66.20, 73.8, "HAZTE EL ANÁLISIS")]
TAGIMG = {txt: chip(txt, F("Anton-Regular.ttf", 76), angle=-2) for _, _, txt in TAGS}
def tags(cv, t):
    for a, b, txt in TAGS:
        if a <= t < b:
            k = ease((t - a) / 0.3) * (1 - ease((t - (b - 0.3)) / 0.3)); s = TAGIMG[txt]
            paste(cv, s, (W - s.width) / 2, 330 - 30 * (1 - k), k)

SMALL = F("Oswald.ttf", 30, 500)
def footnote(cv, t, text, a, b):
    if a <= t < b:
        k = ease((t - a) / 0.3) * (1 - ease((t - (b - 0.3)) / 0.3)); d = ImageDraw.Draw(cv)
        d.text((W / 2, 1840), text, font=SMALL, fill=(235, 225, 210, int(200 * k)), anchor="mm")

CARD_F, CARD_S = F("Anton-Regular.ttf", 96), F("LilitaOne-Regular.ttf", 52)
CARDS = [(34.33, "<100", "NORMAL", GREEN), (36.25, "100–125", "PREDIABETES", AMBER), (39.70, "126+", "DIABETES", RED)]
def cards(cv, t):
    if not (33.4 <= t < 42.79): return
    kk = 1 - ease((t - 42.4) / 0.35); d = ImageDraw.Draw(cv)
    k0 = ease((t - 33.4) / 0.3) * kk
    d.text((W / 2, 420), "GLUCOSA EN AYUNAS", font=F("Anton-Regular.ttf", 84), fill=CREAM + (int(255 * k0),), anchor="mm", stroke_width=5, stroke_fill=(15, 6, 4, int(255 * k0)))
    d.text((W / 2, 495), "(mg/dL)", font=CARD_S, fill=CREAM + (int(220 * k0),), anchor="mm")
    for i, (a, num, lab, col) in enumerate(CARDS):
        if t < a: continue
        k = ease((t - a) / 0.3) * kk; y = 600 + i * 230 + int(40 * (1 - k))
        box = Image.new("RGBA", (860, 190), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, 859, 189], radius=34, fill=(20, 12, 10, 215), outline=col + (255,), width=6)
        bd.text((60, 95), num, font=CARD_F, fill=col, anchor="lm"); bd.text((800, 95), lab, font=CARD_S, fill=CREAM, anchor="rm")
        paste(cv, box, (W - 860) / 2, y, k)
    footnote(cv, t, "Criterio de la Asociación Americana de Diabetes. El diagnóstico lo confirma tu médico.", 33.6, 42.79)

SIGNS = [(49.99, "💧", "MUCHA SED"), (52.25, "", "ORINAR SEGUIDO"), (53.42, "", "CANSANCIO"), (54.87, "", "VISIÓN BORROSA"),
         (55.99, "", "HERIDAS QUE TARDAN EN SANAR")]
SIGN_IMG = [chip(f"{i + 1}. {txt}", F("LilitaOne-Regular.ttf", 50), bg=(20, 12, 10), fg=CREAM, pad=(28, 14)) for i, (_, _, txt) in enumerate(SIGNS)]
def signs(cv, t):
    if not (49.99 <= t < 58.07): return
    kk = 1 - ease((t - 57.7) / 0.35); d = ImageDraw.Draw(cv); k0 = ease((t - 49.99) / 0.3) * kk
    s = chip("5 SEÑALES DE ALERTA", F("Anton-Regular.ttf", 76), angle=-2); paste(cv, s, (W - s.width) / 2, 300, k0)
    for i, (a, _, _) in enumerate(SIGNS):
        if t < a: continue
        k = ease((t - a) / 0.25) * kk; im = SIGN_IMG[i]
        paste(cv, im, W - im.width - 50 + int(60 * (1 - k)), 780 + i * 110, k)

def frame(bgarr, t):
    a = bgarr.astype(np.float32) * SHADE
    cv = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    hook(cv, t); tags(cv, t); cards(cv, t); signs(cv, t)
    footnote(cv, t, "Fuente: ENSANUT 2022, Salud Pública de México.", 42.9, 49.99)
    footnote(cv, t, "Información general. No sustituye la consulta médica.", 66.2, END)
    draw_caption(cv, t)
    out = cv.convert("RGB")
    if t < 0.2: out = Image.blend(Image.new("RGB", (W, H)), out, ease(t / 0.2))
    return out

if __name__ == "__main__":
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", BG, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    o = sys.stdout.buffer
    for n in range(int(END * FPS)):
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        o.write(frame(np.frombuffer(buf, np.uint8).reshape(H, W, 3), n / FPS).tobytes())
