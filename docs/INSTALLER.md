# Windows Installer Guide

## Overview

AutoFire uses NSIS (Nullsoft Scriptable Install System) to create a professional Windows installer that handles:

- Application installation to Program Files
- Desktop and Start Menu shortcuts
- `.afire` file association
- Add/Remove Programs registry entries
- Clean uninstallation

## Prerequisites

### 1. NSIS Installation

Download and install NSIS 3.0 or later:

- **Download**: <https://nsis.sourceforge.io/Download>
- **Install to**: `C:\Program Files (x86)\NSIS\` (default)

### 2. PyInstaller Build

The installer packages the PyInstaller output. Ensure `AutoFire.spec` is configured and builds successfully.

## Building the Installer

### Quick Build (All Steps)

```powershell
.\installer\Build-Installer.ps1
```

### Step-by-Step Build

#### 1. Build Executable

```powershell
pyinstaller AutoFire.spec --clean --noconfirm
```

Output: `dist\AutoFire\AutoFire.exe` + dependencies

#### 2. Compile Installer

```powershell
.\installer\Build-Installer.ps1 -SkipBuild
```

Or manually:

```powershell
cd installer
& "C:\Program Files (x86)\NSIS\makensis.exe" autofire-installer.nsi
```

Output: `installer\AutoFire-0.7.0-Setup.exe`

### Build Options

```powershell
# Clean build (remove old dist/build folders)
.\installer\Build-Installer.ps1 -Clean

# Only build installer (skip PyInstaller)
.\installer\Build-Installer.ps1 -SkipBuild

# Only build executable (skip NSIS)
.\installer\Build-Installer.ps1 -SkipInstaller
```

## Installer Features

### What Gets Installed

- **Application**: `C:\Program Files\AutoFire\`
  - AutoFire.exe
  - All Python runtime dependencies
  - Qt libraries
  - Application data files

- **Shortcuts**:
  - Desktop: `AutoFire.lnk`
  - Start Menu: `AutoFire\AutoFire.lnk`
  - Start Menu: `AutoFire\Uninstall.lnk`

- **File Association**:
  - `.afire` files open with AutoFire
  - Custom icon for .afire files

- **Registry**:
  - Add/Remove Programs entry
  - Uninstall information
  - File association keys

### Uninstallation

The installer creates an uninstaller that removes:

- All installed files
- All shortcuts
- All registry keys
- File associations

## Testing

### Test Installation

1. **Build installer**:

   ```powershell
   .\installer\Build-Installer.ps1
   ```

2. **Run installer** (on test VM recommended):

   ```powershell
   .\installer\AutoFire-0.7.0-Setup.exe
   ```

3. **Verify**:
   - Application launches from Start Menu
   - Desktop shortcut works
   - `.afire` files have AutoFire icon
   - Double-clicking `.afire` file opens AutoFire
   - App appears in Add/Remove Programs

4. **Test uninstall**:
   - Use Add/Remove Programs OR
   - Run `C:\Program Files\AutoFire\Uninstall.exe`
   - Verify complete removal

### Automated Testing

```powershell
# Silent install
.\AutoFire-0.7.0-Setup.exe /S

# Silent uninstall
"C:\Program Files\AutoFire\Uninstall.exe" /S
```

## Customization

### Branding

Edit `installer\autofire-installer.nsi`:

```nsis
!define APP_PUBLISHER "Your Company"
!define MUI_ICON "path\to\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "path\to\banner.bmp"
```

### File Associations

Add more file types:

```nsis
; Add .dxf association
WriteRegStr HKCR ".dxf" "" "AutoFireDXF"
WriteRegStr HKCR "AutoFireDXF\shell\open\command" "" '"$INSTDIR\${APP_EXE}" "%1"'
```

### Additional Components

```nsis
Section "Documentation" SEC_DOCS
  SetOutPath "$INSTDIR\docs"
  File /r "..\docs\*.*"
SectionEnd
```

## Troubleshooting

### NSIS Not Found

Error: `NSIS not found at: C:\Program Files (x86)\NSIS\makensis.exe`

**Solution**: Install NSIS or update path in `Build-Installer.ps1`:

```powershell
$NSIS = "C:\Your\Custom\Path\NSIS\makensis.exe"
```

### PyInstaller Output Missing

Error: `AutoFire.exe not found in dist folder!`

**Solution**: Run PyInstaller first:

```powershell
pyinstaller AutoFire.spec --clean --noconfirm
```

### Icon Not Found

Warning: `Can't find icon: ..\app\data\icon.ico`

**Solution**:

- Create icon file or
- Remove icon lines from .nsi file or
- Use default NSIS icon

### Installer Too Large

Installer >100MB may indicate unnecessary files included.

**Solution**: Check PyInstaller spec excludes list:

```python
excludes=['tkinter', 'matplotlib', 'numpy.tests'],
```

## Release Process

### 1. Update Version

Update `VERSION.txt`:

```
0.7.0
```

### 2. Build Release Installer

```powershell
# Clean build for release
.\installer\Build-Installer.ps1 -Clean

# Sign installer (optional)
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com AutoFire-0.7.0-Setup.exe
```

### 3. Test on Clean VM

- Windows 10/11 clean install
- Run installer
- Test all features
- Uninstall

### 4. Distribute

Upload to:

- GitHub Releases
- Website download page
- Microsoft Store (future)

## Future Enhancements

- [ ] Code signing certificate
- [ ] Auto-update mechanism
- [ ] Component selection (full/minimal install)
- [ ] Multiple language support
- [ ] Silent install parameters
- [ ] Custom install location
- [ ] Portable (no-install) version
