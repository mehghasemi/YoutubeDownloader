# راهنمای توسعه، تست و دیباگ

## آماده‌سازی

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

بررسی:

```powershell
python --version
python -c "import yt_dlp; print(yt_dlp.version.__version__)"
python -m PyInstaller --version
ffmpeg -version
```

## اجرای توسعه و تست پایه

```powershell
python app.py
python -m py_compile app.py
python -m pip check
```

تست دستی: باز شدن برنامه، کارکرد Paste و Ctrl+V، خطای URL نامعتبر، انتخاب پوشه، غیرفعال شدن دکمه هنگام دانلود، نمایش progress، فعال شدن دوباره‌ی دکمه پس از پایان، نمایش خطا، و تاریخچه‌ی نگارش از جدید به قدیم.

تست خودکار فعلی فقط compile است؛ افزودن unit test برای URL validation، format selection، changelog ordering و progress parsing اولویت دارد.

## ساخت EXE

```powershell
python -m PyInstaller `
  --noconfirm --onefile --windowed `
  --name YoutubeDownloader `
  --distpath .\dist --workpath .\build --specpath .\spec app.py
```

خروجی `dist\YoutubeDownloader.exe` است. در صورت قفل شدن build قبلی، مسیرهای جدید مثل `dist-new` و `build-new` استفاده کنید.

## افزودن قابلیت

### کیفیت جدید

مقدار فارسی را به `Combobox.values`، سپس map کیفیت داخل `_download` اضافه کنید؛ format selector و README و تست دستی را نیز به‌روزرسانی کنید.

### نوع خروجی جدید

مقدار UI، منطق format/postprocessor و بررسی وابستگی خارجی را اضافه کنید. موفقیت دانلود stream را از موفقیت postprocess جدا نگه دارید.

### سایت جدید

برای رشد پروژه provider abstraction بسازید:

```python
class VideoProvider(Protocol):
    def can_handle(self, url: str) -> bool: ...
    def download(self, request, on_progress): ...
```

UI نباید format string اختصاصی سایت را بشناسد.

## دیباگ خطاهای رایج

- برای دیدن exception کامل، `python app.py` را اجرا کنید؛ EXE پنجره‌ای console ندارد.
- خطای MP3 یا ویدئوی بی‌صدا معمولاً از نبودن FFmpeg است: `where.exe ffmpeg`.
- اگر فارسی درست نیست، encoding فایل را UTF-8 و خانواده‌های Tk را بررسی کنید.
- اگر progress نادرست است، `_percent_str` ممکن است متن رنگی یا مقدار نامعتبر داشته باشد؛ fallback عددی حفظ شود.
- برای console build: `python -m PyInstaller --noconfirm --onefile --console --name YoutubeDownloaderDebug app.py`
- log آینده در `%LOCALAPPDATA%\YoutubeDownloader\logs\app.log` باشد؛ cookie و token در log ذخیره نشود.

## قواعد ایمن

widgetهای Tkinter فقط از thread اصلی تغییر کنند؛ thread دانلود تنها event بفرستد.
قبل از تغییر `git status` را بررسی کنید. خروجی‌های build را commit نکنید.
هر قابلیت قابل مشاهده باید در `APP_VERSION`، `CHANGELOG` داخل `app.py` و `CHANGELOG.md` ثبت شود.

## چک‌لیست release

- [ ] نسخه و timestamp به‌روزرسانی شده است.
- [ ] رکورد جدید ابتدای CHANGELOG است.
- [ ] README و CHANGELOG.md هماهنگ‌اند.
- [ ] compile و pip check موفق‌اند.
- [ ] تست دستی GUI انجام شده است.
- [ ] EXE ساخته و اندازه/مسیر آن بررسی شده است.
- [ ] نیاز FFmpeg در release note ذکر شده است.
