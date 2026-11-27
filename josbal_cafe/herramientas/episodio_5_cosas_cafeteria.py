# Episodio "5 cosas que hace una cafetería y que no ves". Usa los ayudantes del reel de goteo.
# Uso: cafeteria.py <fonts> <inicio> <fin>   |   cafeteria.py <fonts> 0 0 <segundo> salida.png
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import receta_en_numeros_goteo as R
from receta_en_numeros_goteo import W, H, FPS, CREAM, CARAMEL, RED, DIM, ANTON, OSW, clamp, prog, lerp, col, ctext, chip

GOLD = (222, 145, 55)
HERE = os.path.dirname(os.path.abspath(__file__))
# Tramos de la voz (inicio, fin, texto), sacados con silencedetect
R.PHRASES = [tuple(p) for p in json.load(open(os.path.join(HERE, "frases.json")))]
R.KEYS = {"basura", "varios", "molienda", "prueba", "25", "30", "segundos", "muele", "aroma", "minutos",
          "55", "65", "grados", "quema", "dulce", "filtrada", "sarro", "sabor", "detergente", "amargo",
          "ves", "pruebas", "uno", "dos", "tres", "cuatro", "cinco"}

def sec_start(word):
    return next(a for a, b, s in R.PHRASES if s.lower().startswith(word))

S = [sec_start(w) - 0.15 for w in ("uno", "dos", "tres", "cuatro", "cinco:")]
CLOSE = next(a for a, b, s in R.PHRASES if s.lower().startswith("cinco cosas")) - 0.15
HOOK_END = S[0]
R.WORDS = [(R.word_times(a, b, s), a, b) for a, b, s in R.PHRASES if a >= HOOK_END]  # el gancho usa título fijo

def numchip(d, n, t0, t):
    chip(d, W / 2, 600, f"{n}/5", ANTON[72], CARAMEL, prog(t, t0, 0.3))

def taza(d, cx, cy, s, c, w=7):
    d.line((cx - 70 * s, cy - 60 * s, cx - 55 * s, cy + 60 * s), fill=c, width=w)
    d.line((cx + 70 * s, cy - 60 * s, cx + 55 * s, cy + 60 * s), fill=c, width=w)
    d.line((cx - 55 * s, cy + 60 * s, cx + 55 * s, cy + 60 * s), fill=c, width=w)
    d.arc((cx + 50 * s, cy - 35 * s, cx + 105 * s, cy + 30 * s), -90, 90, fill=c, width=w)

def maquina(d, cx, cy, c, k):
    c = col(c, k)
    d.rounded_rectangle((cx - 260, cy - 260, cx + 260, cy - 120), radius=20, outline=c, width=8)
    d.line((cx - 230, cy - 120, cx - 230, cy + 220), fill=c, width=8)
    d.line((cx + 230, cy - 120, cx + 230, cy + 220), fill=c, width=8)
    d.line((cx - 260, cy + 220, cx + 260, cy + 220), fill=c, width=8)
    d.rounded_rectangle((cx - 70, cy - 120, cx + 70, cy - 70), radius=10, outline=c, width=7)  # grupo
    d.line((cx + 70, cy - 95, cx + 200, cy - 95), fill=c, width=10)  # mango del portafiltro

def hook(d, t):
    for i, (s, c, f) in enumerate((("ANTES DE TU CAFÉ…", CREAM, ANTON[110]), ("YA TIRARON", CREAM, ANTON[110]),
                                   ("VARIOS", RED, ANTON[150]))):
        ctext(d, W / 2, 230 + i * 150, s, f, c)
    # tazas que caen a un bote
    bx, by = W / 2, 1250
    d.line((bx - 200, by - 150, bx - 160, by + 220), fill=CREAM, width=8)
    d.line((bx + 200, by - 150, bx + 160, by + 220), fill=CREAM, width=8)
    d.line((bx - 160, by + 220, bx + 160, by + 220), fill=CREAM, width=8)
    d.line((bx - 230, by - 150, bx + 230, by - 150), fill=CREAM, width=10)
    for i in range(4):
        t0 = 0.4 + i * 0.9
        p = clamp((t - t0) / 0.7)
        if p <= 0:
            continue
        x = bx - 100 + i * 65
        y = lerp(800, by + 60, p * p)
        taza(d, x, y, 1.0, col(CARAMEL if p < 1 else DIM, 1.0), 7)

def s1(d, t):
    numchip(d, 1, S[0], t)
    ctext(d, W / 2, 700, "CALIBRAR LA MOLIENDA", OSW[60], col(CREAM, prog(t, S[0])))
    # cronómetro: aguja que gira y se detiene en la zona 25–30 s
    cx, cy, r = W / 2, 1150, 260
    k = prog(t, S[0] + 0.3)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col(CREAM, k), width=8)
    a0, a1 = -90 + 25 * 6, -90 + 30 * 6
    d.arc((cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22), a0, a1, fill=col(GOLD, k), width=36)
    secs = 27.5 * prog(t, S[0] + 2.0, 3.5)
    ang = np.radians(-90 + secs * 6)
    d.line((cx, cy, cx + (r - 40) * np.cos(ang), cy + (r - 40) * np.sin(ang)), fill=col(RED, k), width=10)
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=col(RED, k))
    if t > S[0] + 5.3:
        ctext(d, W / 2, 1460, "25 a 30 s", ANTON[110], col(GOLD, prog(t, S[0] + 5.3, 0.3)))

def s2(d, t):
    numchip(d, 2, S[1], t)
    ctext(d, W / 2, 700, "MOLER AL MOMENTO", OSW[60], col(CREAM, prog(t, S[1])))
    k = prog(t, S[1] + 0.2)
    rng = np.random.default_rng(5)
    g = prog(t, S[1] + 1.0, 1.2)  # granos -> molido
    for i in range(40):
        x, y = rng.uniform(220, 860), rng.uniform(880, 1120)
        r = lerp(24, 10, g)
        d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=col(CARAMEL, k))
    # aroma: barra que baja con los minutos
    a = prog(t, S[1] + 3.8, 2.0)
    if t > S[1] + 3.5:
        kk = prog(t, S[1] + 3.5, 0.3)
        d.text((180, 1210), "AROMA", font=OSW[52], fill=col(CREAM, kk))
        d.rounded_rectangle((180, 1290, 900, 1340), radius=25, outline=col(CREAM, kk), width=5)
        d.rounded_rectangle((186, 1296, lerp(894, 300, a), 1334), radius=19, fill=col(RED if a > 0.5 else GOLD, kk))
        ctext(d, W / 2, 1380, "en minutos", OSW[52], col(CREAM, kk))

def s3(d, t):
    numchip(d, 3, S[2], t)
    ctext(d, W / 2, 700, "LA LECHE", OSW[60], col(CREAM, prog(t, S[2])))
    x, top, bot = 330, 830, 1450
    k = prog(t, S[2] + 0.2)
    d.rounded_rectangle((x - 30, top, x + 30, bot), radius=30, outline=col(CREAM, k), width=6)
    d.ellipse((x - 55, bot - 30, x + 55, bot + 80), outline=col(CREAM, k), width=6)
    def ty(deg):
        return bot - (bot - top - 30) * (deg - 20) / 60
    d.rectangle((x - 26, ty(65), x + 26, ty(55)), fill=col((80, 60, 40), k))
    v = lerp(20, 60, prog(t, S[2] + 1.0, 1.5))
    if t > S[2] + 4.9:
        v = lerp(60, 75, prog(t, S[2] + 4.9, 1.0))
    c = RED if v > 65 else GOLD
    d.rounded_rectangle((x - 14, ty(v), x + 14, bot + 10), radius=14, fill=col(c, k))
    d.ellipse((x - 38, bot - 12, x + 38, bot + 62), fill=col(c, k))
    for deg in (55, 65):
        d.line((x + 40, ty(deg), x + 80, ty(deg)), fill=col(CREAM, k), width=4)
        d.text((x + 95, ty(deg) - 34), f"{deg} °C", font=OSW[60], fill=col(CREAM, k))
    if v > 65:
        ctext(d, 760, 900, "SE QUEMA", ANTON[88], RED)
    elif t > S[2] + 2.0:
        ctext(d, 760, 1140, "IDEAL", ANTON[88], col(GOLD, prog(t, S[2] + 2.0, 0.3)))

def s4(d, t):
    numchip(d, 4, S[3], t)
    ctext(d, W / 2, 700, "AGUA FILTRADA", OSW[60], col(CREAM, prog(t, S[3])))
    k = prog(t, S[3] + 0.2)
    cx, cy = W / 2, 1100
    # gota: punta arriba, panza abajo
    r, oy = 160, cy + 80
    pts = [(cx + r * np.cos(np.radians(a)), oy + r * np.sin(np.radians(a))) for a in np.linspace(-25, 205, 60)]
    pts = [(cx, cy - 260)] + pts + [(cx, cy - 260)]
    d.line(pts, fill=col(CREAM, k), width=8, joint="curve")
    if t > S[3] + 2.6:
        kk = prog(t, S[3] + 2.6, 0.4)
        rng = np.random.default_rng(9)
        for i in range(18):
            x, y = rng.uniform(cx - 80, cx + 80), rng.uniform(cy - 20, cy + 150)
            d.rectangle((x - 9, y - 9, x + 9, y + 9), fill=col(RED, kk))
        ctext(d, W / 2, 1330, "SARRO = MAL SABOR", ANTON[88], col(RED, kk))

def s5(d, t):
    numchip(d, 5, S[4], t)
    ctext(d, W / 2, 700, "LIMPIEZA DIARIA", OSW[60], col(CREAM, prog(t, S[4])))
    k = prog(t, S[4] + 0.2)
    maquina(d, W / 2, 1150, CREAM, k)
    # brillos de limpio; luego, "si no": gotas de aceite viejo y AMARGO
    if t < S[4] + 4.3:
        for i in range(3):
            p = (t * 1.5 + i / 3) % 1
            x, y = W / 2 - 150 + i * 150, 1000 + 40 * i
            r = 22 * np.sin(p * np.pi)
            d.line((x - r, y, x + r, y), fill=col(GOLD, k), width=5)
            d.line((x, y - r, x, y + r), fill=col(GOLD, k), width=5)
    else:
        kk = prog(t, S[4] + 4.3, 0.4)
        rng = np.random.default_rng(2)
        for i in range(8):
            x, y = W / 2 + rng.uniform(-60, 60), 1080 + rng.uniform(0, 220) * kk
            d.ellipse((x - 14, y - 18, x + 14, y + 18), fill=col(RED, kk))
        ctext(d, W / 2, 1460, "SI NO: AMARGO", ANTON[88], col(RED, kk))

def close(d, t):
    k = prog(t, CLOSE)
    d.rounded_rectangle((110, 560, 970, 1650), radius=40, outline=col(CARAMEL, k), width=5)
    ctext(d, W / 2, 610, "LO QUE NO VES… PERO PRUEBAS", OSW[52], col(CARAMEL, k))
    items = ["espresso: 25 a 30 s", "moler al momento", "leche: 55 a 65 °C", "agua filtrada", "limpieza diaria"]
    for i, s in enumerate(items):
        kk = prog(t, CLOSE + 0.3 + i * 0.35, 0.3)
        y = 760 + i * 170
        chip(d, W / 2, y, f"{i + 1}. {s}", ANTON[64], CREAM if i % 2 == 0 else GOLD, kk)

def scene(d, t):
    if t < HOOK_END:
        hook(d, t)
    elif t < S[1]:
        s1(d, t)
    elif t < S[2]:
        s2(d, t)
    elif t < S[3]:
        s3(d, t)
    elif t < S[4]:
        s4(d, t)
    elif t < CLOSE:
        s5(d, t)
    else:
        close(d, t)

R.scene = scene

if __name__ == "__main__":
    if len(sys.argv) > 4:
        Image.fromarray(R.frame(float(sys.argv[4]))).save(sys.argv[5])
        sys.exit()
    start, end = float(sys.argv[2]), float(sys.argv[3])
    for i in range(int(start * FPS), int(end * FPS)):
        sys.stdout.buffer.write(R.frame(i / FPS).tobytes())
