Param()

Write-Host "==============================================="
Write-Host "  AutoFire PowerShell Build (DEBUG console)"
Write-Host "==============================================="

if (!(Test-Path .\app)) { Write-Host "ERROR: 'app' folder not found here." -ForegroundColor Red; exit 1 }
if (!(Test-Path .\app\boot.py)) { Write-Host "ERROR: app\boot.py missing." -ForegroundColor Red; exit 1 }

$py = "py"
try { & $py -V | Out-Null } catch { $py = "python" }
try { & $py -V | Out-Null } catch { Write-Host "ERROR: Python not found." -ForegroundColor Red; exit 1 }

Write-Host "Installing build requirements (pip, PySide6, ezdxf, packaging, pyinstaller) ..."
& $py -m pip install --upgrade pip
& $py -m pip install PySide6 ezdxf packaging pyinstaller

Write-Host "Building AutoFire_Debug.exe (console visible) ..."

& $py -m PyInstaller --noconfirm --clean --console --name AutoFire_Debug --paths . --add-data "VERSION.txt;." `
  --hidden-import app `
  --hidden-import app.main `
  --hidden-import app.minwin `
  --hidden-import app.scene `
  --hidden-import app.device `
  --hidden-import app.catalog `
  --hidden-import app.tools `
  --hidden-import app.tools.draw `
  --hidden-import core.logger `
  --hidden-import core.logger_bridge `
  --hidden-import core.error_hook `
  --hidden-import updater.auto_update `
  app\boot.py

if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: PyInstaller failed." -ForegroundColor Red; exit 1 }

Write-Host "Run this to see live logs and errors:" -ForegroundColor Yellow
Write-Host ".\dist\AutoFire_Debug\AutoFire_Debug.exe"