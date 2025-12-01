# Quick Start: VS Code Remote Tunnel Setup

## 1. On Your Windows Machine (One-time setup)

Open PowerShell and run:

```powershell
# Start the tunnel
code tunnel
```

**What happens:**

- You'll be prompted to sign in with GitHub or Microsoft
- Give your tunnel a name (e.g., "autofire-dev")
- The tunnel will start and display a URL

**To keep it running permanently:**

```powershell
# Install as Windows service (runs at startup)
code tunnel service install
```

## 2. On Your Android Phone

1. Open any browser (Chrome, Firefox, etc.)
2. Go to: `https://vscode.dev`
3. Click "Open Remote Tunnel"
4. Sign in with the **same account** you used on Windows
5. Select your tunnel name
6. You now have full VS Code access! 🎉

## That's it! Completely FREE and secure

---

## Quick Commands Reference

```powershell
# Check tunnel status
code tunnel status

# Stop tunnel
code tunnel kill

# Uninstall tunnel service
code tunnel service uninstall

# View tunnel logs
code tunnel logs
```

## Tips

- **Bookmark the tunnel URL** on your phone for quick access
- **Battery**: Tunnel uses minimal resources on Windows
- **Security**: Only accessible with your authenticated account
- **Files**: Full access to your workspace, can edit and run commands

## Testing Your Setup

1. Start tunnel on Windows
2. Open `https://vscode.dev/tunnel/<your-name>` on Android
3. Navigate to AutoFire workspace
4. Try editing a file
5. Open terminal and run commands

Everything works just like local VS Code!
