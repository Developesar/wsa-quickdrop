# WSA QuickDrop

ارسال فایل از ویندوز به WSA با یک کلیک.

WSA QuickDrop یک ابزار کوچک ویندوزی است که عکس، PDF، ویدئو، صدا و سندها را با ADB به حافظه Windows Subsystem for Android می‌فرستد. هدف اصلی این است که فایل‌های ویندوز در File Picker برنامه‌های اندرویدی داخل WSA دیده شوند.

## این ابزار چیست

- فایل‌ها را از ویندوز به پوشه‌های مناسب اندروید می‌فرستد.
- برای عکس‌ها از `Pictures/WSAQuickDrop` استفاده می‌کند.
- برای PDF و سندها از `Download/WSAQuickDrop` استفاده می‌کند.
- هیچ فایلی را آپلود نمی‌کند.
- تله‌متری و آنالیتیکس ندارد.

## نصب

فایل release را دانلود و extract کنید، سپس `WSAQuickDrop.exe` را اجرا کنید.

برای نصب گزینه SendTo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_sendto.ps1
```

## فعال کردن Developer Mode در WSA

1. تنظیمات Windows Subsystem for Android را باز کنید.
2. Developer Mode را فعال کنید.
3. یک برنامه اندرویدی را باز کنید تا WSA اجرا شود.
4. پورت پیش‌فرض معمولا `127.0.0.1:58526` است.

راهنمای کامل‌تر در [WSA_SETUP_FA.md](docs/WSA_SETUP_FA.md) آمده است.

## تنظیم ADB

این پروژه ADB را همراه خودش نصب نمی‌کند. Android SDK Platform-Tools را از سایت رسمی Android نصب کنید، سپس مسیر `adb.exe` را به PATH اضافه کنید یا از داخل برنامه فایل `adb.exe` را انتخاب کنید.

راهنمای کامل‌تر در [ADB_SETUP_FA.md](docs/ADB_SETUP_FA.md) آمده است.

## نصب SendTo

بعد از اجرای اسکریپت نصب، در Explorer:

1. یک یا چند فایل را انتخاب کنید.
2. راست‌کلیک کنید.
3. مسیر `Send to > WSA QuickDrop` را بزنید.

این روش نیاز به دسترسی Admin ندارد.

## ارسال فایل با راست‌کلیک

فایل‌ها به شکل خودکار بر اساس نوعشان مسیر‌دهی می‌شوند:

- عکس: `/sdcard/Pictures/WSAQuickDrop`
- PDF و سند: `/sdcard/Download/WSAQuickDrop`
- ویدئو: `/sdcard/Movies/WSAQuickDrop`
- صدا: `/sdcard/Music/WSAQuickDrop`

## ارسال فایل با Drag & Drop

برنامه را باز کنید و فایل‌ها را داخل پنجره رها کنید. اگر Drag & Drop در محیط شما فعال نبود، از دکمه Browse Files استفاده کنید.

## مثال برای Persian OCR Offline

برای تست:

```text
Open Persian OCR Offline > Select Image/PDF > Pixel 5 > Pictures or Download > WSAQuickDrop
```

شناسه‌های شناخته‌شده:

- `ir.persiandots.ocr.dev`
- `ir.persiandots.ocr`

## رفع خطاهای رایج

اگر فایل‌ها در تب Images دیده نمی‌شوند، داخل Android File Picker مسیر `Pixel 5 > Pictures > WSAQuickDrop` یا `Pixel 5 > Download > WSAQuickDrop` را بررسی کنید. گاهی Media Scanner کمی دیر به‌روزرسانی می‌شود.

جزئیات بیشتر در [TROUBLESHOOTING_FA.md](docs/TROUBLESHOOTING_FA.md) است.
