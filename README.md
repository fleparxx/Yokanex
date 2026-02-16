# yt-dlp GUI

Interfaz gráfica simple en **Python + Tkinter** para usar `yt-dlp` sin línea de comandos.

## Requisitos

- Python 3.10+
- `yt-dlp` instalado y disponible en `PATH`

Instalación de `yt-dlp`:

```bash
python -m pip install -U yt-dlp
```

## Ejecutar (modo simple)

```bash
python ytdlp_gui.py
```

## Publicarlo / distribuirlo como paquete

1. Instalar el proyecto en modo editable:

```bash
python -m pip install -e .
```

2. Ejecutar con comando global del paquete:

```bash
ytdlp-gui
```

3. Construir artefactos para publicación (wheel/sdist):

```bash
python -m pip install -U build
python -m build
```

Esto genera `dist/*.whl` y `dist/*.tar.gz` listos para publicar (por ejemplo en PyPI o GitHub Releases).

## Funciones

- Descarga por URL
- Selección de carpeta de salida
- Formatos:
  - Video MP4
  - Solo audio MP3 (con calidad seleccionable)
  - Mejor formato disponible
- Opción para permitir/bloquear playlists
- Descarga de subtítulos
- Consola en vivo con salida del proceso
- Botón para detener la descarga
