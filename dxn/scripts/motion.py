"""Motion toolkit for DXN reels: easing with overshoot, staggered entrances,
3-layer parallax, constant idle micro-motion and an energy-saber slash."""
import math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
F = '/usr/share/fonts/opentype/inter/'
def font(name, size): return ImageFont.truetype(F + name, size)

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_back(t, s=1.4):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1
def ease_in_cubic(t): t = clamp(t); return t * t * t
def ease_out_cubic(t): t = clamp(t) - 1; return t * t * t + 1
def ease_in_out_sine(t): t = clamp(t); return -(math.cos(math.pi * t) - 1) / 2

def entrance(t, start, dur=0.45):
    """0..1 progress (with overshoot) for an element entering at `start`."""
    return ease_out_back((t - start) / dur) if t >= start else 0.0

def exit_(t, end, dur=0.25):
    """1..0 opacity factor for an element leaving at `end`."""
    return 1.0 - ease_in_cubic((t - (end - dur)) / dur) if t > end - dur else 1.0

def idle(t, seed=0.0, amp=5.0, period=2.6):
    """Constant micro-motion: (dy, scale, angle) floating offsets."""
    ph = seed * 1.7
    dy = amp * math.sin(2 * math.pi * t / period + ph)
    sc = 1.0 + 0.012 * math.sin(2 * math.pi * t / (period * 1.3) + ph * 0.7)
    ang = 0.6 * math.sin(2 * math.pi * t / (period * 1.7) + ph * 1.3)
    return dy, sc, ang

# ---------- layers ----------
def chroma_cut(path, out=None):
    """Remove a green chroma background -> RGBA cropped to content."""
    im = Image.open(path).convert('RGB'); px = im.load(); w, h = im.size
    a = Image.new('L', (w, h)); ap = a.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            k = g - max(r, b)
            ap[x, y] = 0 if (g > 90 and k > 40) else (128 if (g > 80 and k > 20) else 255)
            if k > 10:  # despill
                px[x, y] = (r, min(g, max(r, b) + 10), b)
    a = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    rgba = im.convert('RGBA'); rgba.putalpha(a)
    bb = a.point(lambda v: 255 if v > 30 else 0).getbbox(); rgba = rgba.crop(bb)
    if out: rgba.save(out)
    return rgba

def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def place(canvas, layer, cx, cy, scale=1.0, angle=0.0, alpha=1.0):
    """Composite RGBA `layer` centred at (cx,cy) with scale/rotation/opacity."""
    if alpha <= 0.01: return canvas
    l = layer
    if abs(scale - 1) > 1e-3: l = l.resize((max(1, int(l.width * scale)), max(1, int(l.height * scale))), Image.BILINEAR)
    if abs(angle) > 0.05: l = l.rotate(angle, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = l.split()[3].point(lambda v: int(v * alpha)); l = l.copy(); l.putalpha(a)
    canvas.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))
    return canvas

def parallax_frame(bg_big, mid, fg, cam, t, mid_pos, fg_pos, mid_scale=1.0, fg_scale=1.0):
    """cam = camera offset in px (x,y). Speeds: bg .25, mid .6, fg 1.2."""
    cx, cy = cam
    bw, bh = bg_big.size
    x = (bw - W) / 2 - cx * 0.25; y = (bh - H) / 2 - cy * 0.25
    frame = bg_big.crop((int(x), int(y), int(x) + W, int(y) + H)).convert('RGBA')
    dy, sc, ang = idle(t, 0.3, amp=6)
    place(frame, mid, mid_pos[0] - cx * 0.6, mid_pos[1] - cy * 0.6 + dy, mid_scale * sc, ang)
    if fg is not None:
        dy2, sc2, ang2 = idle(t, 1.9, amp=9, period=3.4)
        place(frame, fg, fg_pos[0] - cx * 1.2, fg_pos[1] - cy * 1.2 + dy2, fg_scale * sc2, ang2 * 2)
    return frame

# ---------- particles ----------
class Embers:
    """Warm floating light particles, always moving (micro-motion)."""
    def __init__(self, n=40, seed=7):
        import random; r = random.Random(seed)
        self.p = [(r.uniform(0, W), r.uniform(0, H), r.uniform(1.5, 4.5), r.uniform(20, 60), r.uniform(0, 6.28)) for _ in range(n)]
    def draw(self, frame, t, color=(255, 190, 90), alpha=1.0):
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for x, y, r, sp, ph in self.p:
            yy = (y - sp * t) % H; xx = x + 18 * math.sin(t * 0.8 + ph)
            a = int(160 * alpha * (0.5 + 0.5 * math.sin(t * 2 + ph)))
            d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=color + (a,))
        ov = ov.filter(ImageFilter.GaussianBlur(1.5)); frame.alpha_composite(ov); return frame

# ---------- energy saber slash transition ----------
def saber_slash(img_a, img_b, p, color=(255, 170, 40), angle_deg=-28):
    """p 0..1. Glowing line sweeps diagonally, then A splits in two halves
    that slide apart revealing B. Returns RGB frame."""
    a = img_a.convert('RGBA'); b = img_b.convert('RGBA')
    ang = math.radians(angle_deg); nx, ny = -math.sin(ang), math.cos(ang)  # line normal
    cx, cy = W / 2, H / 2
    sweep = ease_out_cubic(p / 0.45)          # line draws across
    split = ease_in_cubic((p - 0.4) / 0.6)    # halves separate
    # masks for the two halves
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    L = 3000; dx, dy = math.cos(ang) * L, math.sin(ang) * L
    poly = [(cx - dx, cy - dy), (cx + dx, cy + dy), (cx + dx + nx * L, cy + dy + ny * L), (cx - dx + nx * L, cy - dy + ny * L)]
    d.polygon(poly, fill=255)
    off = 900 * split
    out = b.copy()
    half1 = a.copy(); half1.putalpha(m)
    half2 = a.copy(); half2.putalpha(Image.eval(m, lambda v: 255 - v))
    out.alpha_composite(half1, (int(nx * off), int(ny * off)))
    out.alpha_composite(half2, (int(-nx * off), int(-ny * off)))
    # glowing line
    if p < 0.85:
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(ov)
        t0 = -1.0; t1 = -1.0 + 2.0 * sweep
        p0 = (cx + dx * t0 / 2.2, cy + dy * t0 / 2.2); p1 = (cx + dx * t1 / 2.2, cy + dy * t1 / 2.2)
        fade = 1 - clamp((p - 0.55) / 0.3)
        for wdt, al in ((70, 60), (40, 110), (18, 200)):
            gd.line((p0, p1), fill=color + (int(al * fade),), width=wdt)
        glow = ov.filter(ImageFilter.GaussianBlur(18))
        core = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(core).line((p0, p1), fill=(255, 255, 240, int(255 * fade)), width=7)
        out.alpha_composite(glow); out.alpha_composite(glow); out.alpha_composite(core)
    if 0.38 < p < 0.55:  # flash
        fl = 1 - abs((p - 0.465) / 0.085)
        out = Image.blend(out, Image.new('RGBA', (W, H), (255, 240, 210, 255)), 0.45 * clamp(fl))
    return out

# ---------- text with easing ----------
def text_layer(txt, f, fill=(255, 255, 255), stroke=6, sf=(0, 0, 0), pill=None, pad=(46, 22)):
    lines = txt.split('\n'); d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    lh = int(f.size * 1.15); w = int(max(d0.textlength(l, font=f) for l in lines)); h = lh * len(lines)
    pw, ph = (pad if pill else (stroke * 2, stroke * 2))
    im = Image.new('RGBA', (w + pw * 2, h + ph * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if pill: d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=min(60, im.height // 2), fill=pill)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=f)
        d.text(((im.width - lw) / 2, ph + i * lh), l, font=f, fill=fill, stroke_width=0 if pill else stroke, stroke_fill=sf)
    return im

def animate_in(frame, layer, t, start, cx, cy, end=None, seed=0.0, rise=80):
    """Staggered entrance with overshoot + idle micro-motion + eased exit."""
    if t < start or (end is not None and t >= end): return frame
    k = entrance(t, start); a = clamp((t - start) / 0.2) * (exit_(t, end) if end else 1.0)
    dy, sc, ang = idle(t, seed, amp=4)
    place(frame, layer, cx, cy + rise * (1 - k) + dy, (0.85 + 0.15 * k) * sc, ang * 0.5, a)
    return frame
