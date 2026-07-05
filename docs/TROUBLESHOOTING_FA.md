# رفع خطاهای رایج

## 1. adb.exe not found

Android SDK Platform-Tools را نصب کنید، مسیر آن را به PATH اضافه کنید، یا `adb.exe` را از داخل برنامه انتخاب کنید.

## 2. WSA connection refused

WSA را اجرا کنید، Developer Mode را فعال کنید، یک برنامه اندرویدی را باز کنید و دوباره `adb connect 127.0.0.1:58526` را امتحان کنید.

## 3. device offline

WSA را restart کنید، اتصال ADB را دوباره برقرار کنید و diagnostics را اجرا کنید.

## 4. unauthorized

ممکن است WSA منتظر تایید ADB باشد. WSA را restart کنید و دوباره وصل شوید.

## 5. فایل‌ها ارسال شده‌اند ولی در Images دیده نمی‌شوند

در File Picker اندروید این مسیرها را بررسی کنید:

- Pixel 5 > Pictures > WSAQuickDrop
- Pixel 5 > Download > WSAQuickDrop

تب Images ممکن است به refresh یا کمی زمان برای Media Scanner نیاز داشته باشد.

## 6. Media Scanner به‌روزرسانی نکرد

اگر verification موفق بوده، فایل ارسال شده است. به جای تب Recent یا Images، مسیر پوشه را دستی باز کنید.

## 7. File Picker فایلی نشان نمی‌دهد

فیلتر File Picker را از images-only به all files تغییر دهید یا مسیر پوشه را دستی باز کنید.

## 8. چند دستگاه ADB وصل است

برنامه وقتی `127.0.0.1:58526` موجود باشد آن را ترجیح می‌دهد. دستگاه‌های دیگر را قطع کنید یا از `--connect` استفاده کنید.

## 9. WSA اجرا نیست

یک برنامه اندرویدی داخل WSA را باز کنید و دوباره تلاش کنید.

## 10. دستور ADB شناخته نمی‌شود

بعد از تغییر PATH یک PowerShell جدید باز کنید، یا مسیر `adb.exe` را دستی در برنامه انتخاب کنید.
