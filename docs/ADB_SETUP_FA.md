# راه‌اندازی ADB

WSA QuickDrop فایل ADB را همراه خودش نصب نمی‌کند. Android SDK Platform-Tools را از سایت رسمی Android Developer نصب کنید.

## نصب Platform-Tools

1. نسخه Windows از Android SDK Platform-Tools را دانلود کنید.
2. فایل zip را مثلا در `C:\Android\platform-tools` extract کنید.
3. مطمئن شوید `adb.exe` داخل آن پوشه وجود دارد.

## اضافه کردن ADB به PATH

1. در جست‌وجوی ویندوز Environment Variables را پیدا کنید.
2. User Path را ویرایش کنید.
3. مسیر Platform-Tools را اضافه کنید، مثلا `C:\Android\platform-tools`.
4. یک PowerShell جدید باز کنید.

تست:

```powershell
adb version
```

## انتخاب دستی ADB

اگر نمی‌خواهید PATH را تغییر دهید، برنامه WSA QuickDrop را باز کنید و Browse adb.exe را بزنید.

مسیر انتخاب‌شده در این فایل ذخیره می‌شود:

```text
%APPDATA%\WSAQuickDrop\config.json
```
