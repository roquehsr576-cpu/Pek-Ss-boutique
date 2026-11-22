import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import font, text_layer, cover
from PIL import Image, ImageDraw, ImageFilter, ImageFont
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; O = R + 'posts/out/'; FD = R + 'fonts_dl/'
import os; os.makedirs(O, exist_ok=True)
PW, PH = 1080, 1350
def KB(s): return ImageFont.truetype(FD + 'fontsource-kalam-5.3.0/files/kalam-latin-700-normal.woff', s)
def KR(s): return ImageFont.truetype(FD + 'fontsource-kalam-5.3.0/files/kalam-latin-400-normal.woff', s)
IB = lambda s: font('Inter-ExtraBold.otf', s); IM = lambda s: font('Inter-Bold.otf', s)
GOLD = (255, 214, 90); AQUA = (120, 220, 255); WHITE = (255, 255, 255)
logo = Image.open(R + 'clip/dxn-logo.png').convert('RGBA').resize((90, 87), Image.LANCZOS)
def badge():
    b = Image.new('RGBA', (110, 107)); m = Image.new('L', b.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 109, 106), 18, fill=235)
    b.paste((255, 255, 255, 255), (0, 0), m); b.alpha_composite(logo, (10, 10)); return b
BADGE = badge()
def wrap(txt, f, maxw):
    d = ImageDraw.Draw(Image.new('L', (1, 1))); out = []
    for para in txt.split('\n'):
        line = ''
        for w in para.split():
            t = (line + ' ' + w).strip()
            if d.textlength(t, font=f) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out
def draw_block(img, lines_spec, y, align='center'):
    """lines_spec: list of (text, font, color). returns y end"""
    d = ImageDraw.Draw(img)
    for txt, f, col in lines_spec:
        for ln in wrap(txt, f, PW - 140):
            w = d.textlength(ln, font=f); x = (PW - w) / 2 if align == 'center' else 70
            d.text((x, y), ln, font=f, fill=col, stroke_width=max(2, f.size // 18), stroke_fill=(0, 0, 0))
            y += int(f.size * 1.18)
        y += int(f.size * 0.25)
    return y
def photo_bg(path, darken=(0.15, 0.75), focus=0.5):
    im = Image.open(path).convert('RGB'); bg = cover(im, PW, PH).convert('RGBA')
    g = Image.new('L', (1, PH)); [g.putpixel((0, y), int(255 * (darken[0] + (darken[1] - darken[0]) * abs(y / PH - focus) * 2))) for y in range(PH)]
    sh = Image.new('RGBA', (PW, PH), (0, 0, 0, 255)); sh.putalpha(g.resize((PW, PH))); bg.alpha_composite(sh); return bg
def board():
    rng = np.random.default_rng(5); n = np.asarray(Image.fromarray(np.clip(rng.normal(0, 1, (PH // 4, PW // 4)) * 6 + 128, 0, 255).astype(np.uint8)).resize((PW, PH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3)), np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW]; vig = 1 - 0.4 * (((xx - PW / 2) / (PW / 1.3)) ** 2 + ((yy - PH / 2) / (PH / 1.3)) ** 2)
    b = np.zeros((PH, PW, 3), np.float32); b[:] = (30, 32, 34); b *= (1 + 0.22 * (n - 128)[..., None] / 128) * vig[..., None]
    return Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)).convert('RGBA')
def chalk(img, path, size, cx, cy):
    d = Image.open(path).convert('L'); r = size / max(d.size); d = d.resize((int(d.width * r), int(d.height * r)), Image.LANCZOS)
    a = d.point(lambda v: 0 if v < 70 else min(255, int(v * 1.05))); layer = Image.new('RGBA', d.size, (238, 238, 230, 255)); layer.putalpha(a)
    img.alpha_composite(layer, (int(cx - d.width / 2), int(cy - d.height / 2)))
def finish(img, name, foot=False):
    if foot: img.alpha_composite(BADGE, (PW - 140, 30))
    img.convert('RGB').save(O + name, quality=93); print('ok', name)
def prod(img, path, h, cx, cy):
    p = Image.open(path).convert('RGBA'); r = h / p.height; p = p.resize((int(p.width * r), h), Image.LANCZOS)
    sh = Image.new('RGBA', (p.width + 60, p.height + 60)); m = p.split()[-1].point(lambda v: int(v * 0.5)); sh.paste((0, 0, 0, 255), (30, 40), m); sh = sh.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(sh, (int(cx - p.width / 2 - 30), int(cy - p.height / 2 - 30))); img.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))
# 1 desierto
im = photo_bg(R + 'gansos/g0_desierto.png', (0.1, 0.8), 0.55)
draw_block(im, [('Nadie encuentra su paraíso…', IB(78), WHITE), ('sin antes cruzar su desierto.', IB(78), GOLD)], 120); draw_block(im, [('Si hoy estás en el desierto, sigue caminando. ', IM(40), WHITE)], 1180); finish(im, '01_paraiso_desierto.jpg')
# 2 filo (pizarra)
im = board(); chalk(im, R + 'pizarra/d1.png', 760, PW / 2, 760)
draw_block(im, [('No le faltaba esfuerzo.', KB(86), WHITE), ('Le faltaba FILO.', KB(110), GOLD)], 90); draw_block(im, [('¿Cuándo afilaste tu hacha por última vez? ', KR(48), WHITE)], 1190); finish(im, '02_le_faltaba_filo.jpg')
# 3 gansos
im = photo_bg(R + 'gansos/g4_gansos.png', (0.05, 0.75), 0.35)
draw_block(im, [('Un ganso solo', IB(84), WHITE), ('no llega lejos.', IB(84), GOLD)], 110); draw_block(im, [('Vuelan en V, se turnan el frente y se cuidan.', IM(44), WHITE), ('Nadie compite. Así se gana. ', IM(44), WHITE)], 1060); finish(im, '03_un_ganso_solo.jpg')
# 4 equipo DXN
im = photo_bg(R + 'clip/fr/e3/0120.jpg', (0.05, 0.85), 0.2)
draw_block(im, [('Un equipo sólido', IB(80), WHITE), ('vale más que cualquier cosa.', IB(64), GOLD)], 980); finish(im, '04_equipo_solido.jpg')
# 5 huesos 31%
im = Image.new('RGBA', (PW, PH)); d = ImageDraw.Draw(im)
for y in range(PH): d.line((0, y, PW, y), fill=(int(6 + 10 * y / PH), int(60 + 50 * y / PH), int(120 + 60 * y / PH), 255))
sp = cover(Image.open(R + 'agua/fr/splash/0150.jpg').convert('RGB'), PW, 700).convert('RGBA'); m = Image.new('L', sp.size, 0); ImageDraw.Draw(m).rectangle((0, 0, PW, 700), fill=170); sp.putalpha(m); im.alpha_composite(sp, (0, 650))
draw_block(im, [('Tus huesos son', IB(80), WHITE), ('31% AGUA', IB(170), AQUA)], 140); draw_block(im, [('Tus pulmones ~83% · tu cerebro ~73%', IM(44), WHITE), ('El agua no se guarda: se repone. ', IM(44), WHITE)], 1050)
ImageDraw.Draw(im).text((70, 1290), 'Fuente: USGS', font=IM(26), fill=(220, 235, 255)); finish(im, '05_huesos_31_agua.jpg')
# 6 mexicas espirulina
im = photo_bg(R + 'posts/src/mexicas.png', (0.05, 0.8), 0.3)
draw_block(im, [('Hace 500 años', IB(72), WHITE), ('los mexicas ya la sacaban', IB(64), WHITE), ('del lago de Texcoco.', IB(64), GOLD)], 90); draw_block(im, [('Hoy la conocemos como espirulina. ', IM(40), WHITE)], 1270); finish(im, '06_mexicas_espirulina.jpg')
# 7 noni
im = photo_bg(R + 'posts/src/noni_mujer.png', (0.05, 0.85), 0.25)
draw_block(im, [('¿Te animarías a probar', IB(70), WHITE), ('la fruta que huele a QUESO? ', IB(70), GOLD)], 90); draw_block(im, [('Se llama noni.', IM(48), WHITE)], 1260); finish(im, '07_fruta_que_huele_a_queso.jpg')
# 8 cafe preparacion
im = photo_bg(R + 'clip/fr/e2/0100.jpg', (0.05, 0.8), 0.6)
draw_block(im, [('El éxito ama', IB(90), WHITE), ('la preparación.', IB(90), GOLD)], 90); draw_block(im, [('Mi momento: 10 minutos de lectura', IM(44), WHITE), ('con mi café de Ganoderma. ', IM(44), WHITE)], 1130); finish(im, '08_exito_ama_preparacion.jpg')
# carrusel hacha
os.makedirs(O + 'carrusel_hacha', exist_ok=True)
im = board(); chalk(im, R + 'pizarra/lenador.png', 700, PW / 2, 820)
draw_block(im, [('5 formas de', KB(90), WHITE), ('AFILAR TU HACHA', KB(110), GOLD)], 70); draw_block(im, [('Desliza para ver más', KR(52), WHITE)], 1220); finish(im, 'carrusel_hacha/1.jpg')
for i, (ic, t1, t2) in enumerate([('icon2', '10 min al día de aprender', 'algo de lo tuyo: un libro, un video, una lección.'), ('icon1', 'Pregunta a quien ya lo logró', 'No lo hagas a tu manera: hazlo como lo hacen los grandes.'),
                                  ('icon3', 'Si no funciona, no lo repitas igual', 'Resultados diferentes piden información diferente.'), ('icon4', 'Descansa', 'Hasta la mejor hacha se desgasta si nunca para.'),
                                  ('icon5', 'Rodéate de gente que te afile', 'Un buen equipo te hace mejor.')]):
    im = board(); draw_block(im, [(str(i + 2 - 1), KB(220), GOLD)], 60); chalk(im, R + f'pizarra/{ic}.png', 420, PW / 2, 600)
    draw_block(im, [(t1, KB(84), WHITE), (t2, KR(56), (220, 220, 210))], 860); finish(im, f'carrusel_hacha/{i + 2}.jpg')
im = board(); chalk(im, R + 'pizarra/d7.png', 560, PW / 2, 620)
draw_block(im, [('¿Cuál vas a empezar hoy?', KB(84), GOLD)], 90); draw_block(im, [(' Guárdalo para no olvidarlo', KR(58), WHITE), (' Mándalo a quien corta con el hacha sin filo', KR(50), WHITE)], 960); finish(im, 'carrusel_hacha/7.jpg')
# carrusel agua
os.makedirs(O + 'carrusel_agua', exist_ok=True)
def blue():
    im = Image.new('RGBA', (PW, PH)); d = ImageDraw.Draw(im)
    for y in range(PH): d.line((0, y, PW, y), fill=(int(6 + 10 * y / PH), int(60 + 50 * y / PH), int(120 + 60 * y / PH), 255))
    return im
im = blue(); sp = cover(Image.open(R + 'agua/fr/splash/0200.jpg').convert('RGB'), PW, PH).convert('RGBA'); sp.putalpha(120); im.alpha_composite(sp)
draw_block(im, [('¿Cuánta agua hay', IB(84), WHITE), ('en tu cuerpo?', IB(84), AQUA)], 380); draw_block(im, [('La respuesta te va a sorprender ', IM(46), WHITE)], 1150); finish(im, 'carrusel_agua/1.jpg')
im = blue(); y = draw_block(im, [('Agua en cada parte de tu cuerpo', IB(60), WHITE)], 90); d = ImageDraw.Draw(im)
for j, (nm, pc) in enumerate([('Pulmones', 83), ('Músculos y riñones', 79), ('Cerebro y corazón', 73), ('Recién nacido', 78), ('Huesos', 31)]):
    yy = 300 + j * 180; d.rounded_rectangle((70, yy, PW - 70, yy + 150), 30, fill=(8, 25, 45, 210)); d.text((110, yy + 20), nm, font=IM(48), fill=WHITE)
    d.rounded_rectangle((110, yy + 95, 760, yy + 125), 15, fill=(255, 255, 255, 60)); d.rounded_rectangle((110, yy + 95, 110 + 650 * pc / 100, yy + 125), 15, fill=(80, 200, 255, 255)); d.text((800, yy + 55), f'{pc}%', font=IB(70), fill=AQUA)
d.text((70, 1290), 'Fuente: USGS · Mitchell et al., 1945', font=IM(26), fill=(220, 235, 255)); finish(im, 'carrusel_agua/2.jpg')
im = blue(); draw_block(im, [('3 hábitos sencillos', IB(76), AQUA)], 120); draw_block(im, [('1. Un vaso de agua al despertar', IM(56), WHITE), ('2. Tu botella siempre contigo', IM(56), WHITE), ('3. Con calor o más movimiento, un poco más', IM(56), WHITE)], 420)
draw_block(im, [('El agua no se guarda: se repone. ', IB(48), AQUA)], 1150); finish(im, 'carrusel_agua/3.jpg')
im = blue(); draw_block(im, [('El dato que', IB(80), WHITE), ('casi nadie sabe:', IB(80), AQUA)], 140); draw_block(im, [('El agua es la única sustancia natural en la Tierra que existe en sus 3 estados:', IM(52), WHITE), ('sólida · líquida · gas', IB(60), AQUA)], 560)
draw_block(im, [('¿Cuántos vasos llevas hoy? ', IM(50), WHITE)], 1150); d = ImageDraw.Draw(im); d.text((70, 1290), 'Fuente: USGS', font=IM(26), fill=(220, 235, 255)); finish(im, 'carrusel_agua/4.jpg')
