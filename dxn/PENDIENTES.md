# Pendientes y siguiente paso

Estado al 8 de noviembre de 2026.

## Estrategia acordada

- La cuenta habla del Ganoderma y del café: videos educativos, recetas, rutina.
- El negocio (registro como distribuidor) se explica solo por mensaje privado, nunca en el video.
- Todo el contenido sigue `POLITICAS.md`.

## En curso

### Reel 6 nuevo: "Mi rutina de las mañanas" (reemplaza al de "Socio DXN")

Quedó a medias. En `fuentes/reel6_rutina/` ya están:
- `hook_rutina.mp4`: clip animado (Kling) de un sobre de café vertido en una taza y agua caliente al amanecer.
- `ventana.png`: manos con taza humeante junto a la ventana.

Falta:
- Volver a generar la voz. El guion: "Así empiezo mis mañanas. Un sobre de café de Ganoderma, agua caliente, se mezcla y listo. En un minuto. Es mi momento antes de que empiece el día. ¿Y tú? ¿Cómo tomas tu café? Si quieres probar el mío, escríbeme CAFÉ por mensaje." El enlace de la voz anterior expiró.
- Montarlo con `fuentes/parte3/stir.mp4` (mezclar) y cerrar con "¿Quieres probarlo? Escríbeme CAFÉ por mensaje".

## Propuesta aprobada para hacer: reels por producto

Serie de un reel por producto (20 s): gancho animado → sabor → ingredientes (lo que trae y lo que no) → origen (Ganoderma cultivado por DXN con proceso orgánico y control de calidad propio) → momento ideal → empaque oficial + "Escríbeme por mensaje".

Empezar con 3 de prueba: Cream Coffee, Zhi Mocha y Lemonzhi. Luego Lingzhi 3 en 1, 3 en 1 Lite, Black 2 en 1, Zhino, Zhi Roasted y Cocozhi.

Cómo decirlo sin problemas:
- Sí: "Ganoderma cultivado con proceso orgánico" (así lo describe DXN), "sin colorantes, saborizantes ni conservadores artificiales" (solo donde DXN lo dice), "un momento para consentirte".
- No: "producto orgánico" (requiere certificación en México), "sin nada dañino para tu salud", "nutre tu cuerpo".

Costo aproximado por reel: unos 90 créditos de kie.ai (1 clip de Kling 63, 2 o 3 imágenes de 6, Suno 12).

Las fotos oficiales de los empaques están en `fuentes/carrusel_cual_cafe/productos_oficiales/` (ya recortadas en `.png`).

## Pendientes del lado de Roque

- Registrar el 951 228 0679 en WhatsApp Business (Facebook dice que no tiene WhatsApp).
- Terminar el Instagram de DXN (cuenta de negocio) y vincularlo a la página DXN.
- Si se quiere que Claude publique en Facebook: generar el token de la página (debe decir "DXN", no el perfil personal). El token guardado ahora es de perfil personal y no sirve para publicar.
- Editar los textos de los reels y posts ya publicados con los de `COPYS.md`.
- Confirmar que se manejan los 9 productos del carrusel.

## Saldos al cierre

- kie.ai: 1,048 créditos
- Higgsfield: unos 133 créditos (plan gratis: Kling y GPT Image ahí piden plan de pago)

## Herramientas y claves

- La clave de kie.ai y el token de Facebook están guardados en el entorno de nubes "Pek-Ss-boutique" (no en este repositorio).
- Voz del narrador: "Jorge" (ElevenLabs).
- Música: Suno vía kie.ai, y "The Forest's Secret" en `fuentes/musica/`.

## Siguiente sesión (acordado el 11 de noviembre de 2026)

### Serie "Habla el producto" (formato del Vita Café 3D)

Cada producto es un personaje 3D (hecho a partir de su empaque oficial) que explica qué contiene cada ingrediente. El producto se presenta para tomarse tal cual, sin mezclas.

- Duración: más de 60 s. El personaje habla ~30 s (gancho, presentación, cierre) y el resto son escenas de cada ingrediente con su voz encima.
- Costo estimado: ~350 créditos de kie.ai por video (lip sync ~10 créditos por segundo).
- Orden: Lingzhi Black Coffee → Cordyceps Coffee → Cocozhi → Lingzhi Coffee 3 en 1 → Zhi Mocha → Lemonzhi.
- Reglas: decir qué contiene cada ingrediente, su origen e historia; no decir qué hace en el cuerpo (ver tabla en la conversación y `POLITICAS.md`).
- Llamada a la acción distinta en cada video. Seguir `ESTILO_ANIMACION.md`.

### Bloqueos

- ElevenLabs rechaza las voces: "Your subscription has a failed or incomplete payment". Roque debe completar el pago en elevenlabs.io antes de hacer los personajes.
- Las fotos reales del producto que Roque quiere usar deben enviarse como archivo adjunto (no pegadas en el mensaje).

### Hecho en esta sesión

- Reel 8 Black Coffee (74 s) con el estilo nuevo.
- Video largo para YouTube (4:16) en `youtube/`.
- 3 recetas con canela con la bolsa oficial (`reels/receta*.mp4`).
- Saldo kie.ai: ~1,408 créditos. vidIQ: 50 (se renuevan el 19 de noviembre).
