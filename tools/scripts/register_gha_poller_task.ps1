# Register a Scheduled Task to poll GitHub Actions runs for the PR branch
# Usage: Run in PowerShell (no elevated privileges required for current user):
#   pwsh -NoProfile -File .\tools\scripts\register_gha_poller_task.ps1

$scriptPath = "C:\Dev\Autofire\tools\scripts\fetch_gha_runs.ps1"
if (-not (Test-Path $scriptPath)) {
    Write-Error "Poller script not found at: $scriptPath"
    exit 2
}

$pwshArgs = "-NoProfile -WindowStyle Hidden -Command ""Set-Location 'C:\\Dev\\Autofire'; & 'C:\\Dev\\Autofire\\tools\\scripts\\fetch_gha_runs.ps1' -Owner 'Obayne' -Repo 'AutoFireBase' -Branch 'copilot/vscode1761173822319' -OutDir 'C:/Dev/pwsh-diagnostics'"""

# Build the action (runs pwsh with the above arguments)
$action = New-ScheduledTaskAction -Execute 'pwsh.exe' -Argument $pwshArgs

# Trigger: run once now and repeat every 5 minutes for 10 years
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)

# Register task for current user
$taskName = 'AutoFire_GHA_Poller'
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description 'Poll GitHub Actions runs for PR #39' -Force
    Write-Output "Scheduled Task '$taskName' registered successfully for the current user."
} catch {
    Write-Error "Failed to register Scheduled Task: $_"
    exit 1
}

# Show basic status
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State, Actions
