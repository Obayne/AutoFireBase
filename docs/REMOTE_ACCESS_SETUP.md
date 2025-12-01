# Remote Access Setup for AutoFire

This guide helps you connect to your AutoFire development environment from your Android phone.

## 🔧 Option 1: VS Code Remote Tunnels (Recommended - FREE)

**Best for**: Secure, authenticated access to VS Code from anywhere

### Setup Steps

1. **On Your Windows Dev Machine:**

   ```powershell
   # Install VS Code CLI if not already available
   # (VS Code usually includes this)

   # Create a tunnel
   code tunnel
   ```

2. **First Time Setup:**
   - You'll be prompted to authenticate with GitHub or Microsoft
   - Give your tunnel a name (e.g., "autofire-dev")
   - The tunnel will start and give you a URL

3. **Access from Android:**
   - Open browser on Android
   - Go to: `https://vscode.dev/tunnel/<your-tunnel-name>`
   - Sign in with same GitHub/Microsoft account
   - Full VS Code experience in browser!

4. **Keep Tunnel Running:**

   ```powershell
   # Run as background service (Windows)
   code tunnel service install
   ```

### Pros

- ✅ FREE (built into VS Code)
- ✅ Secure (GitHub/Microsoft authentication)
- ✅ Full VS Code in browser
- ✅ No port forwarding needed
- ✅ Works through firewalls

---

## 🔧 Option 2: GitHub Codespaces (FREE Tier Available)

**Best for**: Cloud-based development, no local machine needed

### Setup

1. Push your code to GitHub (already done ✅)
2. On GitHub repo page, click "Code" → "Codespaces" → "Create codespace"
3. Access from Android browser at `github.com/codespaces`

### Free Tier

- 60 hours/month free
- 2 cores, 4GB RAM

---

## 🔧 Option 3: Tailscale + Port Forwarding (FREE)

**Best for**: Direct access to running application

### Setup Steps

1. **Install Tailscale on Windows:**

   ```powershell
   # Download from https://tailscale.com/download/windows
   # Or use winget
   winget install tailscale.tailscale
   ```

2. **Install Tailscale on Android:**
   - Install from Google Play Store
   - Sign in with same account

3. **Connect:**
   - Both devices now on same private network
   - Access dev server at Tailscale IP (e.g., `http://100.x.x.x:8000`)

### Pros

- ✅ FREE for personal use
- ✅ Secure WireGuard VPN
- ✅ Direct access to local services
- ✅ Works with any app/port

---

## 🔧 Option 4: ngrok (FREE Tier)

**Best for**: Quick temporary access, demos

### Setup

```powershell
# Install ngrok
winget install ngrok.ngrok

# Authenticate (sign up at ngrok.com for free)
ngrok config add-authtoken <your-token>

# Expose a port (e.g., development server on 8000)
ngrok http 8000
```

### Android Access

- Use the forwarding URL ngrok provides
- Example: `https://abc123.ngrok-free.app`

### Free Tier Limits

- 1 online ngrok process
- 40 connections/minute
- Random URLs (or 1 static domain)

---

## 📱 Recommended Android Apps

### For Remote Development

1. **VS Code Web** (via browser) - Use with VS Code Tunnels
2. **GitHub Mobile** - For code review and PR management
3. **Termux** - Full terminal on Android (advanced)

### For Viewing/Testing

1. **Chrome** or **Firefox** - For web-based access
2. **Tailscale** - For private network access
3. **RD Client** - For full Windows Remote Desktop (overkill for dev)

---

## 🎯 Quick Start Recommendation

**For you, I recommend VS Code Remote Tunnels because:**

1. ✅ Already have VS Code installed
2. ✅ Completely FREE
3. ✅ Secure authentication
4. ✅ No configuration needed
5. ✅ Works from anywhere
6. ✅ No firewall/router changes

### Let's Set It Up Now

Run this in PowerShell:

```powershell
# Start VS Code tunnel
code tunnel

# Or install as service to run automatically
code tunnel service install
```

Then access from your Android phone at:

```text
https://vscode.dev/tunnel/<your-tunnel-name>
```

---

## 🔒 Security Best Practices

1. **Use Strong Authentication**
   - Enable 2FA on GitHub/Microsoft account
   - Don't share tunnel names publicly

2. **Firewall Rules**
   - VS Code Tunnels: No changes needed ✅
   - Tailscale: No changes needed ✅
   - ngrok: No changes needed ✅

3. **Monitoring**
   - Check VS Code tunnel logs for connections
   - Review Tailscale device list regularly

---

## 🆘 Troubleshooting

### "Can't connect to tunnel"

- Verify tunnel is running: `code tunnel status`
- Check authentication matches on both devices
- Try restarting tunnel

### "Connection refused"

- Check firewall isn't blocking VS Code
- Verify tunnel service is running
- Check Windows Defender settings

### "Slow performance"

- Use Tailscale for better direct connection
- Consider GitHub Codespaces for cloud-based work
- Check your internet connection speed

---

## 💰 Cost Comparison

| Tool | Cost | Limits |
|------|------|--------|
| **VS Code Tunnels** | FREE | Unlimited |
| **Tailscale** | FREE | 1 user, unlimited devices |
| **GitHub Codespaces** | FREE | 60 hrs/month |
| **ngrok** | FREE | 1 process, 40 conn/min |

---

## 📝 Next Steps

1. Choose your preferred method (I recommend **VS Code Tunnels**)
2. Run the setup commands above
3. Test connection from Android
4. Save bookmark on phone for easy access

Need help with any specific setup? Let me know!
