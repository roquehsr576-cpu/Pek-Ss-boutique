import sys, json, subprocess, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from motion import *
B = '/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
G = B + 'scratchpad/dxngal/'; P = B + 'proceso/'
words = [w for w in json.load(open(P + 'words.json'))['words'] if w.get('type') == 'word']
VEND = words[-1]['end']; T = math.ceil(VEND + 3.5)
def at(word, after=0.0):
    for w in words:
        if w['start'] >= after and w['text'].lower().strip('¿?¡!.,:') == word: return w['start']
    raise SystemExit('word not found: ' + word)
# scene starts keyed to narration
t_mat = at('materiales'); t_bol = at('bolsas', t_mat); t_est = at('esterilización'); t_cuel = at('cuelgan')
t_mag = at('aquí', t_cuel); t_sem = at('primera'); t_mes = at('mes', t_sem); t_dos = at('dos', t_mes); t_tres = at('tres', t_dos); t_mad = at('maduro', t_tres)
t_cos = at('cosecha'); t_maq = at('máquinas', t_cos); t_pul = at('pulen'); t_bot = at('botellas'); t_sel = at('sellan'); t_eti = at('etiquetan')
t_lis = at('listo', t_eti); t_q = at('qué', t_lis)
# (start, image, label, caption)
SC = [(0.0, '04_024.jpg', None, None), (1.0, '37_011.jpg', None, None), (2.0, '04_034.jpg', None, None), (3.0, '37_016.jpg', None, None),
      (4.2, '37_001.jpg', None, None),
      (t_mat - 0.2, '37_007.jpg', '1', 'Materiales orgánicos'), (t_bol - 0.2, '37_009.jpg', '2', 'Llenado de bolsas'),
      (t_est - 0.2, '37_011.jpg', '3', 'Esterilización'), (t_est + 2.2, '03_014.jpg', '3', 'Máquina de alta tecnología'),
      (t_cuel - 0.2, '37_001.jpg', '4', 'Bolsas suspendidas'),
      (t_sem - 0.2, '04_001_1.jpg', '1 SEMANA', 'Micelio'), (t_mes - 0.2, '04_005.jpg', '1 MES', 'Cuerno de ciervo'),
      (t_dos - 0.2, '04_010.jpg', '2 MESES', 'Etapa intermedia'), (t_tres - 0.2, '04_024.jpg', '3 MESES', 'Hongo maduro'),
      (t_cos - 0.2, '04_034.jpg', '5', 'Cosecha'), (t_maq - 0.2, '37_016.jpg', '6', 'Llenado de cápsulas'),
      (t_pul - 0.2, '37_017_1.jpg', '7', 'Pulido'), (t_bot - 0.2, '37_019.jpg', '8', 'Embotellado'), (t_sel - 0.2, '37_018.jpg', '9', 'Sellado'),
      (t_eti - 0.2, '37_021.jpg', '10', 'Etiquetado con lote y caducidad'), (t_lis - 0.2, '37_022.jpg', '✓', 'Listo para llegar a tus manos'),
      (t_q - 0.3, 'heart_gano.png', None, None)]
imgs = {}
for _, f, _, _ in SC:
    if f in imgs: continue
    im = Image.open(G + f).convert('RGB'); r = 940 / im.width
    card = im.resize((940, int(im.height * r)), Image.LANCZOS)
    fr = Image.new('RGBA', (card.width + 28, card.height + 28), (255, 255, 255, 255)); fr.paste(card, (14, 14))
    m = Image.new('L', fr.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=26, fill=255); fr.putalpha(m)
    sh = Image.new('RGBA', (fr.width + 80, fr.height + 80), (0, 0, 0, 0)); sh.paste((0, 0, 0, 255), (40, 52), m.point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); sh.alpha_composite(fr, (40, 40))
    bg = cover(im, int(W * 1.15), int(H * 1.15)).filter(ImageFilter.GaussianBlur(28)); bg = ImageEnhance.Brightness(bg).enhance(0.45)
    imgs[f] = (sh, bg)
emb = Embers(40, seed=21)
fH = font('Inter-ExtraBold.otf', 100); fB = font('Inter-ExtraBold.otf', 80); fM = font('Inter-ExtraBold.otf', 60); fS = font('Inter-Bold.otf', 46)
fBadge = font('Inter-ExtraBold.otf', 34)
RED = (200, 25, 25, 240); DARK = (15, 15, 15, 225); GOLD = (255, 205, 110)
badge = text_layer('📷 FOTO REAL · DXN'.replace('📷 ', ''), fBadge, pill=(255, 255, 255, 235), fill=(30, 30, 30), pad=(24, 12))
lbl = {}
def scene_idx(t):
    i = 0
    for k, s in enumerate(SC):
        if t >= s[0]: i = k
    return i
def frame_at(t):
    i = scene_idx(t); s0, f, label, cap = SC[i]; sh, bg = imgs[f]
    e = SC[i + 1][0] if i + 1 < len(SC) else T
    p = ease_in_out_sine((t - s0) / max(0.01, e - s0))
    cx, cy = 30 * math.sin(t * 0.4), 20 * math.sin(t * 0.33)
    bw, bh = bg.size; x = (bw - W) / 2 - cx * 0.25; y = (bh - H) / 2 - cy * 0.25
    fr = bg.crop((int(x), int(y), int(x) + W, int(y) + H)).convert('RGBA')
    k = entrance(t, s0, 0.5); dy, sc, ang = idle(t, i * 0.7, amp=6)
    tilt = (-2.5 if i % 2 else 2.5) * (1 - k) + ang
    place(fr, sh, W / 2 - cx * 0.6, 900 + 160 * (1 - k) + dy - cy * 0.6, (0.82 + 0.18 * k) * sc * (1.0 + 0.04 * p), tilt, clamp(k * 1.5))
    emb.draw(fr, t, color=(255, 220, 160), alpha=0.6)
    if t >= 0.2 and t < T - 6: animate_in(fr, badge, t, max(0.2, s0 + 0.15) if s0 > 0 else 0.2, W / 2, 1410, seed=3)
    if label:
        key = (label, cap)
        if key not in lbl:
            lbl[key] = (text_layer(label, fB if len(label) > 2 else fH, fill=GOLD), text_layer(cap, fM if len(cap) < 22 else fS, pill=RED))
        L1, L2 = lbl[key]
        animate_in(fr, L1, t, s0 + 0.1, W / 2, 300, seed=i)
        animate_in(fr, L2, t, s0 + 0.35, W / 2, 440, seed=i + 0.5)
    return fr
hook = [(0.1, 4.5, text_layer('ESTO NO ES IA', fH), 300), (1.6, 4.5, text_layer('FOTOS REALES DEL CULTIVO DXN', fS, pill=RED), 440)]
endt = [(t_q - 0.2, T, text_layer('¿QUÉ PARTE NO\nCONOCÍAS?', fB, fill=GOLD), 260), (t_q + 1.2, T, text_layer('Cuéntame en los comentarios', fS, pill=RED), 1500)]
caps = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w['text'][-1] in '.,?!:':
        caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
if cur: caps.append([cur[0]['start'], cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i in range(len(caps) - 1): caps[i][1] = caps[i + 1][0] if caps[i + 1][0] - caps[i][1] < 0.6 else caps[i][1] + 0.25
KEY = {'REALES', 'GANODERMA', 'DXN', 'ORGÁNICOS,', 'BOLSAS', 'ESTERILIZACIÓN', 'SUSPENDIDAS', 'MICELIO.', 'CUERNOS', 'CIERVO.', 'MADURO.', 'COSECHA',
       'CÁPSULAS.', 'LIMPIEZA.', 'BOTELLAS,', 'LOTE', 'CADUCIDAD.', 'INTELIGENCIA', 'ARTIFICIAL.', 'MESES', 'SEMANA:'}
fC = font('Inter-ExtraBold.otf', 60)
def draw_caption(fr, txt, t, s):
    d = ImageDraw.Draw(fr); ws = txt.upper().split(); wd = [d.textlength(w + ' ', font=fC) for w in ws]
    k = entrance(t, s, 0.25); x = (W - sum(wd)) / 2
    for w, ww in zip(ws, wd):
        col = (255, 214, 10) if w in KEY or w.strip('¿?.,:') in KEY else (255, 255, 255)
        d.text((x, 1720 + 30 * (1 - k)), w, font=fC, fill=col, stroke_width=6, stroke_fill=(0, 0, 0)); x += ww
def compose(t):
    fr = frame_at(t)
    for j, (s, e, ly, y) in enumerate(hook + endt): animate_in(fr, ly, t, s, W / 2, y + ly.height / 2, end=e if e < T else None, seed=j)
    for s, e, txt in caps:
        if s <= t < e and t < t_q - 0.2: draw_caption(fr, txt, t, s)
    for c in [s[0] for s in SC[1:5]]:
        if c <= t < c + 0.08: fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.5)
    return fr
if sys.argv[1] == 'info': print('T', T, 'scenes', [round(s[0], 1) for s in SC]); sys.exit()
if sys.argv[1] == 'preview':
    ts = [float(x) for x in sys.argv[2].split(',')]; ims = [compose(t).convert('RGB').resize((180, 320)) for t in ts]
    c = Image.new('RGB', (180 * len(ims), 320)); [c.paste(im, (i * 180, 0)) for i, im in enumerate(ims)]; c.save(sys.argv[3]); sys.exit()
lo, hi, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for n in range(int(round(lo * FPS)), int(round(min(hi, T) * FPS))): p.stdin.write(compose(n / FPS).convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok', lo, hi)
