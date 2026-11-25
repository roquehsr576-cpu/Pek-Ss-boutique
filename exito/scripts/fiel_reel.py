"""Reel 1 "Fiel en lo poco": voz alineada por pausas, subtítulos palabra por palabra,
escenas sincronizadas con la voz y la música, textos que no tapan caras.
Uso: python3 exito/scripts/fiel_reel.py [preview]"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from motion import ease_out_back, ease_in_out_sine, clamp

ROOT = 'exito/fuentes/reel1_fiel_en_lo_poco'
MUSIC = 'exito/fuentes/musica/rise_with_purpose.mp3'
OUT = 'exito/reels/reel01_fiel_en_lo_poco.mp4'
W, H, FPS = 1080, 1920, 30
FD = '/usr/share/fonts/opentype/inter/'
def F(name, size): return ImageFont.truetype(FD + name, size)
GOLD, RED, GREEN, WHITE = (245, 196, 66), (235, 70, 70), (70, 200, 120), (255, 255, 255)

TEXT = open(f'{ROOT}/guion_voz.txt').read().strip()
PHRASES = [p.strip() for p in re.split(r'(?<=[\.\,\:\?…])\s+', TEXT) if p.strip()]

# ---------- alineación voz ↔ frases ----------
def voiced_segments(path):
    out = subprocess.run(['ffmpeg', '-i', path, '-af', 'silencedetect=noise=-38dB:d=0.25', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]
    e = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                               capture_output=True, text=True).stdout)
    segs, t = [], 0.0
    for a, b in zip(s, e):
        if a > t: segs.append((t, a))
        t = b
    if dur - t > 0.1: segs.append((t, dur))
    return segs, dur

def align(phrases, segs):
    """Agrupa frases consecutivas en segmentos de voz (DP por duración esperada)."""
    L = [len(p) + 2 for p in phrases]
    rate = sum(b - a for a, b in segs) / sum(L)
    n, m = len(phrases), len(segs)
    INF = 1e18
    dp = [[INF] * (m + 1) for _ in range(n + 1)]; bk = [[0] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for j in range(1, m + 1):
        d = segs[j - 1][1] - segs[j - 1][0]
        for i in range(1, n + 1):
            acc = 0
            for k in range(i, 0, -1):
                acc += L[k - 1]
                c = dp[k - 1][j - 1] + (d - acc * rate) ** 2
                if c < dp[i][j]: dp[i][j], bk[i][j] = c, k - 1
    groups, i = [], n
    for j in range(m, 0, -1):
        k = bk[i][j]; groups.append((k, i, segs[j - 1])); i = k
    groups.reverse()
    words, pstart = [], {}
    for k, i, (a, b) in groups:
        ws = [w for p in phrases[k:i] for w in p.split()]
        wl = [len(w) + 1 for w in ws]; tot = sum(wl); t = a
        first = {}
        cnt = 0
        for pi in range(k, i):
            first[cnt] = pi; cnt += len(phrases[pi].split())
        for wi, (w, l) in enumerate(zip(ws, wl)):
            d = (b - a) * l / tot
            if wi in first: pstart[first[wi]] = t
            words.append((w, t, t + d)); t += d
    return words, pstart

# ---------- utilidades de imagen ----------
def cover(im, w=W, h=H):
    r = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.LANCZOS)
    return im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))

def kenburns(im, p, z0=1.0, z1=1.08, fy=0.5):
    z = z0 + (z1 - z0) * ease_in_out_sine(p)
    w, h = int(W / z), int(H / z)
    x = (im.width - w) // 2; y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)

class Clip:
    def __init__(self, path):
        self.frames = []
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}',
                              '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        n = len(raw) // (W * H * 3)
        self.frames = [raw[i * W * H * 3:(i + 1) * W * H * 3] for i in range(n)]
    def get(self, t):
        i = min(int(t * FPS), len(self.frames) - 1)
        return Image.frombytes('RGB', (W, H), self.frames[i])

def gradient(top=True, h=700, a=200):
    g = Image.new('L', (1, h))
    for y in range(h): g.putpixel((0, y), int(a * (1 - y / h) ** 1.6) if top else int(a * (y / h) ** 1.6))
    lay = Image.new('RGBA', (W, h), (0, 0, 0, 255)); lay.putalpha(g.resize((W, h))); return lay
GTOP, GBOT = gradient(True), gradient(False, 760, 220)

def text_img(txt, size, fill=WHITE, weight='Inter-ExtraBold.otf', stroke=5, pill=None, lh=1.12):
    f = F(weight, size); lines = txt.split('\n'); d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    w = int(max(d0.textlength(l, font=f) for l in lines)); hh = int(size * lh)
    pad = (44, 24) if pill else (stroke * 2, stroke * 2)
    im = Image.new('RGBA', (w + pad[0] * 2, hh * len(lines) + pad[1] * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if pill: d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=min(50, im.height // 2), fill=pill)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=f)
        d.text(((im.width - lw) / 2, pad[1] + i * hh), l, font=f, fill=fill,
               stroke_width=0 if pill else stroke, stroke_fill=(0, 0, 0))
    return im

def put(frame, im, cx, cy, t, start, end=None, rise=70):
    if t < start or (end is not None and t > end): return
    k = ease_out_back(clamp((t - start) / 0.45)); a = clamp((t - start) / 0.2)
    if end is not None: a *= clamp((end - t) / 0.2)
    bob = 4 * math.sin((t - start) * 2 * math.pi / 2.6)
    s = 0.85 + 0.15 * k
    im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if a < 1:
        al = im2.getchannel('A').point(lambda v: int(v * a)); im2.putalpha(al)
    frame.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2 + rise * (1 - k) + bob)))

KEY = {'uno', 'por', 'ciento', 'dios', 'treinta', 'siete', 'veces', 'tres', 'fiel', 'pequeño', 'invisible', 'todo', 'año', 'jesús', 'iguales', 'cuenta'}
SUBF = F('Inter-ExtraBold.otf', 58)
def subtitle(frame, words, t, y=1585):
    cur = [i for i, (_, a, b) in enumerate(words) if a <= t]
    if not cur: return
    i = cur[-1]
    if t > words[i][2] + 0.6: return
    # ventana: frase de hasta 4 palabras que contiene la palabra actual
    s = (i // 4) * 4; chunk = words[s:min(s + 4, len(words))]
    d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    toks = [w for w, _, _ in chunk]; widths = [d0.textlength(w + ' ', font=SUBF) for w in toks]
    x = (W - sum(widths)) / 2
    d = ImageDraw.Draw(frame)
    for (w, a, b), ww in zip(chunk, widths):
        if a > t: break
        clean = re.sub(r'[^\wáéíóúñü]', '', w.lower())
        col = GOLD if clean in KEY else WHITE
        pop = 1 + 0.12 * (1 - clamp((t - a) / 0.15))
        f = SUBF if pop < 1.01 else F('Inter-ExtraBold.otf', int(58 * pop))
        d.text((x, y - (f.size - 58) / 2), w, font=f, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
        x += ww

def main(preview=False):
    segs, vdur = voiced_segments(f'{ROOT}/voz.mp3')
    words, P = align(PHRASES, segs)
    json.dump({'words': words, 'phrase_start': P}, open(f'{ROOT}/words.json', 'w'), ensure_ascii=False, indent=0)
    V0 = 0.15  # la voz empieza 0.15 s después del cuadro 1 (texto grande desde el cuadro 1)
    words = [(w, a + V0, b + V0) for w, a, b in words]; P = {k: v + V0 for k, v in P.items()}
    total = vdur + V0 + 2.6
    img = lambda n: Image.open(f'{ROOT}/img/s{n:02d}.png').convert('RGB')
    clip = lambda n: Clip(f'{ROOT}/veo/v{n:02d}.mp4') if os.path.exists(f'{ROOT}/veo/v{n:02d}.mp4') else None
    # escenas: (frase de inicio, fuente, imagen, opciones de Ken Burns)
    S = [(0, 1, dict(z0=1.0, z1=1.06)), (1, 2, dict(z0=1.12, z1=1.0)), (3, 3, {}), (6, 4, dict(z0=1.0, z1=1.1, fy=0.3)),
         (10, 5, dict(z0=1.1, z1=1.0)), (13, 6, {}), (18, 7, dict(z0=1.0, z1=1.12, fy=0.35)), (21, 8, {}),
         (23, 9, dict(z0=1.12, z1=1.0)), (25, 10, {}), (28, 11, dict(z0=1.0, z1=1.15, fy=0.6)), (31, 12, {}),
         (34, 13, dict(z0=1.0, z1=1.08)), (37, 14, dict(z0=1.08, z1=1.0))]
    starts = [0.0] + [P[s] - 0.12 for s, _, _ in S[1:]]
    ends = starts[1:] + [total]
    bgs = {}
    for (s, n, kb), a in zip(S, starts):
        c = clip(n) if n in (1, 8, 10) else None
        bgs[n] = ('clip', c) if c else ('img', cover(img(n), int(W * 1.0), int(H * 1.0)))
    T = {}  # textos por escena
    p = lambda i: P[i]
    texts = [
        (text_img('1 % AL DÍA…', 104), 540, 330, 0.0, starts[1]),
        (text_img('¿Y QUÉ?', 124, GOLD), 540, 470, 0.35, starts[1]),
        (text_img('HAZ LA CUENTA', 96), 540, 360, p(1), starts[2]),
        (text_img('MISMO DÍA UNO', 92), 540, 330, p(4), starts[3]),
        (text_img('A: +1 % DIARIO', 70, WHITE, pill=(30, 140, 80, 235)), 540, 1000, p(6), starts[4]),
        (text_img('10 min con Dios', 56, WHITE, 'Inter-Bold.otf', pill=(0, 0, 0, 170)), 540, 1130, p(7), starts[4]),
        (text_img('Caminar un poco más', 56, WHITE, 'Inter-Bold.otf', pill=(0, 0, 0, 170)), 540, 1240, p(8), starts[4]),
        (text_img('Cumplir su palabra', 56, WHITE, 'Inter-Bold.otf', pill=(0, 0, 0, 170)), 540, 1350, p(9), starts[4]),
        (text_img('B: −1 % DIARIO', 70, WHITE, pill=(180, 40, 40, 235)), 540, 1000, p(10), starts[5]),
        (text_img('Una excusa aquí', 56, WHITE, 'Inter-Bold.otf', pill=(0, 0, 0, 170)), 540, 1130, p(11), starts[5]),
        (text_img('"Mañana lo hago"', 56, WHITE, 'Inter-Bold.otf', pill=(0, 0, 0, 170)), 540, 1240, p(12), starts[5]),
        (text_img('DÍA 1', 110), 540, 1230, p(14), p(15)),
        (text_img('DÍA 7', 110), 540, 1230, p(15), p(16)),
        (text_img('DÍA 30', 110), 540, 1230, p(16), starts[6]),
        (text_img('CASI IGUALES', 78, GOLD), 540, 1380, p(17), starts[6]),
        (text_img('¿TÚ CUÁL\nHAS SIDO?', 100, GOLD), 540, 1400, p(20), starts[7]),
        (text_img('DESPUÉS DE 1 AÑO', 78), 540, 300, p(21), starts[8]),
        (text_img('× 37.8', 230, GOLD, stroke=8), 540, 520, p(22) + 1.2, starts[8]),
        (text_img('0.03', 230, RED, stroke=8), 540, 430, p(24) + 1.0, starts[9]),
        (text_img('Lo pequeño,', 92), 540, 330, p(26), starts[10]),
        (text_img('todos los días', 100, GOLD), 540, 460, p(27), starts[10]),
        (text_img('Invisible hoy.', 96), 540, 330, p(29), starts[11]),
        (text_img('Todo en un año.', 100, GOLD), 540, 470, p(30), starts[11]),
        (text_img('1.01³⁶⁵ = 37.8', 104, GOLD), 540, 650, p(31), starts[12]),
        (text_img('0.99³⁶⁵ = 0.03', 104, RED), 540, 820, p(31) + 0.8, starts[12]),
        (text_img('Cálculo matemático · idea de\n"Hábitos atómicos", James Clear', 38, (220, 220, 220), 'Inter-Medium.otf', stroke=3), 540, 1000, p(31) + 1.4, starts[12]),
        (text_img('"El que es fiel en lo muy poco,\ntambién en lo más es fiel."', 64, WHITE, 'Inter-Bold.otf'), 540, 380, p(35), starts[13]),
        (text_img('Lucas 16:10', 70, GOLD), 540, 560, p(35) + 0.6, starts[13]),
        (text_img('¿En qué vas a ser fiel\nen lo poco mañana?', 84, GOLD), 540, 420, p(38), None),
    ]
    AI = text_img('Imágenes creadas con IA', 30, (230, 230, 230), 'Inter-Medium.otf', stroke=2)
    nfr = int(total * FPS)
    rng = range(0, nfr, 15) if preview else range(nfr)
    out = OUT if not preview else f'{ROOT}/preview.mp4'
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS if not preview else 2),
                             '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', f'{ROOT}/video_noaudio.mp4' if not preview else out], stdin=subprocess.PIPE)
    for fi in rng:
        t = fi / FPS
        k = max(i for i, a in enumerate(starts) if a <= t)
        n = S[k][1]; kb = S[k][2]; a, b = starts[k], ends[k]; pr = (t - a) / max(0.01, b - a)
        kind, src = bgs[n]
        base = src.get(t - a) if kind == 'clip' else kenburns(src, pr, **kb)
        # transición: entrada con fundido corto y pequeño golpe de zoom
        if k > 0 and t - a < 0.25:
            pn = S[k - 1][1]; pk, ps = bgs[pn]
            prev = ps.get(t - starts[k - 1]) if pk == 'clip' else kenburns(ps, 1.0, **S[k - 1][2])
            base = Image.blend(prev, base, clamp((t - a) / 0.25))
        fr = base.convert('RGBA')
        fr.alpha_composite(GTOP, (0, 0)); fr.alpha_composite(GBOT, (0, H - GBOT.height))
        for im, cx, cy, s0, s1 in texts: put(fr, im, cx, cy, t, s0, s1)
        subtitle(fr, words, t)
        fr.alpha_composite(AI, ((W - AI.width) // 2, H - 70))
        proc.stdin.write(fr.convert('RGB').tobytes())
    proc.stdin.close(); proc.wait()
    json.dump({'total': total, 'reveal': P[21], 'tail': P[34], 'V0': V0}, open(f'{ROOT}/timing.json', 'w'))
    print('frames', nfr, 'total', round(total, 2), 'reveal', round(P[21], 2), 'tail', round(P[34], 2))

if __name__ == '__main__':
    main('preview' in sys.argv)
