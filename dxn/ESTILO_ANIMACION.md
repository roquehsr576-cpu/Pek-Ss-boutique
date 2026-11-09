# Guía de estilo de animación (todos los videos nuevos)

Estas reglas aplican a cada reel que se produzca para la página DXN a partir del Reel 8. Están programadas en `scripts/motion.py`.

## 1. Curvas con easing y rebote final

- Ningún elemento aparece de golpe ni se mueve en línea recta: todo usa curvas de aceleración.
- Entradas: `ease_out_back`, que pasa un poco del punto final y regresa (rebote pequeño, ~8–10 %).
- Salidas: `ease_in_cubic`, que acelera al irse.
- Movimientos de cámara: `ease_in_out_sine`, suave al empezar y al terminar.
- Duración típica de una entrada: 0.45 s.

## 2. Entradas escalonadas

- Cuando aparecen varios elementos (título, etiquetas, tarjetas), entran uno después de otro, nunca todos juntos.
- Separación entre elementos: 0.12–0.18 s.
- Orden: de arriba hacia abajo, o del más importante al menos importante.
- Cada elemento combina: subir 60–90 px + escala de 0.85 a 1 + opacidad de 0 a 1.

## 3. Paralaje en 3 capas

- Cada escena se separa en fondo, medio y frente.
- Velocidades relativas al movimiento de cámara:
  - Fondo: 0.25 (se mueve poco, se ve lejos)
  - Medio (sujeto: taza, producto): 0.6
  - Frente (granos, partículas, vapor): 1.2 (se mueve más que la cámara)
- Las capas de medio y frente se generan sobre fondo verde (chroma) y se recortan.

## 4. Micro movimiento constante

Cuando la escena "se queda quieta" (el texto ya entró y se está leyendo), nada queda congelado:
- Flotación: subir y bajar 4–6 px con onda seno, ciclo de 2–3 s.
- Respiración: escala 1.00 ↔ 1.012.
- Rotación leve: ±0.6°.
- Cada elemento con un desfase distinto para que no se muevan en bloque.
- Partículas (polvo de luz, vapor) siempre en movimiento.

## 5. Efecto sable de energía

- Gancho inicial: manos encendiendo una hoja de energía luminosa (clip animado).
- Transición "corte": línea de luz que barre la pantalla en diagonal; la imagen se parte en dos mitades que se separan y revelan la siguiente escena.
- La línea tiene núcleo blanco, halo de color (dorado-ámbar para café; se ajusta por producto) y destello al terminar.
- Se usa una hoja de energía genérica: sin logos, nombres ni diseños de películas.

## 6. Duración y gancho (para monetizar)

- Los videos duran más de 1 minuto (objetivo: 65–80 s), porque la mayoría de los programas de monetización lo piden.
- Para que no aburra, se divide en capítulos cortos de 6–10 s, cada uno con su cambio de escena y su texto.
- Los primeros 10 segundos son gancho puro: imagen impactante animada, pregunta intrigante y una promesa que se cumple al final ("quédate, porque al final te enseño…").
- Cambios visuales cada 3–6 s como máximo.

## 7. Llamada a la acción

- Siempre hay una llamada a la acción al final, pero distinta en cada video. Ejemplos:
  - "¿Y tú, ya lo probaste? Cuéntame cómo te gusta tu café."
  - "¿Cuál de las tres formas vas a probar primero?"
  - "Guárdalo para tu próxima mañana."
  - "Si quieres probarlo, escríbeme por mensaje."
  - "Comparte este video con quien no puede vivir sin café."
- Evitar las que Meta penaliza (comentar una palabra o número exacto, etiquetar amigos). Ver `POLITICAS.md`.

## 8. Reglas que siguen igual

- Formato vertical 1080 × 1920, 30 fps.
- Subtítulos palabra por palabra con palabras clave en amarillo.
- Cierre con el empaque oficial, "Escríbeme por mensaje" y la leyenda de COFEPRIS.
- Textos según `POLITICAS.md`. Etiqueta de IA activada al publicar.
