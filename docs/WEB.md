# راهنمای کامل نسخه‌ی وب محلی

نگارش فعلی این نسخه: `2.0.0`

## هدف

`web_app.py` یک سرور Flask محلی است. مرورگر فقط رابط کاربری را نمایش می‌دهد؛ دانلود با `yt-dlp` روی همان کامپیوتر اجرا می‌شود. این مدل برای شرایطی مناسب است که کاربر می‌خواهد مرورگر، VPN، Proxy و پروفایل کوکی سیستم خودش را استفاده کند.

سرور فقط روی `127.0.0.1` bind می‌شود و از شبکه‌ی محلی قابل دسترسی نیست.

## اجرا

روش دستی:

```powershell
python -m pip install -r requirements-web.txt
python web_app.py
```

سپس:

```text
http://127.0.0.1:5000
```

روش ساده‌تر: اجرای `Run-WebDownloader.bat`. این فایل وابستگی وب را نصب می‌کند، مرورگر را باز می‌کند و سرور را اجرا می‌نماید. پنجره‌ی PowerShell/Command Prompt را تا پایان دانلود باز نگه دارید.

## قابلیت‌های رابط

- Paste از clipboard مرورگر
- انتخاب 480p، 720p یا 1080p
- MP4 یا MP3
- انتخاب Chrome، Edge یا Firefox برای `cookiesfrombrowser`
- ورود Proxy اختیاری مانند `socks5://127.0.0.1:1080`
- نمایش progress، سرعت، پیام خطا و لینک دریافت فایل

وقتی YouTube خطای «Sign in to confirm you’re not a bot» می‌دهد، مرورگری را انتخاب کنید که در آن وارد YouTube هستید و آن مرورگر را قبل از شروع دانلود ببندید. کوکی در فایل پروژه ذخیره نمی‌شود.

## API

### `GET /`

صفحه‌ی HTML را برمی‌گرداند.

### `POST /api/download`

بدنه‌ی JSON:

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "quality": "1080",
  "output_type": "video",
  "browser": "chrome",
  "proxy": ""
}
```

مقادیر `quality`: `1080`، `720`، `480`.
مقادیر `output_type`: `video`، `audio`.
مقادیر `browser`: خالی، `chrome`، `edge`، `firefox`.

پاسخ موفق:

```json
{"job_id": "شناسه"}
```

### `GET /api/jobs/<job_id>`

وضعیت job را برمی‌گرداند:

```json
{
  "status": "downloading",
  "percent": 42.5,
  "speed": "1.2MiB/s",
  "message": "در حال دانلود: 42.5٪",
  "error": "",
  "filename": ""
}
```

وضعیت‌های اصلی: `queued`، `starting`، `downloading`، `completed`، `error`.

### `GET /api/files/<filename>`

فایل کامل‌شده را از پوشه‌ی پیش‌فرض به‌صورت attachment ارائه می‌کند.

## معماری داخلی

- Flask request thread فقط job را اعتبارسنجی و ثبت می‌کند.
- هر دانلود در `threading.Thread(daemon=True)` اجرا می‌شود.
- وضعیت‌ها در dictionary حافظه‌ای `jobs` نگهداری می‌شوند.
- `jobs_lock` برای دسترسی هم‌زمان به وضعیت‌ها استفاده می‌شود.
- JavaScript هر 700 میلی‌ثانیه `/api/jobs/<id>` را poll می‌کند.
- پس از `completed`، لینک فایل به `/api/files/...` فعال می‌شود.

این وضعیت با restart سرور از بین می‌رود و history دائمی دانلود وجود ندارد.

## دیباگ

برای دیدن خطای کامل:

```powershell
python web_app.py
```

بررسی وابستگی:

```powershell
python -m pip check
python -c "import flask, yt_dlp; print(flask.__version__, yt_dlp.version.__version__)"
```

بررسی پورت:

```powershell
Test-NetConnection 127.0.0.1 -Port 5000
```

اگر پورت اشغال بود، مقدار `port=5000` در انتهای `web_app.py` را تغییر دهید و همان پورت را در مرورگر باز کنید.

## محدودیت‌های فعلی و توسعه‌ی بعدی

- فقط YouTube پشتیبانی می‌شود.
- فقط یک process سرور محلی در نظر گرفته شده است.
- لغو دانلود و صف پایدار وجود ندارد.
- jobها در حافظه هستند.
- مسیر خروجی فعلاً ثابت و برابر `Downloads\YoutubeDownloader` است.

برای توسعه‌ی بعدی، مدل‌های `DownloadRequest` و `DownloadJob` را از Flask جدا کنید، provider برای سایت‌ها بسازید، و برای jobها persistence یا cleanup اضافه کنید.
