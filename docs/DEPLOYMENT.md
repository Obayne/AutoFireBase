# Deployment Guide

## Overview

This guide covers deployment strategies for AutoFireBase across different environments.

## Prerequisites

- Python 3.11+
- Windows 10/11 (64-bit)
- 4GB RAM minimum, 8GB recommended
- 500MB disk space

## Deployment Methods

### 1. Standalone Executable (Recommended for End Users)

#### Building the Executable

```powershell
# Clone repository
git clone https://github.com/Obayne/AutoFireBase.git
cd AutoFireBase

# Set up development environment
./setup_dev.ps1

# Build production executable
./Build_AutoFire.ps1
```

The executable will be created in `dist/AutoFire/AutoFire.exe`.

#### Distribution

1. Compress the `dist/AutoFire/` folder
2. Distribute the ZIP file to end users
3. Users extract and run `AutoFire.exe`

**No Python installation required for end users.**

### 2. Python Environment Deployment

For developers or users who need to modify the codebase:

```powershell
# Clone repository
git clone https://github.com/Obayne/AutoFireBase.git
cd AutoFireBase

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run application
python app/main.py
```

### 3. CI/CD Automated Deployment

GitHub Actions automatically builds releases when tags are pushed:

```powershell
# Create and push a version tag
git tag -a v0.4.8 -m "Release version 0.4.8"
git push origin v0.4.8
```

The workflow will:

1. Build Windows executable
2. Run all tests
3. Create GitHub release
4. Attach build artifacts

## Configuration

### Environment Variables

- `AUTOFIRE_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `AUTOFIRE_DATA_DIR`: Override default data directory
- `AUTOFIRE_PLUGINS_DIR`: Custom plugins directory

### Configuration Files

- `autofire.json`: Application settings
- `manifest.json`: Project metadata
- `.env`: Local environment overrides (not committed)

## System Requirements

### Minimum

- CPU: Dual-core 2.0 GHz
- RAM: 4GB
- Disk: 500MB free space
- Display: 1280x720

### Recommended

- CPU: Quad-core 3.0 GHz+
- RAM: 8GB+
- Disk: 1GB+ free space
- Display: 1920x1080 or higher
- Graphics: Dedicated GPU for large drawings

## Troubleshooting

### Common Issues

**Issue**: Application fails to start
**Solution**: Check `debug_run.log` for errors, ensure all dependencies are installed

**Issue**: DXF import failures
**Solution**: Verify DXF file version (R2010-R2018 supported), check file permissions

**Issue**: Performance degradation with large files
**Solution**: Increase system RAM, close unnecessary applications, use file optimization tools

## Monitoring

See [MONITORING.md](./MONITORING.md) for production monitoring setup.

## Backup and Recovery

See [BACKUP_RECOVERY.md](./BACKUP_RECOVERY.md) for data protection strategies.

## Security

- Never commit sensitive credentials to version control
- Use environment variables for API keys
- Regular security audits via CodeQL (automated)
- Keep dependencies updated via Dependabot

## Support

- GitHub Issues: <https://github.com/Obayne/AutoFireBase/issues>
- Documentation: <https://obayne.github.io/AutoFireBase/>
- Email: [Support contact]

## Version Compatibility

| AutoFire Version | Python | PySide6 | ezdxf |
|------------------|--------|---------|-------|
| 0.4.7+           | 3.11   | 6.10    | 1.x   |
| 0.4.0-0.4.6      | 3.11   | 6.8+    | 1.x   |
| <0.4.0           | 3.10+  | 6.6+    | 0.x   |

## License

See [LICENSE](../LICENSE) for licensing information.
