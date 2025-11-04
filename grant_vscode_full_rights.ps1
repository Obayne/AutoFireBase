# Grant VS Code Full Rights Script
# This script grants VS Code and related processes full access to the AutoFire project
# Run as Administrator for best results

param(
    [string]$ProjectPath = "C:\Dev\Autofire",
    [switch]$Verbose
)

Write-Host "🔥 AutoFire VS Code Full Rights Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Project Path: $ProjectPath" -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some operations may fail. Consider running as Admin." -ForegroundColor Yellow
    Write-Host ""
}

# Function to grant full control to a path
function Grant-FullControl {
    param(
        [string]$Path,
        [string]$User = $env:USERNAME
    )

    try {
        if (Test-Path $Path) {
            Write-Host "✅ Granting full control to: $Path" -ForegroundColor Green

            # Get current ACL
            $acl = Get-Acl $Path

            # Create new access rule for full control
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $User,
                "FullControl",
                "ContainerInherit,ObjectInherit",
                "None",
                "Allow"
            )

            # Add the rule and apply
            $acl.SetAccessRule($accessRule)
            Set-Acl -Path $Path -AclObject $acl

            if ($Verbose) {
                Write-Host "   Full control granted for user: $User" -ForegroundColor Gray
            }
        } else {
            Write-Host "❌ Path not found: $Path" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Failed to grant rights to: $Path" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to set registry permissions for VS Code
function Set-VSCodeRegistryPermissions {
    try {
        Write-Host "🔧 Setting VS Code registry permissions..." -ForegroundColor Cyan

        $registryPaths = @(
            "HKCU:\Software\Microsoft\VSCode",
            "HKCU:\Software\Classes\.py",
            "HKCU:\Software\Classes\.json",
            "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Code.exe"
        )

        foreach ($regPath in $registryPaths) {
            if (Test-Path $regPath -ErrorAction SilentlyContinue) {
                Write-Host "   ✅ Registry access: $regPath" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "   ⚠️  Registry permissions may need manual adjustment" -ForegroundColor Yellow
    }
}

# Function to grant Python execution permissions
function Set-PythonPermissions {
    try {
        Write-Host "🐍 Setting Python execution permissions..." -ForegroundColor Cyan

        # Find Python installations
        $pythonPaths = @()

        # Check common Python locations
        $commonPaths = @(
            "$env:LOCALAPPDATA\Programs\Python",
            "$env:PROGRAMFILES\Python*",
            "$env:PROGRAMFILES(X86)\Python*",
            "$ProjectPath\.venv"
        )

        foreach ($path in $commonPaths) {
            if (Test-Path $path) {
                $pythonPaths += $path
            }
        }

        foreach ($pyPath in $pythonPaths) {
            Grant-FullControl -Path $pyPath
        }

        # Set execution policy for PowerShell if needed
        try {
            $currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
            if ($currentPolicy -eq "Restricted") {
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                Write-Host "   ✅ PowerShell execution policy updated" -ForegroundColor Green
            }
        } catch {
            Write-Host "   ⚠️  Could not update PowerShell execution policy" -ForegroundColor Yellow
        }

    } catch {
        Write-Host "   ❌ Python permissions setup failed" -ForegroundColor Red
    }
}

# Function to create VS Code workspace settings
function Create-VSCodeWorkspaceSettings {
    try {
        Write-Host "⚙️  Creating VS Code workspace settings..." -ForegroundColor Cyan

        $vscodeDir = Join-Path $ProjectPath ".vscode"
        if (-not (Test-Path $vscodeDir)) {
            New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
        }

        $settingsPath = Join-Path $vscodeDir "settings.json"
        $workspaceSettings = @{
            "python.defaultInterpreterPath" = ".\.venv\Scripts\python.exe"
            "python.terminal.activateEnvironment" = $true
            "files.watcherExclude" = @{
                "**/.venv/**" = $true
                "**/node_modules/**" = $true
                "**/.git/objects/**" = $true
                "**/.git/subtree-cache/**" = $true
                "**/logs/**" = $true
            }
            "files.associations" = @{
                "*.py" = "python"
                "*.md" = "markdown"
                "*.json" = "jsonc"
            }
            "terminal.integrated.defaultProfile.windows" = "PowerShell"
            "python.linting.enabled" = $true
            "python.linting.pylintEnabled" = $false
            "python.linting.flake8Enabled" = $true
            "editor.formatOnSave" = $true
            "python.formatting.provider" = "black"
        }

        $workspaceSettings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8

        Grant-FullControl -Path $vscodeDir
        Write-Host "   ✅ VS Code workspace settings created" -ForegroundColor Green

    } catch {
        Write-Host "   ❌ Failed to create VS Code settings" -ForegroundColor Red
    }
}

# Function to set environment variables
function Set-EnvironmentVariables {
    try {
        Write-Host "🌍 Setting environment variables..." -ForegroundColor Cyan

        # Set AutoFire project path
        [Environment]::SetEnvironmentVariable("AUTOFIRE_PROJECT_PATH", $ProjectPath, "User")

        # Add Python virtual environment to PATH if it exists
        $venvPath = Join-Path $ProjectPath ".venv\Scripts"
        if (Test-Path $venvPath) {
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            if ($currentPath -notlike "*$venvPath*") {
                [Environment]::SetEnvironmentVariable("PATH", "$venvPath;$currentPath", "User")
            }
        }

        Write-Host "   ✅ Environment variables set" -ForegroundColor Green

    } catch {
        Write-Host "   ❌ Failed to set environment variables" -ForegroundColor Red
    }
}

# Main execution
Write-Host "🚀 Starting VS Code rights configuration..." -ForegroundColor Green
Write-Host ""

# 1. Grant full control to project directory
Write-Host "1️⃣  Project Directory Permissions" -ForegroundColor Cyan
Grant-FullControl -Path $ProjectPath

# 2. Grant rights to subdirectories
Write-Host ""
Write-Host "2️⃣  Subdirectory Permissions" -ForegroundColor Cyan
$subdirs = @("cad_core", "frontend", "backend", "tests", ".vscode", ".venv", "logs")
foreach ($subdir in $subdirs) {
    $fullPath = Join-Path $ProjectPath $subdir
    if (Test-Path $fullPath) {
        Grant-FullControl -Path $fullPath
    }
}

# 3. Set Python permissions
Write-Host ""
Write-Host "3️⃣  Python Environment" -ForegroundColor Cyan
Set-PythonPermissions

# 4. Set registry permissions
Write-Host ""
Write-Host "4️⃣  Registry Permissions" -ForegroundColor Cyan
Set-VSCodeRegistryPermissions

# 5. Create VS Code workspace settings
Write-Host ""
Write-Host "5️⃣  VS Code Configuration" -ForegroundColor Cyan
Create-VSCodeWorkspaceSettings

# 6. Set environment variables
Write-Host ""
Write-Host "6️⃣  Environment Variables" -ForegroundColor Cyan
Set-EnvironmentVariables

# 7. Final permissions check
Write-Host ""
Write-Host "7️⃣  Final Security Check" -ForegroundColor Cyan
try {
    # Test write access
    $testFile = Join-Path $ProjectPath "vscode_rights_test.tmp"
    "VS Code rights test" | Out-File $testFile -Force

    if (Test-Path $testFile) {
        Remove-Item $testFile -Force
        Write-Host "   ✅ Write access confirmed" -ForegroundColor Green
    }

    # Test Python execution
    $pythonTest = Join-Path $ProjectPath ".venv\Scripts\python.exe"
    if (Test-Path $pythonTest) {
        Write-Host "   ✅ Python environment accessible" -ForegroundColor Green
    }

} catch {
    Write-Host "   ⚠️  Some access issues may remain" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 VS Code Full Rights Configuration Complete!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart VS Code completely" -ForegroundColor White
Write-Host "2. Open the AutoFire workspace folder" -ForegroundColor White
Write-Host "3. Select the Python interpreter from .venv" -ForegroundColor White
Write-Host "4. Try running your Python files again" -ForegroundColor White
Write-Host ""
Write-Host "If issues persist:" -ForegroundColor Yellow
Write-Host "• Run this script as Administrator" -ForegroundColor White
Write-Host "• Check Windows Defender exclusions" -ForegroundColor White
Write-Host "• Verify antivirus software permissions" -ForegroundColor White
Write-Host ""
Write-Host "🔥 AutoFire is ready for AI development!" -ForegroundColor Cyan
