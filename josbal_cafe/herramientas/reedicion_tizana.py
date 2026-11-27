# Re-edición del reel de la tizana: recorta, quita el marco, tapa los subtítulos viejos y pone subtítulos grandes.
# Paso 1:  python3 edit.py base original.mp4 base.mp4
# Paso 2:  python3 edit.py overlay <fonts> | ffmpeg ... (cuadros RGBA del texto encima)
import sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
CROP = "crop=888:1578:96:110,scale=1080:1920"
BAND = (1500, 1840)  # franja donde estaban los subtítulos viejos (ya escalado)
CREAM, RED, DARK = (255, 244, 225), (235, 55, 45), (20, 12, 8)

# (inicio, fin, texto) en el video original
SEGS = [
    (0.10, 2.30, "Acompáñenme a preparar mi bebida favorita"),
    (3.70, 6.10, "una tisana de frutos reales"),
    (6.50, 10.00, "una báscula y una jarra para el agua caliente"),
    (10.20, 14.00, "le echamos la tisana y un poquito de agua caliente"),
    (14.50, 16.90, "esperamos que se infusione todo"),
    (17.20, 18.80, "un vaso con hielos"),
    (19.60, 21.30, "le echamos el jarabe natural"),
    (33.50, 36.40, "le vaciamos la tisana al vaso con hielos"),
    (38.00, 40.80, "probarla… ¡y estaba pasadísima de lanza!"),
]
KEYS = {"frutos", "reales", "báscula", "agua", "caliente", "tisana", "infusione", "hielos", "jarabe", "natural",
        "pasadísima", "lanza!"}

def timeline():
    t, out = 0.0, []
    for a, b, s in SEGS:
        out.append((t, t + (b - a), s))
        t += b - a
    return out, t

def base(src, dst):
    parts, labels = [], []
    for i, (a, b, _) in enumerate(SEGS):
        d = b - a
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={d - 0.06:.2f}:d=0.06[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    fc = "".join(parts) + "".join(labels) + f"concat=n={len(SEGS)}:v=1:a=1[cv][ca];"
    y0, y1 = BAND
    h = y1 - y0
    # franja borrosa con orillas suaves (alfa en rampa de 80 px arriba y abajo)
    fc += (f"[cv]{CROP},split[m][b];[b]crop={W}:{h}:0:{y0},boxblur=30:3,format=rgba,"
           f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*min(1,min(Y,{h}-Y)/80)'[bb];"
           f"[m][bb]overlay=0:{y0}[v];[ca]loudnorm=I=-15:TP=-1.5[a]")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", dst], check=True)

def overlay(fonts, still=None):
    big = ImageFont.truetype(f"{fonts}/Anton-Regular.ttf", 120)
    mid = ImageFont.truetype(f"{fonts}/Anton-Regular.ttf", 84)
    sub = ImageFont.truetype(f"{fonts}/Anton-Regular.ttf", 76)
    tl, total = timeline()

    def ctext(d, y, s, f, c):
        w = f.getlength(s)
        d.text(((W - w) / 2, y), s, font=f, fill=c, stroke_width=8, stroke_fill=DARK)

    def caption(d, s, t, a):
        words, lines, cur = s.split(), [], []
        for w_ in words:
            if cur and sub.getlength(" ".join(cur + [w_]).upper()) > 940:
                lines.append(cur); cur = []
            cur.append(w_)
        lines.append(cur)
        y = 260
        n = len(words)
        shown = int(np.clip((t - a) / 0.11, 0, n)) + 1
        k = 0
        for line in lines:
            txt = " ".join(line).upper()
            x = (W - sub.getlength(txt)) / 2
            for w_ in line:
                if k < shown:
                    c = RED if w_.lower().strip("…¡!,") in {x.strip("¡!") for x in KEYS} else CREAM
                    d.text((x, y), w_.upper(), font=sub, fill=c, stroke_width=7, stroke_fill=DARK)
                x += sub.getlength(w_.upper() + " ")
                k += 1
            y += 100

    def frame(t):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        a0, b0, _ = tl[0]
        if t < b0:  # gancho: título completo desde el primer cuadro
            ctext(d, 250, "TIZANA DE", mid, CREAM)
            ctext(d, 360, "FRUTOS REALES", big, RED)
            ctext(d, 520, "ASÍ SE HACE", mid, CREAM)
            return im
        for a, b, s in tl:
            if a <= t < b + 0.15:
                caption(d, s, t, a)
                break
        # salto de tiempo antes de vaciar
        a7 = tl[7][0]
        if a7 <= t < a7 + 1.8:
            ctext(d, 1180, "UN RATO DESPUÉS…", mid, CREAM)
        return im

    if still is not None:
        return frame(still)
    for i in range(int(round(total * FPS))):
        sys.stdout.buffer.write(frame(i / FPS).tobytes())

if __name__ == "__main__":
    if sys.argv[1] == "base":
        base(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "total":
        print(f"{timeline()[1]:.2f}")
    elif sys.argv[1] == "still":
        overlay(sys.argv[2], float(sys.argv[3])).save(sys.argv[4])
    else:
        overlay(sys.argv[2])
