# Gancho nuevo de los primeros segundos: el texto completo se ve desde el primer cuadro.
# Uso: hook.py <fonts> <cafe|papas> <duración> [segundo salida.png]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import receta_en_numeros_goteo as R
from receta_en_numeros_goteo import W, H, FPS, CREAM, CARAMEL, RED, ANTON, clamp, prog, lerp, col, ctext

KIND, DUR = sys.argv[2], float(sys.argv[3])
GOLD = (222, 145, 55)

TITLES = {
    "cafe": [("¿TU CAFÉ SALE", CREAM), ("AGUADO", RED), ("O MUY FUERTE?", CREAM)],
    "papas": [("¿TUS PAPAS", CREAM), ("SALEN", CREAM), ("AGUADAS?", RED)],
}

def title(d, t):
    y = 230
    for i, (s, c) in enumerate(TITLES[KIND]):
        f = ANTON[150] if c == RED else ANTON[110]
        # entra de golpe; la palabra roja late un poco
        pulse = 1.0 if c != RED else 0.85 + 0.15 * abs(np.sin(t * 4))
        ctext(d, W / 2, y, s, f, col(c, pulse))
        y += f.size + 30

def taza(d, cx, top, level, c_liq, k=1.0):
    bot, l, r = top + 360, cx - 150, cx + 150
    d.line((l, top, l + 30, bot), fill=col(CREAM, k), width=8)
    d.line((r, top, r - 30, bot), fill=col(CREAM, k), width=8)
    d.line((l + 30, bot, r - 30, bot), fill=col(CREAM, k), width=8)
    d.arc((r - 40, top + 80, r + 90, top + 250), -90, 90, fill=col(CREAM, k), width=8)
    wy = bot - (bot - top - 40) * level
    d.polygon((l + 30 * (wy - top) / (bot - top) + 8, wy, r - 30 * (wy - top) / (bot - top) - 8, wy,
               r - 38, bot - 8, l + 38, bot - 8), fill=c_liq)

def scene(d, t):
    title(d, t)
    if KIND == "cafe":
        # dos tazas: una clara (aguada) y una casi negra (muy fuerte); al final aparece el "1 número"
        taza(d, 300, 900, 0.8, (150, 110, 70))
        taza(d, 780, 900, 0.8, (45, 25, 15))
        ctext(d, 300, 1360, "AGUADO", R.OSW[52], CREAM)
        ctext(d, 780, 1360, "MUY FUERTE", R.OSW[52], CREAM)
        if t > DUR - 1.4:
            k = prog(t, DUR - 1.4, 0.3)
            ctext(d, W / 2, 1460, "1 SOLO NÚMERO", ANTON[110], col(RED, k))
    else:
        # bastones colgando de un tenedor, doblados hacia abajo como papas blandas
        d.line((280, 880, 800, 880), fill=CREAM, width=10)
        for i in range(5):
            x = 320 + i * 100
            bend = 110 + 10 * np.sin(t * 2.5 + i)
            u = np.linspace(0, 1, 20)
            pts = [(x + bend * v ** 2.2, 900 + 330 * v - 60 * v ** 3) for v in u]
            d.line(pts, fill=(225, 205, 160), width=46, joint="curve")
        if t > DUR - 1.6:
            k = prog(t, DUR - 1.6, 0.3)
            ctext(d, W / 2, 1460, "1 SOLA FRITURA", ANTON[110], col(RED, k))

R.scene = scene
R.WORDS = []  # el título reemplaza a los subtítulos en el gancho

if __name__ == "__main__":
    if len(sys.argv) > 4:
        Image.fromarray(R.frame(float(sys.argv[4]))).save(sys.argv[5])
        sys.exit()
    for i in range(int(round(DUR * FPS))):
        sys.stdout.buffer.write(R.frame(i / FPS).tobytes())
