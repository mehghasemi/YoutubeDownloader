# معماری و قرارداد کد

## هدف

برنامه یک GUI کوچک برای دانلود یک ویدئوی YouTube است. تمام منطق فعلی در `app.py` قرار دارد؛ backend، دیتابیس و فایل تنظیمات جداگانه وجود ندارد.

## فایل‌ها

```text
app.py                 # نقطه‌ی ورود، UI، دانلود و changelog
requirements.txt       # وابستگی runtime: yt-dlp
README.md              # شروع سریع و استفاده
CHANGELOG.md           # تاریخچه‌ی متنی
docs/ARCHITECTURE.md   # این سند
docs/DEVELOPMENT.md    # توسعه و دیباگ
```

پوشه‌های `build*`، `dist*`، `spec*` و `__pycache__` تولیدی‌اند.

## ثابت‌های مهم

- `DOWNLOAD_DIR`: `Path.home()/Downloads/YoutubeDownloader`
- `APP_VERSION`: نگارش نمایشی برنامه.
- `CHANGELOG`: tuple رکوردهای `(version, timestamp, items)`؛ حتماً از جدیدترین به قدیمی‌ترین مرتب باشد.
- `YOUTUBE_RE`: فقط شکل عمومی دامنه‌های `youtube.com` و `youtu.be` را بررسی می‌کند؛ قابل دانلود بودن توسط `yt-dlp` مشخص می‌شود.

## کلاس `DownloadApp`

state اصلی:

- `events`: صف thread-safe برای انتقال نتیجه از thread دانلود به UI.
- `downloading`: جلوگیری از دانلود هم‌زمان.
- `url_var`, `output_var`, `quality_var`, `type_var`: ورودی‌های فرم.
- `status_var`, `progress_var`: وضعیت و progressbar.
- `ui_font`: فونت انتخاب‌شده در runtime.

## threading

شبکه و `yt-dlp` blocking هستند؛ `_download` در `threading.Thread(daemon=True)` اجرا می‌شود.
thread دانلود هرگز widget Tkinter را تغییر نمی‌دهد و فقط `events.put(...)` می‌کند.
`_process_events` با `after(100, ...)` در thread اصلی صف را می‌خواند و UI را تغییر می‌دهد.

## جریان اجرا

```text
ورودی URL → اعتبارسنجی regex → ساخت پوشه → شروع thread
thread → format selector → yt-dlp → progress_hook/events
events → _process_events → status/progress/messagebox
```

## دانلود و خروجی

MP4 از `bestvideo` و `bestaudio` تا سقف height انتخابی ساخته می‌شود و در صورت نیاز با FFmpeg merge می‌گردد.
MP3 از `bestaudio/best` دریافت و با postprocessor `FFmpegExtractAudio` به MP3 192kbps تبدیل می‌شود.
نبودن FFmpeg ممکن است merge یا تبدیل نهایی را شکست دهد.

## progress و خطا

`_progress_hook` برای `status=downloading` درصد و سرعت را می‌فرستد و برای `finished` پیام پردازش را می‌فرستد.
`finished` پایان download stream است، نه الزاماً پایان merge یا convert.
استثناهای دانلود به event نوع `error` تبدیل و فقط در thread اصلی با messagebox نمایش داده می‌شوند.

## فونت و RTL

`_find_font` به‌ترتیب `IRANSans`، `IRAN Sans`، `IRANSansWeb`، `Tahoma` و `Segoe UI` را بررسی می‌کند.
اگر فونت IRANSans روی سیستم نصب نباشد، برنامه باید بدون خطا با fallback اجرا شود.
برای bundle کردن فونت در آینده ابتدا مجوز توزیع آن بررسی شود.

## فهرست تغییرات

`_show_changelog` یک `Toplevel` modal می‌سازد و مستقیماً `CHANGELOG` را از جدید به قدیم نمایش می‌دهد.
هر رکورد باید version، تاریخ/ساعت و bulletهای تغییرات داشته باشد.

## مسیر توسعه‌ی آینده

برای افزودن سایت‌های دیگر، صف دانلود یا لغو دانلود، بهتر است ابتدا منطق را جدا کنید:

```text
core/models.py       # request/result/progress
core/providers.py    # providerهای سایت‌ها
core/downloader.py   # orchestration و خطا
ui/main_window.py    # Tkinter
```

UI نباید format string اختصاصی سایت را مستقیماً مدیریت کند.
