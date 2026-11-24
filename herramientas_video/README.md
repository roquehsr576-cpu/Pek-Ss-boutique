# Herramientas de video (reels educativos estilo "Dulce Café")

Scripts en Python (Pillow + numpy) que generan los cuadros del video y los mandan a `ffmpeg`.
Se usaron para la serie de Dulce Café y sirven para cualquier otra página o marca (por ejemplo, ganoderma).

## Qué hay aquí

| Script | Para qué sirve |
|---|---|
| `episodio_reel.py` | Episodio educativo: ilustraciones con movimiento de cámara, gancho de portada, subtítulos palabra por palabra sincronizados con la voz, etiquetas de datos. |
| `logo_sting.py` | Cierre de marca: el logo da una vuelta lenta tipo moneda, anillo dorado y destello. |
| `logo_redibujar.py` | Redibuja un logo circular en alta resolución (textos editables por argumento). |
| `frases_grano_partido.py` | Reel de frases: letras una por una y un grano tostado que se parte con café molido cayendo. |
| `promo_premium.py` | Reel premium: fondo espresso, granos cayendo en 3 capas, tipografía elegante al ritmo de la música. |

## Fuentes (Google Fonts)

Descargar en una carpeta `fonts/` desde `https://raw.githubusercontent.com/google/fonts/main/`:
`ofl/lilitaone/LilitaOne-Regular.ttf`, `ofl/anton/Anton-Regular.ttf`, `ofl/oswald/Oswald[wght].ttf` (guardar como `Oswald.ttf`),
`ofl/playfairdisplay/PlayfairDisplay[wght].ttf` (como `PlayfairDisplay.ttf`), `ofl/rubikdirt/RubikDirt-Regular.ttf`,
`ofl/greatvibes/GreatVibes-Regular.ttf`.

## Receta de un episodio (la fórmula que funciona)

1. **Guion** de 35–50 s: gancho que contradice algo cotidiano ("NUNCA hiervas tu café"), explicación simple,
   dato de origen de la marca, y cierre con **pregunta abierta** (nunca "comenta / comparte / sigue": Facebook lo penaliza).
   Revisar que cada dato sea verídico antes de producir.
2. **Voz**: ElevenLabs, modelo `eleven_v4`, con etiquetas de emoción (`[curious]`, `[warmly]`, `[proudly]`).
3. **Ilustraciones**: Higgsfield, modelo `z_image` (funciona en plan gratis, 0.15 créditos c/u), formato `9:16`.
   Prompt base: *"Stylized 3D render, warm cinematic lighting, rich detail. … Dark warm background with bokeh.
   Subject slightly low, empty dark space in the top third. No text, no logos."*
   El plan gratis permite **una imagen a la vez**. Revisar que cada imagen sea verídica antes de usarla.
4. **Pausas de la voz** para sincronizar subtítulos:
   `ffmpeg -i voz.mp3 -af silencedetect=n=-36dB:d=0.18 -f null -`
   Con esos tiempos se llenan `SEGS` (texto por tramo) y `SHOTS` (imagen por tramo) en `episodio_reel.py`.
5. **Render**:
   ```bash
   python3 episodio_reel.py <carpeta con img0.png…> <fonts> <logo.png> | \
     ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - -c:v libx264 -crf 18 -pix_fmt yuv420p main.mp4
   python3 logo_sting.py <logo.png> <fonts> 1080 1920 7.5 | \
     ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - -c:v libx264 -crf 18 -pix_fmt yuv420p sting.mp4
   ```
6. **Mezcla**: unir `main.mp4` + `sting.mp4`, voz normalizada y música baja que se agacha cuando hay voz:
   ```
   [voz]loudnorm=I=-15,asplit=2[vo][sc];
   [musica]volume=0.40[mu]; [mu][sc]sidechaincompress=threshold=0.015:ratio=12:attack=20:release=500[duck];
   [vo][duck]amix=inputs=2:normalize=0
   ```

## Reglas acordadas para los próximos videos

- **Sin logo pequeño en la esquina** durante el video; la marca va solo en el cierre (logo girando, 3 s).
- **Gancho visible desde el primer cuadro** (sin fundido), algo cambia cada 2–3 s, 30–40 s en total.
- **Educativos sin llamado a comprar** en el video ("pide el tuyo", precios): la venta va en el texto de la publicación.
- Los reels de venta se hacen aparte, pensados para pautar.
- Preferir **fotos y videos reales** del origen; ilustraciones solo para lo que no se puede fotografiar.

## Para adaptar a otra marca

En `episodio_reel.py` cambiar: textos del gancho (`hook`), la etiqueta (`STICKER`), `SEGS`, `KEYS`, `SHOTS`, `TAGS`
y la paleta (`GOLD`, `CREAM`, `DARK`). En `logo_sting.py` cambiar el texto bajo el logo.
