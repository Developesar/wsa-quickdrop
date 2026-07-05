# راهنمای کاربر

## روش ساده

1. WSA QuickDrop را باز کنید.
2. Connect را بزنید.
3. از Pixel 5 یک پوشه مثل Pictures، Download، Documents یا DCIM را انتخاب کنید.
4. فایل‌ها را داخل برنامه رها کنید یا Browse files را بزنید.
5. Send را بزنید.
6. در برنامه اندرویدی، File Picker را باز کنید و به Pixel 5 > پوشه انتخاب‌شده بروید.

در رابط گرافیکی، همه فایل‌های صف‌شده به همان پوشه انتخاب‌شده می‌روند. مقصد بر اساس پسوند فایل عوض نمی‌شود.

## روش SendTo

1. میانبر SendTo را نصب کنید.
2. فایل‌ها را در Windows Explorer انتخاب کنید.
3. Right click > Send to > WSA QuickDrop را بزنید.
4. برنامه باز می‌شود و فایل‌ها را در صف نشان می‌دهد.
5. پوشه مقصد را بررسی کنید و Send را بزنید.

ارسال فوری از SendTo در Settings قابل فعال‌سازی است، ولی پیش‌فرض خاموش است.

## مرورگر پوشه

پنل سمت چپ Pixel 5 را نشان می‌دهد. این نام ساده حافظه اندروید داخل WSA است. در حالت عادی مسیرهای فنی مثل `/sdcard` نمایش داده نمی‌شوند.

کاربران حرفه‌ای می‌توانند Show advanced Android path را در Settings فعال کنند.

## ساخت پوشه

1. یک پوشه والد مثل Pictures را انتخاب کنید.
2. Create folder را بزنید.
3. نام امن وارد کنید، مثلا My OCR Tests.
4. برنامه پوشه Pixel 5 > Pictures > My OCR Tests را می‌سازد و انتخاب می‌کند.

## CLI

```powershell
WSAQuickDrop.exe --send "sample.jpg" --folder Pictures
WSAQuickDrop.exe --send "sample.pdf" --folder Download
WSAQuickDrop.exe --send "sample.jpg" --folder "Pictures/My OCR Tests"
WSAQuickDrop.exe --list-folders
WSAQuickDrop.exe --create-folder Pictures "My OCR Tests"
```

## مثال Persian OCR Offline

1. Pictures را انتخاب کنید.
2. عکس را داخل برنامه رها کنید.
3. Send را بزنید.
4. Persian OCR Offline را باز کنید.
5. Select Image را بزنید.
6. مسیر Pixel 5 > Pictures را باز کنید.
7. عکس را انتخاب کنید.
