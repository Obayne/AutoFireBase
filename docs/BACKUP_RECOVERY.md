# Backup and Recovery

## Overview

This guide covers data protection strategies for AutoFireBase projects and configuration.

## What to Back Up

### Critical Data

1. **Project Files** (`.afp` files)
   - CAD drawings and layouts
   - Device placements
   - Wire routing
   - Coverage calculations

2. **Configuration Files**
   - `autofire.json`: Application settings
   - `manifest.json`: Project metadata
   - User preferences
   - Custom tool configurations

3. **Export Data**
   - DXF exports
   - PDF reports
   - BOM (Bill of Materials) CSV files
   - Coverage analysis reports

### Optional Data

- Session logs (`communication_logs/`)
- Temporary files (can be regenerated)
- Cache files (can be rebuilt)

## Backup Strategies

### Manual Backup

#### Project Files

```powershell
# Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$projectName = "MyProject"
$backupPath = "C:\Backups\AutoFire\${projectName}_${timestamp}.zip"

# Compress project directory
Compress-Archive -Path "C:\Projects\$projectName\" -DestinationPath $backupPath
```

#### Configuration Backup

```powershell
# Backup application configuration
$configBackup = "C:\Backups\AutoFire\Config_${timestamp}.zip"
Compress-Archive -Path "$env:APPDATA\AutoFire\" -DestinationPath $configBackup
```

### Automated Backup

#### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 6 PM)
4. Action: Run PowerShell script

**Backup Script** (`backup_autofire.ps1`):

```powershell
param(
    [string]$ProjectsRoot = "C:\Projects",
    [string]$BackupRoot = "C:\Backups\AutoFire"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Ensure backup directory exists
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

# Backup all projects
Get-ChildItem -Path $ProjectsRoot -Directory | ForEach-Object {
    $projectName = $_.Name
    $backupFile = Join-Path $BackupRoot "${projectName}_${timestamp}.zip"

    Write-Host "Backing up $projectName..."
    Compress-Archive -Path $_.FullName -DestinationPath $backupFile -Force
}

# Clean up old backups (keep last 30 days)
$cutoffDate = (Get-Date).AddDays(-30)
Get-ChildItem -Path $BackupRoot -Filter "*.zip" |
    Where-Object { $_.LastWriteTime -lt $cutoffDate } |
    Remove-Item -Force

Write-Host "Backup completed at $timestamp"
```

#### Cloud Sync

Use cloud storage for automatic backup:

**OneDrive Setup**:

```powershell
# Move projects to OneDrive
Move-Item "C:\Projects" "$env:OneDrive\AutoFire_Projects"

# Create symbolic link
New-Item -ItemType SymbolicLink -Path "C:\Projects" -Target "$env:OneDrive\AutoFire_Projects"
```

**Google Drive / Dropbox**:

- Configure sync folder
- Move/link project directory
- Enable version history

### Version Control (Git)

For text-based configuration and scripts:

```powershell
# Initialize project repository
cd C:\Projects\MyProject
git init
git add .
git commit -m "Initial project state"

# Push to remote (GitHub, GitLab, etc.)
git remote add origin https://github.com/username/myproject.git
git push -u origin main
```

**Note**: Binary CAD files may not benefit from git versioning.

## Recovery Procedures

### Restore from Backup

#### Full Project Restore

```powershell
# Extract backup
$backupFile = "C:\Backups\AutoFire\MyProject_20250101_120000.zip"
$restorePath = "C:\Projects\MyProject_Restored"

Expand-Archive -Path $backupFile -DestinationPath $restorePath

# Verify integrity
if (Test-Path "$restorePath\manifest.json") {
    Write-Host "Project restored successfully"
} else {
    Write-Error "Restoration failed - manifest not found"
}
```

#### Selective File Restore

```powershell
# Extract specific files from backup
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zip = [System.IO.Compression.ZipFile]::OpenRead($backupFile)
$file = $zip.Entries | Where-Object { $_.Name -eq "critical_layout.afp" }
$file.ExtractToFile("C:\Recovered\critical_layout.afp", $true)
$zip.Dispose()
```

### Configuration Restore

```powershell
# Restore application settings
$configBackup = "C:\Backups\AutoFire\Config_20250101_120000.zip"
Expand-Archive -Path $configBackup -DestinationPath "$env:APPDATA\AutoFire" -Force
```

### Disaster Recovery

#### Complete System Failure

1. **Install AutoFireBase** on new system
2. **Restore backups** from cloud/external drive
3. **Verify configurations** (check paths, settings)
4. **Test project loading** - open sample project
5. **Validate functionality** - run basic operations

#### Corrupted Project File

1. **Locate latest backup**
2. **Compare timestamps** - find pre-corruption backup
3. **Restore backup copy**
4. **Test file integrity** - ensure project opens
5. **Re-apply recent changes** if possible

#### Lost Configuration

1. **Run AutoFireBase** - will create default config
2. **Restore from backup** if available
3. **Manually reconfigure** if necessary

## Data Integrity

### Verification

**Checksum Verification**:

```powershell
# Generate checksum
$hash = Get-FileHash -Path "MyProject.afp" -Algorithm SHA256
$hash.Hash | Out-File "MyProject.afp.sha256"

# Verify checksum
$originalHash = Get-Content "MyProject.afp.sha256"
$currentHash = (Get-FileHash -Path "MyProject.afp" -Algorithm SHA256).Hash

if ($originalHash -eq $currentHash) {
    Write-Host "File integrity verified ✓"
} else {
    Write-Error "File corrupted - restore from backup"
}
```

### Auto-save

AutoFireBase auto-saves every 5 minutes (configurable):

```json
// autofire.json
{
  "autosave": {
    "enabled": true,
    "interval_seconds": 300,
    "max_backups": 10
  }
}
```

Auto-save location: `%TEMP%\AutoFire\AutoSave\`

## Backup Best Practices

### 3-2-1 Rule

- **3 copies** of data (original + 2 backups)
- **2 different media** (local drive + external/cloud)
- **1 offsite** copy (cloud storage)

### Backup Schedule

- **Continuous**: Auto-save (every 5 minutes)
- **Daily**: Local backup (end of workday)
- **Weekly**: Cloud backup (Sunday evening)
- **Monthly**: Archive to external drive

### Testing Backups

```powershell
# Monthly backup test script
$testBackup = Get-ChildItem "C:\Backups\AutoFire" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

Write-Host "Testing backup: $($testBackup.Name)"

# Try to extract
$testExtract = "$env:TEMP\BackupTest"
Expand-Archive -Path $testBackup.FullName -DestinationPath $testExtract -Force

# Verify key files exist
$required = @("manifest.json", "*.afp")
$allPresent = $required | ForEach-Object {
    Test-Path (Join-Path $testExtract $_)
} | Where-Object { $_ -eq $false } | Measure-Object | Select-Object -ExpandProperty Count

if ($allPresent -eq 0) {
    Write-Host "Backup verified successfully ✓"
} else {
    Write-Error "Backup test failed - restore may not work"
}

# Cleanup
Remove-Item $testExtract -Recurse -Force
```

## Storage Requirements

### Estimates

- **Average Project**: 10-50 MB
- **Large Project**: 100-500 MB
- **Daily Backup** (10 projects): ~1 GB
- **Monthly Retention**: ~30 GB

### Cleanup

```powershell
# Remove backups older than 90 days
$retention = 90
$cutoff = (Get-Date).AddDays(-$retention)

Get-ChildItem "C:\Backups\AutoFire" -Recurse -File |
    Where-Object { $_.LastWriteTime -lt $cutoff } |
    Remove-Item -Force -Verbose
```

## Compliance

### Data Retention Policies

- **Active Projects**: Indefinite retention
- **Completed Projects**: 7 years (industry standard)
- **Backups**: 30-90 days rolling window
- **Logs**: 30 days

### Privacy Considerations

- Exclude sensitive client data from cloud backups if required
- Encrypt backups containing confidential information
- Follow organizational data handling policies

## Troubleshooting

### Backup Fails

- **Check disk space**: Ensure backup destination has space
- **Verify permissions**: Run backup as administrator if needed
- **Check locks**: Close AutoFireBase before backup
- **Review logs**: Check Windows Event Viewer

### Restore Fails

- **Verify backup integrity**: Check file size, test extract
- **Check target path**: Ensure destination is writable
- **Version compatibility**: Ensure backup matches AutoFire version

## Resources

- Windows Backup: <https://support.microsoft.com/windows-backup>
- Git LFS for large files: <https://git-lfs.github.com/>
- Cloud storage comparison: [Link to comparison guide]
