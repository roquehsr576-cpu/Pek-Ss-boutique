# El Verdadero Éxito

Reels motivacionales para la página "El Verdadero Éxito". Es una página separada de DXN y de Pek'Ss Boutique: no se mezclan logos, productos ni negocio en los videos. El negocio solo se habla por mensaje privado.

## Decisiones actuales

- Sin nombre de página ni logo en los videos (por ahora).
- Voz: ElevenLabs `eleven_v4`, "El Faraón" (`W1hAcdh0RNsPYUA7fkJh`).
- Música: la elige Roque (prompt sugerido para Suno en cada guion).
- Temas: hábitos, disciplina, equipo, historias con enseñanza, mentalidad y finanzas personales básicas y verificables.

## Cómo se trabaja

1. Propuesta de tema → guion en tabla con costo → esperar el "dale" de Roque antes de gastar créditos.
2. Gancho en los primeros 3 s sin dar la respuesta; pregunta abierta a la mitad; más de 60 s; cierre con pregunta abierta (nunca "comenta", "comparte", "sigue" ni "etiqueta").
3. Solo datos verificables con fuente; las historias no confirmadas se cuentan como "imagina…" o parábola.
4. Imágenes Higgsfield z_image 9:16, Veo (kie.ai) solo en tomas clave, subtítulos palabra por palabra, textos que no tapan caras (`scripts/motion.py`).
5. Audio: la voz manda; música con sidechain (umbral 0.03, ratio 6, ataque 30, release 280), música 0.35–0.42, EQ −4 dB en 2.5 kHz, loudnorm −14 LUFS.
6. Videos en `reels/`, copys en `COPYS.md`, aprendizajes en `APRENDIZAJES.md`. Commit y push al terminar cada video.

Las reglas base vienen de `dxn/` (rama `claude/focused-franklin-ovqeea`): `APRENDIZAJES.md`, `POLITICAS.md`, `ESTILO_ANIMACION.md`.

## Producción del reel 1 (lo que se aprendió)

- Veo (kie.ai, veo3_fast) devolvió "Internal Error" 3 veces sin cobrar; se usó **Kling 2.6 imagen a video** en kie.ai (`scripts/kie_kling_img.py`, 63 créditos por clip de 5 s).
- Higgsfield en plan gratis solo permite 1 imagen a la vez.
- Render: `scripts/fiel_reel.py` (alineación de frases con las pausas de la voz, subtítulos palabra por palabra) y `scripts/mezcla.py` (la entrada emotiva de la música cae en la revelación y el final natural de la canción acompaña el cierre).
