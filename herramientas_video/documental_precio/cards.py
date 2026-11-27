"""News/data cards for 'El verdadero precio del café': date and place, then the prices in Mexican pesos.

No photos of the march exist, so the news part is told with honest data cards over a darkened,
blurred real photo of a coffee farm, with the source in small print.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

GOLD = (240, 196, 102)
CREAM = (255, 246, 232)
RED = (232, 96, 80)
GREEN = (120, 200, 140)
SOURCE = "Fuente: La Jornada, El Imparcial y otros medios · 23–25 nov 2026"

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

class Cards:
    def __init__(self, W, H, fd, bg_img):
        self.W, self.H = W, H
        bg = bg_img.convert("RGB")
        sc = max(W / bg.width, H / bg.height) * 1.1
        bg = bg.resize((int(bg.width * sc), int(bg.height * sc)), Image.LANCZOS)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width + W) // 2, (bg.height + H) // 2))
        bg = bg.filter(ImageFilter.GaussianBlur(14))
        self.bg = Image.blend(bg, Image.new("RGB", (W, H), (14, 9, 6)), 0.72)
        self.big = ImageFont.truetype(f"{fd}/Anton-Regular.ttf", 210)
        self.mid = ImageFont.truetype(f"{fd}/Anton-Regular.ttf", 96)
        self.lab = ImageFont.truetype(f"{fd}/Oswald.ttf", 52); self.lab.set_variation_by_axes([600])
        self.src = ImageFont.truetype(f"{fd}/Oswald.ttf", 30); self.src.set_variation_by_axes([400])

    def _base(self, t):
        z = 1 + 0.03 * ease(t / 6)
        w, h = int(self.W / z), int(self.H / z)
        im = self.bg.crop(((self.W - w) // 2, (self.H - h) // 2, (self.W + w) // 2, (self.H + h) // 2)).resize((self.W, self.H))
        return im.convert("RGBA")

    def fecha(self, u, t):
        """23 NOV 2026 · Tapachula, Chiapas."""
        im = self._base(t); d = ImageDraw.Draw(im)
        a = int(255 * ease(u / 0.12))
        d.text((self.W / 2, 760), "23 DE NOVIEMBRE", font=self.mid, fill=GOLD + (a,), anchor="mm")
        d.text((self.W / 2, 880), "2026", font=self.mid, fill=CREAM + (a,), anchor="mm")
        b = int(255 * ease((u - 0.25) / 0.15))
        d.line([(self.W / 2 - 220, 960), (self.W / 2 + 220, 960)], fill=GOLD + (b,), width=4)
        d.text((self.W / 2, 1040), "TAPACHULA, CHIAPAS", font=self.lab, fill=CREAM + (b,), anchor="mm")
        d.text((self.W / 2, 1110), "cafeticultores marchan por un precio justo", font=self.lab, fill=(220, 205, 185, b), anchor="mm")
        d.text((self.W / 2, 1830), SOURCE, font=self.src, fill=(200, 185, 165, 220), anchor="mm")
        return im.convert("RGB")

    def _counter(self, d, y, label, value, prog, col, a):
        v = int(round(value * ease(prog)))
        d.text((self.W / 2, y - 120), label, font=self.lab, fill=CREAM + (a,), anchor="mm")
        d.text((self.W / 2, y + 20), f"{v} pesos", font=self.big, fill=col + (a,), anchor="mm")
        d.text((self.W / 2, y + 150), "por kilo de café robusta", font=self.src, fill=(220, 205, 185, a), anchor="mm")

    def pagan(self, u, t):
        """43 vs 45: they are paid less than it costs."""
        im = self._base(t); d = ImageDraw.Draw(im)
        a1 = int(255 * ease(u / 0.1))
        self._counter(d, 640, "LES PAGAN", 43, u / 0.35, RED, a1)
        if u > 0.45:
            a2 = int(255 * ease((u - 0.45) / 0.1))
            self._counter(d, 1180, "PRODUCIRLO LES CUESTA (aprox.)", 45, (u - 0.45) / 0.35, CREAM, a2)
        d.text((self.W / 2, 1790), "Dato: caficultor Eduardo Camarena", font=self.src, fill=(200, 185, 165, 220), anchor="mm")
        d.text((self.W / 2, 1830), SOURCE, font=self.src, fill=(200, 185, 165, 220), anchor="mm")
        return im.convert("RGB")

    def piden(self, u, t):
        """They ask for at least 55 pesos per kilo."""
        im = self._base(t); d = ImageDraw.Draw(im)
        a = int(255 * ease(u / 0.12))
        self._counter(d, 900, "PIDEN AL MENOS", 55, u / 0.4, GREEN, a)
        b = int(255 * ease((u - 0.5) / 0.15))
        d.text((self.W / 2, 1180), "y una mesa para dialogar", font=self.lab, fill=CREAM + (b,), anchor="mm")
        d.text((self.W / 2, 1830), SOURCE, font=self.src, fill=(200, 185, 165, 220), anchor="mm")
        return im.convert("RGB")
