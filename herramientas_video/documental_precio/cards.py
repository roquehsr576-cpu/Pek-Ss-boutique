"""News/data cards for 'El verdadero precio del café' (figures in Mexican pesos).

No photos of the march exist, so the news is told with data cards over a darkened, blurred real photo,
with the source in small print. Times are seconds into the card (t) so numbers land on the narration.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

GOLD = (240, 196, 102)
CREAM = (255, 246, 232)
RED = (232, 96, 80)
GREEN = (120, 200, 140)
SOFT = (220, 205, 185)
SRC_CHIS = "Fuente: La Jornada, El Imparcial y otros medios · 23–25 nov 2026"
SRC_VER = "Fuente: Golpe Político y XEU Noticias · oct 2026"

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
        self.big = ImageFont.truetype(f"{fd}/Anton-Regular.ttf", 200)
        self.mid = ImageFont.truetype(f"{fd}/Anton-Regular.ttf", 96)
        self.lab = ImageFont.truetype(f"{fd}/Oswald.ttf", 52); self.lab.set_variation_by_axes([600])
        self.src = ImageFont.truetype(f"{fd}/Oswald.ttf", 30); self.src.set_variation_by_axes([400])
        self.unit = ImageFont.truetype(f"{fd}/Oswald.ttf", 36); self.unit.set_variation_by_axes([500])

    def _base(self, t):
        z = 1 + 0.03 * ease(t / 8)
        w, h = int(self.W / z), int(self.H / z)
        im = self.bg.crop(((self.W - w) // 2, (self.H - h) // 2, (self.W + w) // 2, (self.H + h) // 2)).resize((self.W, self.H))
        top = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        return im.convert("RGBA"), top, ImageDraw.Draw(top)

    def _done(self, im, top, src, extra=None):
        d = ImageDraw.Draw(top)
        if extra: d.text((self.W / 2, 1785), extra, font=self.src, fill=(200, 185, 165, 220), anchor="mm")
        d.text((self.W / 2, 1830), src, font=self.src, fill=(200, 185, 165, 220), anchor="mm")
        im.alpha_composite(top)
        return im.convert("RGB")

    def _counter(self, d, y, label, value, prog, col, a, unit):
        v = int(round(value * ease(prog)))
        d.text((self.W / 2, y - 125), label, font=self.lab, fill=CREAM + (a,), anchor="mm")
        d.text((self.W / 2, y + 15), f"{v} pesos", font=self.big, fill=col + (a,), anchor="mm")
        d.text((self.W / 2, y + 150), unit, font=self.unit, fill=SOFT + (a,), anchor="mm")

    def fecha(self, t, dur):
        im, top, d = self._base(t)
        a = int(255 * ease(t / 0.4))
        d.text((self.W / 2, 760), "23 DE NOVIEMBRE", font=self.mid, fill=GOLD + (a,), anchor="mm")
        d.text((self.W / 2, 880), "2026", font=self.mid, fill=CREAM + (a,), anchor="mm")
        b = int(255 * ease((t - 2.4) / 0.5))
        d.line([(self.W / 2 - 220, 960), (self.W / 2 + 220, 960)], fill=GOLD + (b,), width=4)
        d.text((self.W / 2, 1040), "TAPACHULA, CHIAPAS", font=self.lab, fill=CREAM + (b,), anchor="mm")
        c = int(255 * ease((t - 4.0) / 0.5))
        d.text((self.W / 2, 1110), "cafeticultores marchan por un precio justo", font=self.lab, fill=SOFT + (c,), anchor="mm")
        return self._done(im, top, SRC_CHIS)

    def pagan(self, t, dur):
        """'les pagan 43' lands at ~1.1 s, '45' at ~5.6 s into the card."""
        im, top, d = self._base(t)
        unit = "por kilo · café robusta de Chiapas"
        self._counter(d, 640, "LES PAGAN", 43, (t - 0.6) / 0.6, RED, int(255 * ease((t - 0.5) / 0.3)), unit)
        a2 = int(255 * ease((t - 3.8) / 0.3))
        if a2: self._counter(d, 1180, "PRODUCIRLO LES CUESTA (aprox.)", 45, (t - 4.9) / 0.7, CREAM, a2, unit)
        return self._done(im, top, SRC_CHIS, "Dato del costo: caficultor Eduardo Camarena")

    def piden(self, t, dur):
        im, top, d = self._base(t)
        a = int(255 * ease(t / 0.3))
        self._counter(d, 900, "PIDEN AL MENOS", 55, (t - 0.4) / 0.8, GREEN, a, "por kilo")
        b = int(255 * ease((t - 2.6) / 0.4))
        d.text((self.W / 2, 1190), "y una mesa para dialogar", font=self.lab, fill=CREAM + (b,), anchor="mm")
        return self._done(im, top, SRC_CHIS)

    def veracruz(self, t, dur):
        """'8 pesos' at ~4.5 s, '7 pesos' at ~9.1 s into the card."""
        im, top, d = self._base(t)
        a = int(255 * ease(t / 0.4))
        d.text((self.W / 2, 330), "VERACRUZ", font=self.mid, fill=GOLD + (a,), anchor="mm")
        d.text((self.W / 2, 420), "zona de Huatusco · inicio de cosecha", font=self.lab, fill=CREAM + (a,), anchor="mm")
        a1 = int(255 * ease((t - 3.4) / 0.3))
        if a1: self._counter(d, 760, "LLEGARON A OFRECER", 8, (t - 4.2) / 0.5, RED, a1, "por kilo de café cereza")
        a2 = int(255 * ease((t - 6.8) / 0.3))
        if a2: self._counter(d, 1260, "PAGAR EL CORTE CUESTA HASTA", 7, (t - 8.7) / 0.5, CREAM, a2, "por kilo cortado")
        return self._done(im, top, SRC_VER)
