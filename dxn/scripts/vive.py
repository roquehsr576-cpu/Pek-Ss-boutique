import sys, subprocess, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
R = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; P = R + 'scratchpad/dxnsite/pick/'
DROP = 2.5; BEAT = 0.6; STEP = 2 * BEAT
SEQ = [('A05', 'EVENTOS'), ('C00', None), ('A02', None), ('A10', None),
       ('I00', 'VIAJES'), ('I03', None), ('I11', None), ('I06', None), ('I09', None),
       ('T03', 'CAPACITACIONES'), ('T05', None), ('T09', None), ('T11', None),
       ('C02', 'RECONOCIMIENTOS'), ('C08', None), ('C07', None), ('C11', None), ('A11', None)]
END = DROP + STEP * len(SEQ); T = END + 4.4
cache = {}
def card(k):
    if k in cache: return cache[k]
    im = Image.open(P + k + '.jpg').convert('RGB')
    bg = ImageEnhance.Brightness(cover(im, W, H).filter(ImageFilter.GaussianBlur(30))).enhance(0.5).convert('RGBA')
    r = 1040 / im.width; ph = im.resize((1040, int(im.height * r)), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', ph.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), 28, fill=255); ph.putalpha(m)
    cache[k] = (bg, ph); return cache[k]
fH = font('Inter-ExtraBold.otf', 110); fB = font('Inter-ExtraBold.otf', 80); fM = font('Inter-ExtraBold.otf', 62); fS = font('Inter-Bold.otf', 42); fT = font('Inter-Medium.otf', 28)
RED = (200, 25, 40, 240); GOLD = (255, 214, 90)
logo = Image.open(R + 'clip/dxn-logo.png').convert('RGBA')
def badge(sz):
    l = logo.resize((sz, int(sz * 145 / 150)), Image.LANCZOS); b = Image.new('RGBA', (sz + 30, l.height + 30)); m = Image.new('L', b.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, b.width - 1, b.height - 1), 24, fill=235); b.paste((255, 255, 255, 255), (0, 0), m); b.alpha_composite(l, (15, 15)); return b
LB = badge(110); BIG = badge(330)
LAB = {}
grad = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(grad)
for y in range(H): d.line((0, y, W, y), fill=(int(120 - 80 * y / H), int(14 + 6 * y / H), int(24 + 10 * y / H), 255))
emb = Embers(50, seed=3)
def compose(t):
    if t < DROP:
        bg, ph = card('A00'); fr = bg.copy(); p = t / DROP
        place(fr, ph, W / 2, 900, 0.95 + 0.08 * p, 0, 1)
        fr = Image.blend(fr, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.35 * (1 - p))
        animate_in(fr, text_layer('Esto es lo que', fB), t, 0.2, W / 2, 330); animate_in(fr, text_layer('nadie te cuenta', fB, fill=GOLD), t, 0.9, W / 2, 440)
        animate_in(fr, text_layer('de DXN...', fB), t, 1.5, W / 2, 550)
    elif t < END:
        i = int((t - DROP) / STEP); s0 = DROP + i * STEP; k, lab = SEQ[i]; bg, ph = card(k); fr = bg.copy()
        loc = t - s0; punch = 1.0 + 0.07 * (1 - ease_out_cubic(clamp(loc / 0.25))) + 0.03 * (loc / STEP)
        place(fr, ph, W / 2, 960, punch, (-1.2 if i % 2 else 1.2) * (1 - clamp(loc / 0.2)), 1)
        if loc < 0.08: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.5 * (1 - loc / 0.08))
        cur = None
        for j in range(i, -1, -1):
            if SEQ[j][1]: cur = (SEQ[j][1], DROP + j * STEP); break
        if cur:
            if cur[0] not in LAB: LAB[cur[0]] = text_layer(cur[0], fH if len(cur[0]) < 12 else fM, fill=GOLD, stroke=8)
            animate_in(fr, LAB[cur[0]], t, cur[1], W / 2, 330, seed=i)
        animate_in(fr, text_layer('FOTOS REALES · DXN', fS, pill=RED), t, DROP + 0.2, W / 2, 1560)
    else:
        fr = grad.copy(); emb.draw(fr, t, color=(255, 210, 140), alpha=0.8)
        k = entrance(t, END + 0.1, 0.6); dy, sc, ang = idle(t, 2, amp=6); place(fr, BIG, W / 2, 820 + 150 * (1 - k) + dy, (0.6 + 0.4 * k) * sc, ang, clamp(k * 1.4))
        animate_in(fr, text_layer('Más que un café,', fB), t, END + 0.5, W / 2, 1160); animate_in(fr, text_layer('una comunidad', fB, fill=GOLD), t, END + 0.9, W / 2, 1270)
        animate_in(fr, text_layer('¿Te gustaría vivirlo? Escríbeme', fS, pill=RED), t, END + 1.6, W / 2, 1480)
    animate_in(fr, text_layer('Fotos: galería oficial DXN Latinoamérica', fT, pill=(0, 0, 0, 130), pad=(18, 8)), t, 0.3, W / 2, 1860)
    if t < END: fr.alpha_composite(LB, (W - 160, 40))
    return fr
if sys.argv[1] == 'info': print('T', T, 'END', END); sys.exit()
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((216, 384)) for t in ts]
    c = Image.new('RGB', (216 * len(ims), 384)); [c.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(min(hi, T) * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
