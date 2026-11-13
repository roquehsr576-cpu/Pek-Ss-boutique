#!/bin/bash
# Une el clip animado con los textos y una tarjeta final de 3 s.
# Uso: bash armar.sh clip.mp4 salida.mp4 musica.mp3
set -e
cd "$(dirname "$0")"
CLIP="${1:-clip.mp4}"
MUSICA="${3:-musica.mp3}"
OUT="${2:-pekss_buen_fin.mp4}"
python3 textos.py textos >/dev/null

# Cada texto: entra con fundido + deslizamiento hacia abajo, sale con fundido.
# texto(n, inicio, fin)
txt() {
  local n=$1 s=$2 e=$3
  echo "[$n:v]format=rgba,fade=in:st=$s:d=0.4:alpha=1,fade=out:st=$(echo "$e-0.35" | bc):d=0.35:alpha=1[t$n];"
}
ov() {
  local prev=$1 n=$2 s=$3 e=$4 out=$5
  echo "[$prev][t$n]overlay=x=0:y='-70*max(0\,1-(t-$s)/0.45)':enable='between(t\,$s\,$e)'[$out];"
}

ffmpeg -y -loglevel error \
  -i "$CLIP" \
  -loop 1 -t 14 -i textos/t1.png \
  -loop 1 -t 14 -i textos/t2.png \
  -loop 1 -t 14 -i textos/t3.png \
  -loop 1 -t 14 -i textos/t4.png \
  -i "$MUSICA" \
  -filter_complex "\
[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,tpad=stop_mode=clone:stop_duration=3,setsar=1[base];\
$(txt 1 0.3 3.4)$(txt 2 3.6 6.6)$(txt 3 6.8 9.8)$(txt 4 10.1 13.5)\
$(ov base 1 0.3 3.4 v1)$(ov v1 2 3.6 6.6 v2)$(ov v2 3 6.8 9.8 v3)$(ov v3 4 10.1 13.5 v4)\
[v4]scale=1080:1920:flags=lanczos,format=yuv420p[v];\
[5:a]apad,afade=t=out:st=11.5:d=1.5[a]" \
  -map "[v]" -map "[a]" -t 13 -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "Listo: $OUT"
