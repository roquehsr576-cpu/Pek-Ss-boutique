Hola. Quiero replicar para mi página **"El Verdadero Éxito"** el sistema de reels que ya funciona en mi página DXN. Todo está documentado en mi repositorio `roquehsr576-cpu/Pek-Ss-boutique`, rama `claude/focused-franklin-ovqeea`, carpeta `dxn/`. Clónalo o léelo primero (si no está en esta sesión, agrégalo con add_repo).

## Lee esto antes de proponer nada
- `dxn/APRENDIZAJES.md`: reglas del gancho, retención y estadísticas reales.
- `dxn/POLITICAS.md` y `dxn/ESTILO_ANIMACION.md`: créditos, mezcla de audio, pizarrón, regla de no tapar caras.
- `dxn/COPYS.md`: ejemplos de copys que ya usé.
- `dxn/scripts/gano_reel5.py`: plantilla de reel con ilustraciones 3D, gancho, subtítulos palabra por palabra, etiquetas y pregunta a la mitad.
- `dxn/scripts/diab_reel.py`: plantilla con clips animados de Veo de fondo, tarjetas y lista animada.
- `dxn/scripts/hacha.py` y `pizarra.py`: estilo pizarrón ("Afila tu hacha").
- `dxn/scripts/gansos.py` y `motion.py`: fotos con movimiento y textos que esquivan caras.
- `dxn/scripts/kie_veo_img.py` y `veo_wait.py`: animar imágenes con Veo (kie.ai).
- `dxn/reels/reel16_habitos_gansos.mp4` y `reel17_afila_tu_hacha.mp4`: los motivacionales que más se parecen a lo que quiero para esta página.

## El sistema (la fórmula)
1. **Primero propuestas, después créditos.** Propón temas, luego el guion completo en tabla (escena, imagen, voz, texto en pantalla) con costo estimado. **No gastes créditos sin mi "dale" claro.** Un número suelto o un mensaje raro no es aprobación: pregunta.
2. **Gancho en los primeros 3 segundos:**
   - rompe una expectativa o abre una duda;
   - **nunca des la respuesta en la portada ni antes del segundo 8–10**;
   - texto grande desde el primer cuadro;
   - la imagen más llamativa va primero.
3. **Cuerpo:**
   - cortes cada 2–4 s y formato lista cuando se pueda;
   - **una pregunta abierta a la mitad** (en voz y en pantalla);
   - más de 60 s para monetizar.
4. **Cierre con pregunta abierta.** Nunca "comenta", "comparte", "sigue" ni "etiqueta". Al publicar, la pregunta se fija como primer comentario.
5. **Solo datos verificables**, con fuente. Si una historia no se puede confirmar, se cuenta como "imagina…" o como parábola, nunca como hecho. Sin promesas de dinero fácil ni de salud.
6. **Producción:**
   - imágenes con Higgsfield `z_image` en 9:16 (~0.15 créditos c/u), revisadas una por una y repetidas si no son fieles;
   - movimiento con Veo de kie.ai (~60 créditos por clip de 8 s) solo en tomas clave, o en todas si hay saldo y lo apruebo;
   - voz con ElevenLabs `eleven_v4`, voz **El Faraón 3** (`W1hAcdh0RNsPYUA7fkJh`); confírmala con creative_list_voices;
   - subtítulos palabra por palabra sincronizados con las pausas de la voz (silencedetect), palabras clave en dorado;
   - render con PIL → ffmpeg.
7. **Audio:**
   - la voz manda; la música sube en las pausas con sidechain (umbral 0.03, ratio 6, ataque 30, release 280);
   - música ~0.35–0.42, EQ −4 dB en 2.5 kHz, loudnorm −14 LUFS;
   - pistas que ya tengo: `dxn/fuentes/reel15_vive_dxn/caribe_0.mp3` y `caribe_1.mp3`.
8. **Nunca tapar caras** con texto (usa `face_boxes` / `safe_zone` de `motion.py`).
9. **Guarda todo:**
   - videos en `exito/reels/`, copys en `exito/COPYS.md`, fuentes y scripts en `exito/`;
   - commit y push al terminar cada video;
   - mándame el video al terminarlo, con su copy listo para pegar.
10. **Mide y aprende:** cuando te mande la captura de estadísticas (retención, segundo donde se van, compartidos, no seguidores), actualiza `exito/APRENDIZAJES.md` y aplícalo al siguiente video.

## Reglas de la página
- **"El Verdadero Éxito" es una página separada de DXN y de Pek'Ss Boutique.** No mezcles logos, productos ni el negocio en los videos. El negocio solo se habla por mensaje privado.
- Temas: hábitos, disciplina, equipo, historias con enseñanza (estilo gansos o hacha), mentalidad, finanzas personales básicas y verificables.

## Para empezar
1. Revisa el repositorio.
2. Dime qué créditos tengo (Higgsfield `balance`, kie.ai `/api/v1/chat/credit`). Si la llave de kie.ai no está en este entorno, pídemela con el formulario seguro, nunca por chat.
3. Propónme **10 temas** para una serie de "El Verdadero Éxito", cada uno con gancho, dato o historia central verificable y pregunta de cierre.
4. Pregúntame lo que falte: nombre exacto de la página, si quiero logo, voz y música.
