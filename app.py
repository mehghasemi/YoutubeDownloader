"""Simple YouTube downloader GUI.

Requires:
    python -m pip install -r requirements.txt
    ffmpeg available on PATH for video/audio merging.
"""

from __future__ import annotations

import os
import queue
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

import yt_dlp


DOWNLOAD_DIR = Path.home() / "Downloads" / "YoutubeDownloader"
APP_VERSION = "1.1.0"
CHANGELOG = (
    ("1.1.0", "2026-08-30 13:52", ("رابط کاربری کاملاً راست‌چین و فارسی شد.", "افزودن پشتیبانی از فونت IRANSans با جایگزین خودکار.", "افزودن شماره نگارش و فهرست تغییرات.")),
    ("1.0.0", "2026-08-30 13:22", ("نسخه‌ی اولیه‌ی دانلودر یوتیوب.", "دانلود ویدئو با کیفیت‌های 480p، 720p و 1080p.", "خروجی MP4 و MP3 و نمایش پیشرفت دانلود.")),
)
YOUTUBE_RE = re.compile(
    r"^https?://(?:(?:www|m)\.)?(?:youtube\.com|youtu\.be)/.+", re.IGNORECASE
)


class DownloadApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("دانلودر یوتیوب")
        self.geometry("660x390")
        self.minsize(600, 350)
        self.configure(padx=18, pady=18)

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.downloading = False
        self.url_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(DOWNLOAD_DIR))
        self.quality_var = tk.StringVar(value="بهترین کیفیت تا 1080p")
        self.type_var = tk.StringVar(value="ویدئو (MP4)")
        self.status_var = tk.StringVar(value="لینک یوتیوب را وارد کنید.")
        self.progress_var = tk.DoubleVar(value=0)
        self.ui_font = self._find_font()
        self.bold_font = (self.ui_font, 18, "bold")
        self._configure_styles()

        self._build_ui()
        self.after(100, self._process_events)

    def _find_font(self) -> str:
        available = set(tkfont.families(self))
        for name in ("IRANSans", "IRAN Sans", "IRANSansWeb", "Tahoma", "Segoe UI"):
            if name in available:
                return name
        return "TkDefaultFont"

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.configure(".", font=(self.ui_font, 10))
        style.configure("TButton", font=(self.ui_font, 10))
        style.configure("TLabel", font=(self.ui_font, 10))
        style.configure("TEntry", font=(self.ui_font, 10))
        style.configure("TCombobox", font=(self.ui_font, 10))

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="دانلودر ویدئوی یوتیوب", font=self.bold_font).grid(
            row=0, column=0, sticky="e", pady=(0, 18)
        )

        form = ttk.Frame(self)
        form.grid(row=1, column=0, sticky="ew")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="لینک ویدئو:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=6)
        url_entry = ttk.Entry(form, textvariable=self.url_var, justify="left")
        url_entry.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(form, text="Paste", command=self._paste_url).grid(
            row=0, column=2, padx=(8, 0), pady=6
        )
        url_entry.bind("<Control-v>", self._paste_event)
        url_entry.bind("<Control-V>", self._paste_event)

        ttk.Label(form, text="کیفیت:").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
        ttk.Combobox(
            form,
            textvariable=self.quality_var,
            values=("بهترین کیفیت تا 1080p", "بهترین کیفیت تا 720p", "بهترین کیفیت تا 480p"),
            state="readonly",
        ).grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="نوع خروجی:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
        ttk.Combobox(
            form,
            textvariable=self.type_var,
            values=("ویدئو (MP4)", "صدا (MP3)"),
            state="readonly",
        ).grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="پوشه ذخیره:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
        ttk.Entry(form, textvariable=self.output_var, state="readonly").grid(
            row=3, column=1, sticky="ew", pady=6
        )
        ttk.Button(form, text="انتخاب", command=self._choose_folder).grid(
            row=3, column=2, padx=(8, 0), pady=6
        )

        self.download_button = ttk.Button(self, text="شروع دانلود", command=self._start_download)
        self.download_button.grid(row=2, column=0, sticky="ew", pady=(20, 8))
        ttk.Progressbar(self, variable=self.progress_var, maximum=100).grid(
            row=3, column=0, sticky="ew", pady=6
        )
        ttk.Label(self, textvariable=self.status_var, wraplength=620).grid(
            row=4, column=0, sticky="e", pady=(8, 0)
        )
        ttk.Label(
            self,
            text="برای ادغام صدا و تصویر یا تبدیل MP3، نصب بودن FFmpeg لازم است.",
            foreground="#666666",
        ).grid(row=5, column=0, sticky="e", pady=(18, 0))
        version_label = tk.Label(
            self,
            text=f"نگارش {APP_VERSION}",
            font=(self.ui_font, 9, "underline"),
            fg="#1769aa",
            cursor="hand2",
            anchor="e",
        )
        version_label.grid(row=6, column=0, sticky="e", pady=(16, 0))
        version_label.bind("<Button-1>", lambda _event: self._show_changelog())
        url_entry.focus_set()

    def _show_changelog(self) -> None:
        window = tk.Toplevel(self)
        window.title("فهرست تغییرات")
        window.geometry("610x430")
        window.minsize(520, 330)
        window.transient(self)
        window.grab_set()
        window.configure(padx=18, pady=18)

        tk.Label(
            window,
            text="فهرست تغییرات",
            font=(self.ui_font, 15, "bold"),
            anchor="e",
        ).pack(fill="x", pady=(0, 14))

        container = ttk.Frame(window)
        container.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="left", fill="y")
        changes = tk.Text(
            container,
            wrap="word",
            height=15,
            font=(self.ui_font, 10),
            padx=12,
            pady=10,
            relief="solid",
            borderwidth=1,
            yscrollcommand=scrollbar.set,
        )
        changes.pack(side="right", fill="both", expand=True)
        scrollbar.configure(command=changes.yview)

        for index, (version, timestamp, items) in enumerate(CHANGELOG):
            changes.insert("end", f"نگارش {version}\n", "version")
            changes.insert("end", f"تاریخ و ساعت: {timestamp}\n", "timestamp")
            for item in items:
                changes.insert("end", f"• {item}\n")
            if index < len(CHANGELOG) - 1:
                changes.insert("end", "\n")
        changes.tag_configure("version", font=(self.ui_font, 11, "bold"), justify="right")
        changes.tag_configure("timestamp", foreground="#666666", justify="right")
        changes.configure(state="disabled")

        ttk.Button(window, text="بستن", command=window.destroy).pack(pady=(14, 0), anchor="e")

    def _choose_folder(self) -> None:
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def _paste_event(self, _event: tk.Event) -> str:
        self._paste_url()
        return "break"

    def _paste_url(self) -> None:
        try:
            clipboard_text = self.clipboard_get().strip()
        except tk.TclError:
            messagebox.showwarning("کلیپ‌بورد خالی است", "لینکی در کلیپ‌بورد پیدا نشد.")
            return
        self.url_var.set(clipboard_text)

    def _start_download(self) -> None:
        if self.downloading:
            return
        url = self.url_var.get().strip()
        if not YOUTUBE_RE.match(url):
            messagebox.showerror("لینک نامعتبر", "لطفاً یک لینک معتبر یوتیوب وارد کنید.")
            return

        output = Path(self.output_var.get()).expanduser()
        output.mkdir(parents=True, exist_ok=True)
        self.downloading = True
        self.download_button.configure(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("در حال آماده‌سازی دانلود...")
        threading.Thread(target=self._download, args=(url, output), daemon=True).start()

    def _download(self, url: str, output: Path) -> None:
        is_audio = self.type_var.get() == "صدا (MP3)"
        quality = {
            "بهترین کیفیت تا 1080p": 1080,
            "بهترین کیفیت تا 720p": 720,
            "بهترین کیفیت تا 480p": 480,
        }[self.quality_var.get()]
        format_selector = (
            "bestaudio/best"
            if is_audio
            else (
                f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
            )
        )

        options = {
            "format": format_selector,
            "outtmpl": str(output / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "windowsfilenames": True,
            "merge_output_format": "mp4",
        }
        if is_audio:
            options["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
            ]

        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
            self.events.put(("done", "دانلود با موفقیت تمام شد."))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def _progress_hook(self, data: dict) -> None:
        if data.get("status") == "downloading":
            raw = data.get("_percent_str", "0%").replace("%", "").strip()
            try:
                percent = float(raw)
            except ValueError:
                percent = 0
            self.events.put(("progress", (percent, f"در حال دانلود: {raw}%  {data.get('_speed_str', '')}")))
        elif data.get("status") == "finished":
            self.events.put(("progress", (100, "دانلود فایل تمام شد؛ در حال پردازش...")))

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "progress":
                    percent, text = payload
                    self.progress_var.set(percent)
                    self.status_var.set(text)
                elif event == "done":
                    self.downloading = False
                    self.download_button.configure(state="normal")
                    self.status_var.set(str(payload))
                    messagebox.showinfo("تمام شد", f"{payload}\n\nمسیر: {self.output_var.get()}")
                elif event == "error":
                    self.downloading = False
                    self.download_button.configure(state="normal")
                    self.status_var.set("دانلود ناموفق بود.")
                    messagebox.showerror("خطا", f"دانلود انجام نشد:\n{payload}")
        except queue.Empty:
            pass
        self.after(100, self._process_events)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    DownloadApp().mainloop()
