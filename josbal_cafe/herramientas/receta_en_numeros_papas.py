# Reel "La receta en números": papas a la francesa (doble fritura). Usa los ayudantes del reel de goteo.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import receta_en_numeros_goteo as R
from receta_en_numeros_goteo import W, H, FPS, CREAM, CARAMEL, RED, DIM, ANTON, OSW, clamp, prog, lerp, col, ctext, chip

DUR = 53.5
GOLD = (222, 145, 55)

R.PHRASES = [
    (0.05, 4.38, "¿Sabías que las papas a la francesa más crujientes se fríen DOS veces?"),
    (4.76, 5.24, "Primero,"),
    (5.35, 10.15, "se cortan de 1 centímetro y se remojan en agua fría al menos 30 minutos,"),
    (10.27, 11.32, "para quitarles almidón."),
    (11.59, 13.38, "Luego se secan muy bien."),
    (13.98, 14.78, "Primera fritura:"),
    (15.06, 16.40, "160 grados,"),
    (16.51, 17.73, "unos 5 minutos."),
    (18.06, 19.07, "Se cuecen por dentro,"),
    (19.19, 19.87, "sin dorarse."),
    (20.27, 21.22, "Se dejan reposar."),
    (21.67, 22.55, "Segunda fritura:"),
    (22.83, 24.10, "180 grados,"),
    (24.20, 25.50, "2 a 3 minutos."),
    (25.63, 27.26, "Ahí se ponen crujientes."),
    (27.64, 28.16, "La regla:"),
    (28.49, 29.31, "primero cocer,"),
    (29.53, 30.24, "luego dorar."),
    (30.69, 31.20, "El error:"),
    (31.62, 34.52, "freírlas una sola vez con el aceite muy caliente."),
    (34.94, 36.10, "Quedan doradas por fuera..."),
    (36.26, 37.35, "y crudas por dentro."),
    (37.73, 38.73, "¿Salen grasosas?"),
    (39.10, 40.22, "El aceite está frío."),
    (40.58, 43.40, "Si echas muchas papas a la vez, la temperatura baja."),
    (43.84, 46.17, "Fríe en tandas pequeñas y usa termómetro."),
    (46.58, 50.26, "1 centímetro, 160 y luego 180 grados."),
    (50.65, 51.84, "¿Tú cómo las haces en casa?"),
]
R.KEYS = {"dos", "1", "centímetro", "30", "minutos", "almidón", "secan", "160", "5", "dentro", "reposar", "180",
          "2", "3", "crujientes", "cocer", "dorar", "error", "sola", "caliente", "crudas", "grasosas", "frío",
          "baja", "tandas", "pequeñas", "termómetro"}
R.WORDS = [(R.word_times(a, b, s), a, b) for a, b, s in R.PHRASES]

def papa(d, x, y, w, h, c, k=1.0, angle=0):
    # bastón de papa, horizontal (angle=0) o vertical (angle=90)
    if angle:
        d.rounded_rectangle((x - h / 2, y - w / 2, x + h / 2, y + w / 2), radius=h / 3, fill=col(c, k))
    else:
        d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), radius=h / 3, fill=col(c, k))

def olla(d, cx, cy, k):
    d.line((cx - 260, cy - 120, cx - 230, cy + 160), fill=col(CREAM, k), width=8)
    d.line((cx + 260, cy - 120, cx + 230, cy + 160), fill=col(CREAM, k), width=8)
    d.line((cx - 230, cy + 160, cx + 230, cy + 160), fill=col(CREAM, k), width=8)
    pts = [(cx - 250 + i * 10, cy - 20 + 10 * np.sin(i / 3)) for i in range(51)]
    d.line(pts, fill=col(GOLD, k), width=6)

def termometro(d, x, top, bot, v, c, k, labels=()):
    # v: 0..1 nivel; tubo vertical con bulbo
    d.rounded_rectangle((x - 28, top, x + 28, bot), radius=28, outline=col(CREAM, k), width=6)
    d.ellipse((x - 52, bot - 30, x + 52, bot + 74), outline=col(CREAM, k), width=6)
    d.ellipse((x - 36, bot - 14, x + 36, bot + 58), fill=col(c, k))
    lvl = bot - (bot - top - 30) * v
    d.rounded_rectangle((x - 14, lvl, x + 14, bot + 10), radius=14, fill=col(c, k))
    for lab, lv in labels:
        y = bot - (bot - top - 30) * lv
        d.line((x + 40, y, x + 70, y), fill=col(CREAM, k), width=4)
        d.text((x + 85, y - 30), lab, font=OSW[52], fill=col(CREAM, k))

def deg(v):
    # 0..1 del termómetro = 100..200 °C
    return (v - 100) / 100

def scene(d, t):
    cx = W / 2
    # 1. Gancho: la papa entra dos veces al aceite
    if t < 4.6:
        k = prog(t, 0.0, 0.3)
        olla(d, cx, 1080, k)
        dip = 0.5 - 0.5 * np.cos(min(t, 3.6) / 1.8 * 2 * np.pi)
        y = lerp(820, 1080, dip)
        for i in range(3):
            papa(d, cx - 80 + i * 80, y, 260, 46, CREAM if t < 2.2 else GOLD, k, angle=90)
        n = 1 if t < 2.2 else 2
        ctext(d, cx, 1330, f"×{n}", ANTON[300], col(RED if n == 2 else CREAM, k))
        return
    # 2. Corte de 1 cm, remojo 30 min, quitar almidón, secar
    if t < 13.85:
        k = prog(t, 4.7)
        papa(d, cx, 720, 640, 110, CREAM, k)
        if t > 6.0:
            kk = prog(t, 6.0)
            d.line((cx + 360, 665, cx + 360, 775), fill=col(RED, kk), width=6)
            d.line((cx + 340, 665, cx + 380, 665), fill=col(RED, kk), width=6)
            d.line((cx + 340, 775, cx + 380, 775), fill=col(RED, kk), width=6)
            ctext(d, cx + 360, 790, "1 cm", ANTON[88], col(RED, kk))
        if t > 7.4:
            kk = prog(t, 7.4)
            d.rounded_rectangle((170, 1010, 910, 1400), radius=40, outline=col(CREAM, kk), width=8)
            d.rectangle((182, 1110, 898, 1388), fill=col((40, 60, 70), kk))
            for i in range(6):
                papa(d, 290 + i * 100, 1250, 220, 40, CREAM, kk, angle=90)
            mins = int(round(30 * clamp((t - 8.2) / 1.6)))
            ctext(d, cx, 1440, f"{mins} min en agua fría", ANTON[88], col(CARAMEL, kk))
        if 10.2 < t < 11.6:
            rng = np.random.default_rng(3)
            for i in range(30):
                x0, y0 = rng.uniform(220, 860), rng.uniform(1150, 1350)
                y1 = y0 - (t - 10.2) * rng.uniform(150, 320)
                r = rng.uniform(5, 11)
                d.ellipse((x0 - r, y1 - r, x0 + r, y1 + r), fill=col(CREAM, 0.8))
            ctext(d, cx, 860, "ALMIDÓN", ANTON[88], col(CREAM, prog(t, 10.3, 0.3)))
        if t > 11.6:
            ctext(d, cx, 860, "SECAR MUY BIEN", ANTON[88], col(RED, prog(t, 11.6, 0.3)))
        return
    # 3. Primera fritura: 160 °C, 5 min, papas pálidas, reposo
    if t < 21.55:
        k = prog(t, 13.95)
        v = deg(lerp(100, 160, prog(t, 15.0, 0.9)))
        termometro(d, 180, 640, 1380, v, CARAMEL, k, [("160 °C", deg(160))] if t > 15.6 else ())
        ctext(d, 720, 620, "1ª FRITURA", ANTON[88], col(CREAM, k))
        if t > 16.5:
            m = int(round(5 * clamp((t - 16.5) / 1.0)))
            ctext(d, 720, 760, f"{m} min", ANTON[150], col(CARAMEL, prog(t, 16.5, 0.3)))
        for i in range(5):
            papa(d, 590 + i * 65, 1180, 280, 42, CREAM, prog(t, 18.0 + i * 0.1, 0.3), angle=90)
        if t > 19.2:
            ctext(d, 720, 1360, "SIN DORAR", ANTON[72], col(CREAM, prog(t, 19.2, 0.3)))
        if t > 20.3:
            ctext(d, 720, 1460, "REPOSO", ANTON[72], col(CARAMEL, prog(t, 20.3, 0.3)))
        return
    # 4. Segunda fritura: 180 °C, 2 a 3 min, se doran
    if t < 27.5:
        k = prog(t, 21.6)
        v = deg(lerp(160, 180, prog(t, 22.8, 0.8)))
        termometro(d, 180, 640, 1380, v, RED, k, [("180 °C", deg(180))] if t > 23.2 else ())
        ctext(d, 720, 620, "2ª FRITURA", ANTON[88], col(CREAM, k))
        if t > 24.2:
            ctext(d, 720, 760, "2 a 3 min", ANTON[110], col(CARAMEL, prog(t, 24.2, 0.3)))
        g = prog(t, 24.5, 2.0)
        c = tuple(int(lerp(a, b, g)) for a, b in zip(CREAM, GOLD))
        for i in range(5):
            papa(d, 590 + i * 65, 1180, 280, 42, c, k, angle=90)
        if t > 25.7:
            ctext(d, 720, 1360, "CRUJIENTES", ANTON[88], col(GOLD, prog(t, 25.7, 0.3)))
        return
    # 5. La regla
    if t < 30.6:
        k = prog(t, 27.6, 0.35)
        ctext(d, cx, 760, "160° → 180°", ANTON[150], col(CREAM, k))
        if t > 28.4:
            ctext(d, cx, 1000, "COCER", ANTON[110], col(CARAMEL, prog(t, 28.4, 0.3)))
        if t > 29.4:
            ctext(d, cx, 1150, "↓", ANTON[88], col(CREAM, prog(t, 29.4, 0.3)))
            ctext(d, cx, 1260, "DORAR", ANTON[110], col(GOLD, prog(t, 29.4, 0.3)))
        return
    # 6. El error: una sola fritura muy caliente -> crudas por dentro
    if t < 37.6:
        k = prog(t, 30.65)
        ctext(d, cx, 620, "1 SOLA FRITURA", ANTON[88], col(CREAM, k))
        if t > 32.6:
            ctext(d, cx, 740, "ACEITE MUY CALIENTE", OSW[60], col(RED, prog(t, 32.6, 0.3)))
        # corte transversal de una papa
        if t > 34.8:
            kk = prog(t, 34.8)
            d.rounded_rectangle((300, 900, 780, 1380), radius=60, fill=col(GOLD, kk))
            kr = prog(t, 36.2)
            d.rounded_rectangle((360, 960, 720, 1320), radius=40, fill=col((235, 225, 205), kk))
            if kr > 0:
                d.rounded_rectangle((360, 960, 720, 1320), radius=40, outline=col(RED, kr), width=10)
                ctext(d, cx, 1090, "CRUDO", ANTON[110], col(RED, kr))
            ctext(d, cx, 1420, "dorada por fuera", OSW[52], col(GOLD, kk))
        return
    # 7. Grasosas: la temperatura cae con muchas papas
    if t < 43.75:
        k = prog(t, 37.7)
        x0, x1, y0, y1 = 150, 930, 680, 1300
        d.line((x0, y0, x0, y1), fill=col(CREAM, k), width=5)
        d.line((x0, y1, x1, y1), fill=col(CREAM, k), width=5)
        zy = lerp(y0, y1, 0.55)
        d.rectangle((x0 + 4, zy, x1, y1 - 4), fill=col((70, 22, 18), k))
        ctext(d, x1 - 150, y1 - 80, "ACEITE FRÍO", OSW[44], col(RED, k))
        d.text((x0 + 20, y0 + 10), "180 °C", font=OSW[44], fill=col(CREAM, k))
        drop = prog(t, 40.8, 1.6)
        pts = []
        for i in range(61):
            u = i / 60
            yy = lerp(y0 + 60, y0 + 60, 0)
            if u > 0.4:
                yy = y0 + 60 + (zy + 140 - y0 - 60) * drop * min(1, (u - 0.4) / 0.25)
            pts.append((lerp(x0, x1, u * prog(t, 37.8, 2.0)), yy))
        d.line(pts, fill=RED if drop > 0.5 else CARAMEL, width=10)
        if t > 40.8:
            for i in range(9):
                papa(d, 420 + (i % 5) * 70, 560 + (i // 5) * 30 + 200 * prog(t, 40.8 + i * 0.05, 0.6), 120, 30, CREAM, prog(t, 40.8, 0.2), angle=90)
        ctext(d, cx, 1360, "GRASOSAS", ANTON[110], col(RED, prog(t, 37.9, 0.3)))
        return
    # 8. Solución: tandas pequeñas + termómetro
    if t < 46.45:
        k = prog(t, 43.85)
        for j, (lab, n, c) in enumerate((("TANDA CHICA", 3, GOLD), ("TANDA GRANDE", 9, RED))):
            x = 290 + j * 500
            for i in range(n):
                papa(d, x - 120 + (i % 3) * 120, 880 + (i // 3) * 70, 90, 34, CREAM, k)
            ctext(d, x, 1160, lab, OSW[52], col(CREAM, k))
            ctext(d, x, 1240, "SÍ" if j == 0 else "NO", ANTON[110], col(c, k))
        if t > 45.0:
            termometro(d, cx, 1450, 1640, 0.8, RED, prog(t, 45.0, 0.3))
        return
    # 9. Tarjeta resumen
    k = prog(t, 46.5)
    d.rounded_rectangle((110, 560, 970, 1650), radius=40, outline=col(CARAMEL, k), width=5)
    ctext(d, cx, 610, "PAPAS A LA FRANCESA", OSW[52], col(CARAMEL, k))
    chip(d, cx, 820, "1 cm", ANTON[110], CREAM, prog(t, 46.6))
    chip(d, cx, 1010, "1ª  160 °C", ANTON[88], CREAM, prog(t, 47.6))
    chip(d, cx, 1180, "2ª  180 °C", ANTON[88], GOLD, prog(t, 48.6))
    kb = prog(t, 49.3)
    if kb > 0:
        termometro(d, cx - 160, 1320, 1500, 0.8, RED, kb)
        d.text((cx - 70, 1430), "termómetro", font=OSW[60], fill=col(CREAM, kb))

R.scene = scene

if __name__ == "__main__":
    if len(sys.argv) > 4:
        Image.fromarray(R.frame(float(sys.argv[4]))).save(sys.argv[5])
        sys.exit()
    start, end = float(sys.argv[2]), float(sys.argv[3])
    for i in range(int(start * FPS), int(end * FPS)):
        sys.stdout.buffer.write(R.frame(i / FPS).tobytes())
