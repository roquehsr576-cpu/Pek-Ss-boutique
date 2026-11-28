"""Animated map of Mexico lighting up the four main coffee states (SADER 2022 shares)."""
import json, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

GOLD = (240, 196, 102); CREAM = (255, 246, 232)
STATES = [("MX-CHP", "CHIAPAS", "38 %", (-30, 70)), ("MX-VER", "VERACRUZ", "24 %", (120, -40)),
          ("MX-PUE", "PUEBLA", "20 %", (-110, -150)), ("MX-OAX", "OAXACA", "9 %", (-200, 80))]
SRC = "Producción de café por estado · SADER (2022)"

def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)

class Mapa:
    def __init__(self, W, H, fd, geo):
        self.W, self.H = W, H
        feats = json.load(open(geo))["features"]
        lon0, lon1, lat0, lat1 = -118.5, -85.5, 33.0, 13.8
        k = math.cos(math.radians(23))
        self.sc = (W * 1.9) / ((lon1 - lon0) * k)          # big canvas, we zoom into the south
        self.MW = int((lon1 - lon0) * k * self.sc); self.MH = int((lat0 - lat1) * self.sc)
        P = lambda lo, la: ((lo - lon0) * k * self.sc, (lat0 - la) * self.sc)
        self.P = P
        self.polys = {}
        for f in feats:
            g = f["geometry"]; ps = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            self.polys[f["properties"]["id"]] = [[P(lo, la) for lo, la in p[0]] for p in ps]
        base = Image.new("RGB", (self.MW, self.MH), (22, 14, 9))
        d = ImageDraw.Draw(base)
        for pid, ps in self.polys.items():
            for p in ps: d.polygon(p, fill=(92, 62, 38), outline=(150, 108, 70))
        self.base = base
        self.cent = {pid: (sum(x for p in ps for x, _ in p) / sum(len(p) for p in ps),
                           sum(y for p in ps for _, y in p) / sum(len(p) for p in ps)) for pid, ps in self.polys.items()}
        self.big = ImageFont.truetype(f"{fd}/Anton-Regular.ttf", 64)
        self.pct = ImageFont.truetype(f"{fd}/Anton-Regular.ttf", 54)
        self.src = ImageFont.truetype(f"{fd}/Oswald.ttf", 30); self.src.set_variation_by_axes([400])
        self.ttl = ImageFont.truetype(f"{fd}/Oswald.ttf", 56); self.ttl.set_variation_by_axes([600])

    def frame(self, t, dur, lights=(2.2, 3.0, 3.8, 4.4), total_at=8.0, zoom=2.0):
        """u: 0..1 over the shot; states light up one by one over the first 70 %."""
        # camera: from whole country to the south-east coffee belt
        z = ease(t / zoom) if zoom else 1.0
        cx0, cy0, w0 = self.MW / 2, self.MH / 2, self.MW
        cx1, cy1 = self.P(-95.3, 19.8); w1 = self.MW * 0.5
        cx, cy, vw = cx0 + (cx1 - cx0) * z, cy0 + (cy1 - cy0) * z, w0 + (w1 - w0) * z
        vh = vw * self.H / self.W
        box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
        canvas = Image.new("RGB", (int(vw), int(vh)), (22, 14, 9))
        sx0, sy0 = max(0, int(box[0])), max(0, int(box[1])); sx1, sy1 = min(self.MW, int(box[2])), min(self.MH, int(box[3]))
        canvas.paste(self.base.crop((sx0, sy0, sx1, sy1)), (sx0 - int(box[0]), sy0 - int(box[1])))
        fr = canvas.resize((self.W, self.H), Image.BILINEAR).convert("RGBA")
        s = self.W / vw
        T = lambda p: ((p[0] - box[0]) * s, (p[1] - box[1]) * s)
        lay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        glow = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
        txt = []
        for i, (pid, name, pct, off) in enumerate(STATES):
            a = ease((t - lights[i]) / 0.35)
            if a <= 0: continue
            for p in self.polys[pid]:
                q = [T(v) for v in p]
                d.polygon(q, fill=GOLD + (int(225 * a),), outline=(255, 240, 200, int(255 * a)))
                g.line(q + [q[0]], fill=GOLD + (int(200 * a),), width=14)
            cx_, cy_ = T(self.cent[pid]); txt.append((cx_ + off[0], cy_ + off[1], name, pct, a))
        fr.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12))); fr.alpha_composite(lay)
        top = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0)); d = ImageDraw.Draw(top)
        for x, y, name, pct, a in txt:
            al = int(255 * a)
            d.text((x, y), name, font=self.big, fill=CREAM + (al,), anchor="mm", stroke_width=6, stroke_fill=(20, 10, 4, al))
            d.text((x, y + 62), pct, font=self.pct, fill=GOLD + (al,), anchor="mm", stroke_width=6, stroke_fill=(20, 10, 4, al))
        if total_at is not None:
            a = int(255 * ease((t - total_at) / 0.4))
            d.text((self.W / 2, 420), "≈ 90 % DEL CAFÉ DE MÉXICO", font=self.ttl, fill=GOLD + (a,), anchor="mm", stroke_width=5, stroke_fill=(20, 10, 4, a))
        d.text((self.W / 2, 1830), SRC, font=self.src, fill=(200, 185, 165, 220), anchor="mm")
        fr.alpha_composite(top)
        return fr.convert("RGB")
