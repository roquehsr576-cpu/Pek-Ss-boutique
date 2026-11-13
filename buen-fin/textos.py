"""Genera los textos (PNG transparentes) que se superponen al video del Buen Fin."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 720, 1280
FONT = Path(__file__).resolve().parent.parent / "historias-ig" / "fonts" / "SpaceGrotesk-Bold.ttf"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "textos")
OUT.mkdir(exist_ok=True)

ROJO = (214, 31, 38)
ROSA = (233, 79, 140)
TURQUESA = (0, 150, 160)
BLANCO = (255, 255, 255)
NARANJA = (247, 140, 30)
NEGRO = (20, 20, 20)


def font(size):
    f = ImageFont.truetype(str(FONT), size)
    try:
        f.set_variation_by_axes([700])
    except Exception:
        pass
    return f


def placa(lineas, y0, nombre, fondo=None):
    """lineas: lista de (texto, tamaño, color_relleno, color_borde).
    fondo: color de una placa redondeada detrás del texto (estilo Buen Fin)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sombra)
    if fondo:
        alto = sum(int(s * 1.08) for _, s, _, _ in lineas)
        caja = (30, y0 - 28, W - 30, y0 + alto + 22)
        ds.rounded_rectangle(tuple(v + o for v, o in zip(caja, (6, 12, 6, 12))), 40, fill=(0, 0, 0, 110))
        d.rounded_rectangle(caja, 40, fill=fondo, outline=NEGRO, width=8)
    y = y0
    for texto, size, relleno, borde in lineas:
        f = font(size)
        # Reduce el tamaño si no cabe en el ancho
        while d.textlength(texto, font=f) > W - 60:
            size -= 4
            f = font(size)
        w = d.textlength(texto, font=f)
        x = (W - w) / 2
        stroke = max(4, size // 11)
        ds.text((x + 4, y + 8), texto, font=f, fill=(0, 0, 0, 120), stroke_width=stroke, stroke_fill=(0, 0, 0, 120))
        d.text((x, y), texto, font=f, fill=relleno, stroke_width=stroke, stroke_fill=borde)
        y += int(size * 1.08)
    sombra = sombra.filter(ImageFilter.GaussianBlur(6))
    Image.alpha_composite(sombra, img).save(OUT / f"{nombre}.png")


def calendario(arriba, grande, franja, nombre, y0=110, tam=150):
    """Tarjeta tipo calendario (blanca, letras negras, franja roja abajo)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sombra)
    x0, x1 = 80, W - 80
    f_arriba, f_grande, f_franja = font(54), font(tam), font(46)
    lineas = grande.split("\n")
    alto = 70 + 64 + len(lineas) * int(tam * 0.98) + 20 + 96
    y1 = y0 + alto
    ds.rounded_rectangle((x0 + 14, y0 + 18, x1 + 14, y1 + 18), 26, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=BLANCO, outline=NEGRO, width=10)
    d.rounded_rectangle((x0 + 5, y1 - 96, x1 - 5, y1 - 5), 20, fill=ROJO)
    d.rectangle((x0 + 5, y1 - 96, x1 - 5, y1 - 70), fill=ROJO)
    for cx in (x0 + 150, x1 - 150):  # argollas del calendario
        d.ellipse((cx - 14, y0 + 26, cx + 14, y0 + 54), fill=NEGRO)
    y = y0 + 70
    d.text((W / 2, y), arriba, font=f_arriba, fill=NEGRO, anchor="mt")
    y += 64
    for linea in lineas:
        d.text((W / 2, y), linea, font=f_grande, fill=NEGRO, anchor="mt")
        y += int(tam * 0.98)
    d.text((W / 2, y1 - 50), franja, font=f_franja, fill=BLANCO, anchor="mm")
    sombra = sombra.filter(ImageFilter.GaussianBlur(8))
    Image.alpha_composite(sombra, img).save(OUT / f"{nombre}.png")


calendario("¡YA LLEGÓ EL", "BUEN\nFIN :)", "en PeK'sS", "t1", y0=70, tam=128)
placa([("¡10% DE", 120, BLANCO, ROSA), ("DESCUENTO!", 110, ROSA, BLANCO), ("en toda la tienda", 56, BLANCO, ROSA)], 120, "t2")
calendario("DOMINGO", "15", "de noviembre", "t3", y0=80, tam=200)
placa([("¡Ven, visítanos!", 72, BLANCO, ROJO), ("Ese regalo para ESE momento", 40, ROJO, BLANCO),
       ("¡Se terminan pronto!", 50, BLANCO, ROJO)], 130, "t4")
print("ok", sorted(p.name for p in OUT.iterdir()))
