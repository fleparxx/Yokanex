# yt-dlp GUI

Interfaz gráfica simple en **Python + Tkinter** para usar `yt-dlp` sin línea de comandos.

## Requisitos

- Python 3.10+
- `yt-dlp` instalado y disponible en `PATH`

Instalación de `yt-dlp`:

```bash
python -m pip install -U yt-dlp
```

## Ejecutar

```bash
python ytdlp_gui.py
```

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
