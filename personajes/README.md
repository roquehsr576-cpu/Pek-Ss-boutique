# Personajes: la cafetera y la taza (Dulce Café)

Fuente: `post_original_vapor_que_me_eleva.png`, el post viral de la página ("El vapor que me eleva", grito "¡Uuuuulalá!").

| Archivo | Qué es |
|---|---|
| `taza.png` | Taza recortada, fondo transparente (ojos cerrados, sonrojada, con un corazoncito rojo en la mano). |
| `cafetera.png` | Cafetera italiana recortada, fondo transparente (ojos cerrados, besito, mano en la mejilla). |
| `post_original_vapor_que_me_eleva.png` | Imagen original completa (940×788). |
| `anim_cafetera_y_taza.py` | Script que generó `dulce_cafe_cafetera_y_taza.mp4`. |
| `logo_redibujar.py` | Redibuja el logo circular (el logo oficial está en `../dulce_cafe_logo_oficial_hd.png`). |

## Notas

- Solo existe **una pose/expresión** de cada personaje: la del post original. Las emociones del video (cansada, contenta, hablando)
  se lograron con transformaciones: escala (squash/stretch), inclinación, saltos y rebote según el volumen de la voz.
  Para poses nuevas habría que dibujarlas o generarlas tomando estos PNG como referencia.
- Fondo original: durazno plano `rgb(248, 196, 149)`. Sombras en el piso: elipses café `rgb(181, 110, 50)`.
- En el video, la taza se escaló ×1.45 y la cafetera ×1.4, con el piso en y=1460 de un lienzo de 1080×1920.
- `anim_cafetera_y_taza.py` espera en su carpeta `cup.png`, `moka.png`, `logo_hd.png` y `aud/` con las voces
  (`set.mp3`, `kate.mp3`, `set9.mp3`). Aquí se llaman `taza.png` y `cafetera.png`; renómbralos o ajusta el script.
- Voces: cafetera = "Set" (ElevenLabs `M3vcCGICiYlMoOxWIVIl`), taza = "Kate 7" (`U9tZtg3uJtVgXPkvosWR`), modelo `eleven_v4`.
