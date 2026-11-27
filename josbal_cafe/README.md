# Reels educativos de JOSBAL Café

Formato "La receta en números": gráficos animados sobre fondo oscuro con los colores del logo
(café oscuro, crema, caramelo y rojo), **sin logo ni nombre** hasta que los videos empiecen a pegar.
Solo enseñanza, hecho para compartirse; nunca pedir "comenta / comparte / sigue".

| Video | Tema | Duración |
|---|---|---|
| `josbal_receta_goteo_1a16.mp4` | Café de goteo: la regla 1:16 | 44 s |
| `papas_a_la_francesa_doble_fritura.mp4` | Papas a la francesa: doble fritura 160 °C → 180 °C | 53 s |

## Cómo se hizo

1. Voz: ElevenLabs, voz "Set", modelo `eleven_v4`.
2. Pausas para sincronizar subtítulos: `ffmpeg -i voz.mp3 -af silencedetect=n=-36dB:d=0.15 -f null -`
   (los tiempos van en `PHRASES` del script).
3. Gráficos (fuentes Anton y Oswald de Google Fonts en una carpeta `fonts/`):
   ```bash
   python3 herramientas/receta_en_numeros_goteo.py fonts 0 44 | \
     ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - -c:v libx264 -crf 18 -pix_fmt yuv420p main.mp4
   ffmpeg -i main.mp4 -i voz.mp3 -filter_complex "[1:a]loudnorm=I=-15:TP=-1.5,apad[a]" \
     -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest video.mp4
   ```
   Para revisar un cuadro suelto: `python3 herramientas/receta_en_numeros_goteo.py fonts 0 0 <segundo> cuadro.png`
