#!/usr/bin/env python3
"""Marca de agua DECOMPIS para fotos y videos.

Pone dos capas, ambas leves:
  1. El logo circular de DECOMPIS en el centro (semitransparente).
  2. La palabra "DECOMPIS" repetida en diagonal sobre toda la imagen, muy tenue,
     para que no se pueda quitar recortando la esquina.

Uso:
  python3 marca/marca_agua.py foto1.jpg foto2.png video.mp4 ...
  python3 marca/marca_agua.py carpeta/            (procesa todo lo de la carpeta)

Opciones:
  --salida DIR       carpeta donde guardar (por defecto: marca/con_marca/)
  --esquina POS      centro (defecto), abajo-derecha, abajo-izquierda, arriba-derecha, arriba-izquierda
  --logo-opacidad N  0-100, opacidad del logo (defecto 25 en el centro, 45 en esquina)
  --texto-opacidad N 0-100, opacidad del texto repetido (defecto 7; 0 lo quita)
"""
import argparse
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
LOGO = AQUI / "logo" / "decompis_logo.png"
FUENTE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FOTOS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEOS = {".mp4", ".mov", ".m4v", ".webm"}


def capa_marca(ancho, alto, esquina, logo_op, texto_op):
    """Crea una capa transparente del tamaño de la imagen con la marca de agua."""
    capa = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    lado = min(ancho, alto)

    # 1. Texto repetido en diagonal
    if texto_op > 0:
        tam = max(18, lado // 16)
        fuente = ImageFont.truetype(FUENTE, tam)
        diag = int(math.hypot(ancho, alto))
        lienzo = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
        d = ImageDraw.Draw(lienzo)
        texto = "DECOMPIS"
        tw = d.textlength(texto, font=fuente)
        paso_x, paso_y = int(tw * 1.9), int(tam * 4.2)
        alfa = int(255 * texto_op / 100)
        for fila, y in enumerate(range(0, diag, paso_y)):
            desfase = (paso_x // 2) * (fila % 2)
            for x in range(-paso_x, diag, paso_x):
                d.text((x + desfase, y), texto, font=fuente, fill=(255, 255, 255, alfa),
                       stroke_width=max(1, tam // 30), stroke_fill=(0, 0, 0, alfa // 2))
        lienzo = lienzo.rotate(30, resample=Image.BICUBIC)
        izq, arr = (diag - ancho) // 2, (diag - alto) // 2
        capa.alpha_composite(lienzo.crop((izq, arr, izq + ancho, arr + alto)))

    # 2. Logo en la esquina
    if logo_op > 0:
        logo = Image.open(LOGO).convert("RGBA")
        centro = esquina == "centro"
        t = max(60, int(lado * (0.32 if centro else 0.17)))
        logo = logo.resize((t, t), Image.LANCZOS)
        a = logo.getchannel("A").point(lambda v: int(v * logo_op / 100))
        logo.putalpha(a)
        m = int(lado * 0.035)
        if centro:
            x, y = (ancho - t) // 2, (alto - t) // 2
        else:
            x = m if "izquierda" in esquina else ancho - t - m
            y = m if "arriba" in esquina else alto - t - m
        capa.alpha_composite(logo, (x, y))
    return capa


def marcar_foto(src, dst, args):
    im = Image.open(src)
    im = im.convert("RGBA")
    im.alpha_composite(capa_marca(*im.size, args.esquina, args.logo_opacidad, args.texto_opacidad))
    if dst.suffix.lower() in {".jpg", ".jpeg"}:
        im.convert("RGB").save(dst, quality=95)
    else:
        im.save(dst)


def marcar_video(src, dst, args):
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0:s=x", str(src)],
        capture_output=True, text=True, check=True).stdout.strip()
    ancho, alto = map(int, salida.split("x")[:2])
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "marca.png"
        capa_marca(ancho, alto, args.esquina, args.logo_opacidad, args.texto_opacidad).save(png)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-i", str(png),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto",
             "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
             "-c:a", "copy", "-movflags", "+faststart", str(dst)],
            check=True)


def main():
    p = argparse.ArgumentParser(description="Marca de agua DECOMPIS")
    p.add_argument("archivos", nargs="+")
    p.add_argument("--salida", default=str(AQUI / "con_marca"))
    p.add_argument("--esquina", default="centro",
                   choices=["centro", "abajo-derecha", "abajo-izquierda", "arriba-derecha", "arriba-izquierda"])
    p.add_argument("--logo-opacidad", type=int, default=None)
    p.add_argument("--texto-opacidad", type=int, default=7)
    args = p.parse_args()
    if args.logo_opacidad is None:
        args.logo_opacidad = 25 if args.esquina == "centro" else 45

    entradas = []
    for a in args.archivos:
        ruta = Path(a)
        entradas += sorted(f for f in ruta.iterdir() if f.is_file()) if ruta.is_dir() else [ruta]

    out = Path(args.salida)
    out.mkdir(parents=True, exist_ok=True)
    hechos = 0
    for src in entradas:
        ext = src.suffix.lower()
        if ext in FOTOS:
            dst = out / f"{src.stem}_decompis{ext}"
            marcar_foto(src, dst, args)
        elif ext in VIDEOS:
            dst = out / f"{src.stem}_decompis.mp4"
            marcar_video(src, dst, args)
        else:
            continue
        hechos += 1
        print(f"✓ {dst}")
    if not hechos:
        sys.exit("No encontré fotos ni videos para marcar.")


if __name__ == "__main__":
    main()
