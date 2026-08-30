# دانلودر یوتیوب

برنامه‌ی دسکتاپ ویندوز برای دریافت لینک یوتیوب و دانلود آن به‌صورت MP4 یا MP3.
رابط کاربری با Python/Tkinter و موتور دانلود با `yt-dlp` ساخته شده است.

## مستندات

- [معماری و قرارداد کد](docs/ARCHITECTURE.md)
- [توسعه، تست و دیباگ](docs/DEVELOPMENT.md)
- [تاریخچه‌ی نگارش‌ها](CHANGELOG.md)

## وضعیت فعلی

- نگارش: `1.1.0`
- هدف: Windows 10/11، 64 بیتی
- Python توسعه: 3.10 یا جدیدتر
- ورودی: لینک تکی YouTube؛ playlist پشتیبانی نمی‌شود.
- خروجی: ویدئوی MP4 یا صدای MP3
- پوشه‌ی پیش‌فرض: `%USERPROFILE%\Downloads\YoutubeDownloader`
- فونت: اولویت با `IRANSans` و fallback خودکار به فونت‌های نصب‌شده‌ی رایج.

## اجرای نسخه‌ی توسعه

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

## ساخت فایل اجرایی

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name YoutubeDownloader app.py
```

خروجی در `dist\YoutubeDownloader.exe` ساخته می‌شود. پوشه‌های build و dist و فایل‌های spec خروجی تولیدی‌اند و طبق `.gitignore` commit نمی‌شوند.

## FFmpeg

FFmpeg برای ترکیب stream جداگانه‌ی تصویر/صدا و تبدیل MP3 لازم است:

```powershell
winget install Gyan.FFmpeg
ffmpeg -version
```

## استفاده

1. لینک را وارد کنید یا روی `Paste`/`Ctrl+V` بزنید.
2. سقف کیفیت را انتخاب کنید.
3. نوع خروجی و پوشه‌ی ذخیره را انتخاب کنید.
4. روی `شروع دانلود` کلیک کنید.
5. روی شماره‌ی نگارش پایین پنجره برای دیدن تاریخچه کلیک کنید.

## نکته برای توسعه‌دهنده یا مدل زبانی

ترتیب مطالعه‌ی پیشنهادی: این README، سپس `docs/ARCHITECTURE.md`، بعد `app.py` و در پایان `docs/DEVELOPMENT.md` و `CHANGELOG.md`.
هر تغییر قابل مشاهده باید هم در `CHANGELOG` داخل `app.py` و هم در `CHANGELOG.md` ثبت شود.

فقط محتوایی را دانلود کنید که دانلود آن از نظر حقوقی و قوانین سایت مجاز است.
