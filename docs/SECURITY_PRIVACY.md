# Security and Privacy

WSA QuickDrop is local-only.

- Files are sent locally through ADB.
- There is no server component.
- There are no analytics.
- There is no telemetry.
- Files are not uploaded to cloud services.
- Logs stay on the local machine under `%APPDATA%\WSAQuickDrop\logs`.
- The user controls which files are selected.
- ADB access requires WSA Developer Mode.
- Security-sensitive users should disable WSA Developer Mode when they are done.

## Process safety

The app uses argument-list process execution and does not use shell concatenation for Windows file paths. Android shell commands are built from validated `/sdcard/` paths and POSIX-quoted before execution.

## Custom Android paths

Custom destinations must:

- start with `/sdcard/`
- not contain `..`
- not contain control characters
- not be `/`, `/system`, `/data`, `/vendor`, `/proc`, or `/dev`

## Logs

Logs may include:

- timestamps
- app version
- ADB path
- WSA endpoint
- selected file count
- destination paths
- command success or failure
- error messages

Logs do not include file contents and are never uploaded by the app.
