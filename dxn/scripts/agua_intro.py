import sys, json, subprocess, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; B = R + 'agua/'
HK = 2.61; G1 = 0.35; TZ = 4.96; T = HK + G1 + TZ + 0.35; T2 = HK + G1
grad = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(grad)
for y in range(H): d.line((0, y, W, y), fill=(int(6 + 10 * y / H), int(60 + 50 * y / H), int(120 + 60 * y / H), 255))
emb = Embers(45, seed=4)
FX = 540
def body_mask():
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); s = 0.95; cy = 800
    def R_(x0, y0, x1, y1, r): d.rounded_rectangle((FX + x0 * s, cy + y0 * s, FX + x1 * s, cy + y1 * s), int(r * s), fill=255)
    d.ellipse((FX - 85 * s, cy - 190 * s, FX + 85 * s, cy - 10 * s), fill=255); R_(-30, -20, 30, 30, 5); R_(-120, 20, 120, 450, 60)
    R_(-178, 35, -128, 450, 25); R_(128, 35, 178, 450, 25); R_(-110, 410, -12, 900, 40); R_(12, 410, 110, 900, 40)
    return m
BODY = body_mask(); EDGE = BODY.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
s, cy = 0.95, 800
BONES = [(FX - 61 * s, cy + 440 * s, FX - 61 * s, cy + 870 * s), (FX + 61 * s, cy + 440 * s, FX + 61 * s, cy + 870 * s), (FX - 153 * s, cy + 60 * s, FX - 153 * s, cy + 420 * s),
         (FX + 153 * s, cy + 60 * s, FX + 153 * s, cy + 420 * s), (FX, cy + 30 * s, FX, cy + 410 * s)]
for i in range(5): BONES.append((FX - 70 * s, cy + (90 + 45 * i) * s, FX + 70 * s, cy + (90 + 45 * i) * s))
fH = font('Inter-ExtraBold.otf', 120); fB = font('Inter-ExtraBold.otf', 84); fBig = font('Inter-ExtraBold.otf', 230); fS = font('Inter-Bold.otf', 42); fT = font('Inter-Medium.otf', 28)
AQUA = (120, 220, 255); BLUE = (10, 110, 200, 235); RED = (200, 30, 60, 235)
def splash(p): i = int(1 + clamp(p) * 236); return Image.open(f'{B}fr/splash/{i:04d}.jpg').convert('RGBA')
L = [(0.0, T2, text_layer('TUS HUESOS SON', font('Inter-ExtraBold.otf', 66), stroke=7), 110), (0.35, T2, text_layer('31%', fBig, fill=AQUA, stroke=12), 190), (0.6, T2, text_layer('AGUA', fH, stroke=8), 430),
     (0.3, T2, text_layer('Fuente: USGS · Mitchell et al., 1945', fT, pill=(0, 0, 0, 140), pad=(20, 8)), 1640),
     (T2, T, text_layer('QUÉDATE\nAL FINAL', fH, fill=AQUA, stroke=10), 420), (T2 + 2.2, T, text_layer('El dato final casi nadie lo sabe', fS, pill=RED), 800)]
logo = Image.open(R + 'clip/dxn-logo.png').convert('RGBA').resize((120, 116), Image.LANCZOS)
lb = Image.new('RGBA', (140, 136)); m = Image.new('L', (140, 136), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 139, 135), 22, fill=230); lb.paste((255, 255, 255, 255), (0, 0), m); lb.alpha_composite(logo, (10, 10))
CAPS = [(0.0, HK, 'HASTA TUS HUESOS, 31%'), (T2, T2 + 1.6, 'Y QUÉDATE HASTA EL FINAL...'), (T2 + 1.85, T2 + 3.4, 'PORQUE TE TENGO UN DATO'), (T2 + 3.4, T, 'QUE CASI NADIE SABE.')]
KEY = {'HUESOS,', '31%', 'FINAL...', 'DATO', 'NADIE'}
fC = font('Inter-ExtraBold.otf', 62)
def compose(t):
    if t < T2:
        fr = grad.copy(); emb.draw(fr, t, color=(200, 240, 255), alpha=0.6)
        lvl = cy + 900 * s - (1100 * s) * 0.6 * ease_out_cubic(clamp(t / 1.2))
        water = Image.new('RGBA', (W, H)); wd = ImageDraw.Draw(water)
        wd.polygon([(x, lvl + 10 * math.sin(x / 40 + t * 4)) for x in range(0, W + 10, 10)] + [(W, H), (0, H)], fill=(70, 190, 255, 200))
        fr.alpha_composite(Image.composite(Image.new('RGBA', (W, H), (255, 255, 255, 45)), Image.new('RGBA', (W, H)), BODY))
        fr.alpha_composite(Image.composite(water, Image.new('RGBA', (W, H)), BODY))
        fr.alpha_composite(Image.composite(Image.new('RGBA', (W, H), (255, 255, 255, 230)), Image.new('RGBA', (W, H)), EDGE))
        ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov); pul = 0.5 + 0.5 * math.sin(t * 7); k = clamp(t / 0.4)
        for bx in BONES: od.line(bx, fill=(255, 230, 90, int(k * (200 + 55 * pul))), width=16)
        fr.alpha_composite(ov.filter(ImageFilter.GaussianBlur(2)))
    else:
        fr = splash((t - T2) / (T - T2) * 0.6)
        if t < T2 + 0.1: fr = Image.blend(fr, Image.new('RGBA', (W, H), (230, 250, 255, 255)), 0.5 * (1 - (t - T2) / 0.1))
    for i, (s_, e, ly, y) in enumerate(L): animate_in(fr, ly, t, s_, W / 2, y + ly.height / 2, end=e if e < T else None, seed=i * 0.8)
    dd = ImageDraw.Draw(fr)
    for a, b, txt in CAPS:
        if a <= t < b:
            ws = txt.split(); wd_ = [dd.textlength(w + ' ', font=fC) for w in ws]; x = (W - sum(wd_)) / 2; k = entrance(t, a, 0.25)
            for w, ww in zip(ws, wd_): dd.text((x, 1700 + 30 * (1 - k)), w, font=fC, fill=(120, 220, 255) if w in KEY else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
    fr.alpha_composite(lb, (W - 170, 40)); return fr
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
out = sys.argv[1]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(T * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', T)
