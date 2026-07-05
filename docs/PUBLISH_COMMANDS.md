# Publish Commands

These commands are for manual publishing only. Do not run them from automation unless you intentionally want to publish.

## If No Remote Exists

```powershell
gh repo create wsa-quickdrop --public --source . --remote origin --push
```

## If A Remote Already Exists

```powershell
git push origin main
git push origin v0.2.0
```

## Create GitHub Release

Command Prompt style:

```cmd
gh release create v0.2.0 ^
  release/WSAQuickDrop-v0.2.0-win-x64.zip ^
  release/WSAQuickDrop-v0.2.0-win-x64.zip.sha256 ^
  --title "WSA QuickDrop v0.2.0" ^
  --notes-file docs/RELEASE_NOTES_v0.2.0.md
```

PowerShell style:

```powershell
gh release create v0.2.0 `
  release/WSAQuickDrop-v0.2.0-win-x64.zip `
  release/WSAQuickDrop-v0.2.0-win-x64.zip.sha256 `
  --title "WSA QuickDrop v0.2.0" `
  --notes-file docs/RELEASE_NOTES_v0.2.0.md
```
