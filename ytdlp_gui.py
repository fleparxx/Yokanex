#!/usr/bin/env python3
"""GUI simple para descargar videos/audio usando yt-dlp."""

from __future__ import annotations

import os
import queue
import shlex
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class YtDlpGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("yt-dlp GUI")
        self.geometry("860x560")
        self.minsize(760, 460)

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.process: subprocess.Popen[str] | None = None

        self.url_var = tk.StringVar()
        self.output_var = tk.StringVar(value=os.path.join(os.getcwd(), "descargas"))
        self.format_var = tk.StringVar(value="Video (mp4)")
        self.audio_quality_var = tk.StringVar(value="192")
        self.playlist_var = tk.BooleanVar(value=False)
        self.subtitles_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.after(120, self._poll_logs)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        form = ttk.Frame(container)
        form.pack(fill="x")

        ttk.Label(form, text="URL").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Entry(form, textvariable=self.url_var).grid(
            row=0, column=1, columnspan=3, sticky="ew", padx=(6, 0), pady=(0, 6)
        )

        ttk.Label(form, text="Carpeta de salida").grid(row=1, column=0, sticky="w", pady=(0, 6))
        ttk.Entry(form, textvariable=self.output_var).grid(
            row=1, column=1, columnspan=2, sticky="ew", padx=6, pady=(0, 6)
        )
        ttk.Button(form, text="Elegir...", command=self._choose_output).grid(
            row=1, column=3, sticky="ew", pady=(0, 6)
        )

        ttk.Label(form, text="Formato").grid(row=2, column=0, sticky="w")
        format_combo = ttk.Combobox(
            form,
            textvariable=self.format_var,
            state="readonly",
            values=["Video (mp4)", "Solo audio (mp3)", "Mejor disponible"],
        )
        format_combo.grid(row=2, column=1, sticky="ew", padx=6)

        ttk.Label(form, text="Calidad audio kbps").grid(row=2, column=2, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.audio_quality_var,
            state="readonly",
            values=["96", "128", "160", "192", "256", "320"],
            width=8,
        ).grid(row=2, column=3, sticky="w")

        ttk.Checkbutton(form, text="Descargar playlist", variable=self.playlist_var).grid(
            row=3, column=1, sticky="w", pady=(8, 0), padx=6
        )
        ttk.Checkbutton(form, text="Descargar subtítulos", variable=self.subtitles_var).grid(
            row=3, column=2, sticky="w", pady=(8, 0)
        )

        for col in (1, 2, 3):
            form.columnconfigure(col, weight=1)

        actions = ttk.Frame(container)
        actions.pack(fill="x", pady=10)

        self.download_button = ttk.Button(actions, text="Descargar", command=self._start_download)
        self.download_button.pack(side="left")

        self.stop_button = ttk.Button(actions, text="Detener", command=self._stop_download, state="disabled")
        self.stop_button.pack(side="left", padx=6)

        self.command_label = ttk.Label(actions, text="", foreground="#555")
        self.command_label.pack(side="left", padx=8)

        log_frame = ttk.LabelFrame(container, text="Salida")
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, wrap="word", height=18)
        self.log_text.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y", pady=8, padx=8)
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _choose_output(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_var.get() or os.getcwd())
        if selected:
            self.output_var.set(selected)

    def _build_command(self) -> list[str]:
        url = self.url_var.get().strip()
        if not url:
            raise ValueError("Introduce una URL válida.")

        yt_dlp_path = shutil.which("yt-dlp")
        if not yt_dlp_path:
            raise RuntimeError(
                "No se encontró 'yt-dlp'. Instálalo y vuelve a intentarlo."
            )

        output_dir = os.path.abspath(self.output_var.get().strip() or "descargas")
        os.makedirs(output_dir, exist_ok=True)

        command = [yt_dlp_path, url, "-P", output_dir]

        selected_format = self.format_var.get()
        if selected_format == "Video (mp4)":
            command += ["-f", "bv*+ba/b", "--merge-output-format", "mp4"]
        elif selected_format == "Solo audio (mp3)":
            command += ["-x", "--audio-format", "mp3", "--audio-quality", self.audio_quality_var.get()]
        else:
            command += ["-f", "best"]

        if not self.playlist_var.get():
            command.append("--no-playlist")

        if self.subtitles_var.get():
            command += ["--write-subs", "--sub-langs", "all"]

        return command

    def _append_log(self, text: str) -> None:
        self.log_text.insert("end", text)
        self.log_text.see("end")

    def _set_running(self, is_running: bool) -> None:
        self.download_button.config(state="disabled" if is_running else "normal")
        self.stop_button.config(state="normal" if is_running else "disabled")

    def _start_download(self) -> None:
        if self.process and self.process.poll() is None:
            messagebox.showinfo("Descarga en progreso", "Ya hay una descarga en curso.")
            return

        try:
            command = self._build_command()
        except (ValueError, RuntimeError) as error:
            messagebox.showerror("Error", str(error))
            return

        command_display = " ".join(shlex.quote(part) for part in command)
        self.command_label.config(text=f"Comando: {command_display}")
        self._append_log(f"\n$ {command_display}\n")

        self._set_running(True)
        thread = threading.Thread(target=self._run_process, args=(command,), daemon=True)
        thread.start()

    def _run_process(self, command: list[str]) -> None:
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.log_queue.put(line)

            exit_code = self.process.wait()
            if exit_code == 0:
                self.log_queue.put("\n✅ Descarga completada.\n")
            else:
                self.log_queue.put(f"\n❌ El proceso terminó con código {exit_code}.\n")
        except Exception as error:  # noqa: BLE001
            self.log_queue.put(f"\n❌ Error al ejecutar yt-dlp: {error}\n")
        finally:
            self.log_queue.put("__PROCESS_END__")

    def _stop_download(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self._append_log("\n⚠️ Descarga detenida por el usuario.\n")

    def _poll_logs(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break

            if message == "__PROCESS_END__":
                self._set_running(False)
                continue

            self._append_log(message)

        self.after(120, self._poll_logs)


if __name__ == "__main__":
    app = YtDlpGUI()
    app.mainloop()
