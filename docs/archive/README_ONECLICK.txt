HOW TO USE (no programming needed)
----------------------------------
1) Put this file (Build_AutoFire.cmd) AND the other patches in your "AutoFire Base" folder.
2) First apply the updater patch (only once):
     python tools\apply_patch.py --project "." --patch ".\patch_0.4.5-fixC.zip"
3) Double‑click Build_AutoFire.cmd
   - It installs what it needs and builds dist\AutoFire\AutoFire.exe
4) Create C:\AutoFireUpdates and drop new patch .zip files there.
   - Each time you start AutoFire.exe, it will auto‑install newer patches.