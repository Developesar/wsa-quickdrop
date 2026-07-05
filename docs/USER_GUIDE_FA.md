# راهنمای کاربر

## ارسال با راست‌کلیک

1. اسکریپت `scripts/install_sendto.ps1` را اجرا کنید.
2. در Windows Explorer یک یا چند فایل را انتخاب کنید.
3. راست‌کلیک کنید.
4. مسیر `Send to > WSA QuickDrop` را انتخاب کنید.
5. فایل‌ها با ADB به WSA فرستاده می‌شوند.

## ارسال با Drag & Drop

1. `WSAQuickDrop.exe` را باز کنید.
2. فایل‌ها را داخل پنجره رها کنید یا از Browse Files استفاده کنید.
3. حالت مقصد را انتخاب کنید.
4. روی Send to WSA بزنید.

## حالت‌های مقصد

- Auto: بر اساس نوع فایل مسیر را انتخاب می‌کند.
- Pictures: همه فایل‌ها را به `/sdcard/Pictures/WSAQuickDrop` می‌فرستد.
- Downloads: همه فایل‌ها را به `/sdcard/Download/WSAQuickDrop` می‌فرستد.
- Documents: همه فایل‌ها را به `/sdcard/Documents/WSAQuickDrop` می‌فرستد.
- Movies: همه فایل‌ها را به `/sdcard/Movies/WSAQuickDrop` می‌فرستد.
- Music: همه فایل‌ها را به `/sdcard/Music/WSAQuickDrop` می‌فرستد.
- Custom: مسیر دلخواه زیر `/sdcard/`.

## استفاده از CLI

```powershell
WSAQuickDrop.exe --send "C:\Users\User\Desktop\sample.jpg"
WSAQuickDrop.exe --send "sample.pdf" --target downloads
WSAQuickDrop.exe --send "sample.jpg" --target custom --custom-path "/sdcard/Pictures/MyInbox"
WSAQuickDrop.exe --diagnose
```

## مثال Persian OCR Offline

1. عکس یا PDF را با WSA QuickDrop ارسال کنید.
2. Persian OCR Offline را داخل WSA باز کنید.
3. Select Image/PDF را بزنید.
4. در File Picker اندروید، Pixel 5 را انتخاب کنید.
5. وارد Pictures یا Download شوید.
6. پوشه WSAQuickDrop را باز کنید.
