"""نسخه‌ی وب محلی دانلودر YouTube.

اجرا:
    python -m pip install -r requirements-web.txt
    python web_app.py

سپس در مرورگر باز کنید:
    http://127.0.0.1:5000

دانلود روی همین رایانه انجام می‌شود و کوکی مرورگر فقط توسط yt-dlp
در حافظه خوانده می‌شود.
"""

from __future__ import annotations

import re
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yt_dlp
from flask import Flask, jsonify, render_template, request, send_from_directory

APP_VERSION = "2.0.0"
DOWNLOAD_DIR = Path.home() / "Downloads" / "YoutubeDownloader"
YOUTUBE_RE = re.compile(
    r"^https?://(?:(?:www|m)\.)?(?:youtube\.com|youtu\.be)/.+", re.IGNORECASE
)
QUALITY_MAP = {"1080": 1080, "720": 720, "480": 480}
BROWSER_MAP = {"chrome": "chrome", "edge": "edge", "firefox": "firefox"}

app = Flask(__name__)
jobs: dict[str, dict[str, Any]] = {}
jobs_lock = threading.Lock()


def _new_job() -> dict[str, Any]:
    """وضعیت اولیه‌ی یک دانلود را می‌سازد."""
    return {
        "status": "queued",
        "percent": 0,
        "speed": "",
        "message": "در صف دانلود...",
        "error": "",
        "filename": "",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def _set_job(job_id: str, **values: Any) -> None:
    """وضعیت job را به‌صورت thread-safe تغییر می‌دهد."""
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(values)


def _progress_hook(job_id: str, data: dict[str, Any]) -> None:
    """وضعیت yt-dlp را به وضعیت قابل نمایش در مرورگر تبدیل می‌کند."""
    if data.get("status") == "downloading":
        raw = str(data.get("_percent_str", "0%")).replace("%", "").strip()
        try:
            percent = float(raw)
        except ValueError:
            percent = 0
        _set_job(
            job_id,
            status="downloading",
            percent=percent,
            speed=str(data.get("_speed_str", "")),
            message=f"در حال دانلود: {raw}٪",
        )
    elif data.get("status") == "finished":
        _set_job(job_id, percent=100, message="دریافت فایل تمام شد؛ در حال پردازش...")


def _friendly_error(error_text: str) -> str:
    """پیام مناسب برای خطاهای ضدربات و شبکه برمی‌گرداند."""
    if "Sign in to confirm" in error_text or "not a bot" in error_text:
        return (
            "YouTube نیاز به ورود یا تأیید ضدربات دارد. مرورگر دارای حساب را "
            "انتخاب کنید، مرورگر را ببندید و دوباره امتحان کنید.\n\n"
            f"جزئیات: {error_text}"
        )
    if "WinError 10054" in error_text or "UNEXPECTED_EOF" in error_text:
        return (
            "اتصال امن به YouTube قطع شد. VPN/Proxy سراسری یا Proxy محلی را "
            "بررسی کنید.\n\n"
            f"جزئیات: {error_text}"
        )
    return error_text


def _download(
    job_id: str,
    url: str,
    output: Path,
    quality: int,
    output_type: str,
    browser: str,
    proxy: str,
) -> None:
    """یک دانلود را خارج از thread درخواست Flask اجرا می‌کند."""
    is_audio = output_type == "audio"
    selector = (
        "bestaudio/best"
        if is_audio
        else (
            f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        )
    )
    options: dict[str, Any] = {
        "format": selector,
        "outtmpl": str(output / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "retries": 10,
        "fragment_retries": 10,
        "extractor_retries": 5,
        "socket_timeout": 30,
        "force_ipv4": True,
        "sleep_interval_requests": 1,
        "progress_hooks": [lambda data: _progress_hook(job_id, data)],
        "quiet": True,
        "no_warnings": True,
        "windowsfilenames": True,
        "merge_output_format": "mp4",
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/134.0.0.0 Safari/537.36"
            )
        },
    }
    if proxy:
        options["proxy"] = proxy
    if browser:
        options["cookiesfrombrowser"] = (browser,)
    if is_audio:
        options["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ]

    try:
        _set_job(job_id, status="starting", message="در حال اتصال به YouTube...")
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=True)
        filename = str(info.get("_filename") or info.get("title") or "")
        _set_job(
            job_id,
            status="completed",
            percent=100,
            message="دانلود با موفقیت تمام شد.",
            filename=Path(filename).name if filename else "",
        )
    except Exception as exc:
        _set_job(
            job_id,
            status="error",
            message="دانلود انجام نشد.",
            error=_friendly_error(str(exc)),
        )


@app.get("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.post("/api/download")
def start_download():
    data = request.get_json(silent=True) or request.form
    url = str(data.get("url", "")).strip()
    quality_key = str(data.get("quality", "1080"))
    output_type = str(data.get("output_type", "video"))
    browser_key = str(data.get("browser", ""))
    proxy = str(data.get("proxy", "")).strip()

    if not YOUTUBE_RE.match(url):
        return jsonify({"error": "لطفاً یک لینک معتبر YouTube وارد کنید."}), 400
    if quality_key not in QUALITY_MAP:
        return jsonify({"error": "کیفیت انتخاب‌شده معتبر نیست."}), 400
    if output_type not in {"video", "audio"}:
        return jsonify({"error": "نوع خروجی معتبر نیست."}), 400
    if browser_key and browser_key not in BROWSER_MAP:
        return jsonify({"error": "مرورگر انتخاب‌شده معتبر نیست."}), 400

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = _new_job()
    threading.Thread(
        target=_download,
        args=(
            job_id, url, DOWNLOAD_DIR, QUALITY_MAP[quality_key], output_type,
            BROWSER_MAP.get(browser_key, ""), proxy,
        ),
        daemon=True,
    ).start()
    return jsonify({"job_id": job_id})


@app.get("/api/jobs/<job_id>")
def job_status(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            return jsonify({"error": "دانلود پیدا نشد."}), 404
        return jsonify(job)


@app.get("/api/files/<path:filename>")
def download_file(filename: str):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
