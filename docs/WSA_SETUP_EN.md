# WSA Setup

## Enable Developer Mode

1. Open Windows Subsystem for Android settings.
2. Enable Developer Mode.
3. Start an Android app so WSA is running.
4. Note the ADB endpoint. The default is usually `127.0.0.1:58526`.

## Test connection

```powershell
adb connect 127.0.0.1:58526
adb devices
```

You should see a device similar to:

```text
127.0.0.1:58526    device
```

When this is ready, WSA QuickDrop can list folders under Pixel 5 and send files to the selected folder.

## If connection is refused

- Make sure WSA is running.
- Open an Android app once.
- Confirm Developer Mode is enabled.
- Confirm the port in WSA settings.
- Restart WSA and retry.
- In WSA QuickDrop, click Connect, then Refresh folders.
