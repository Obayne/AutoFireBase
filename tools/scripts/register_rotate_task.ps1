# Register a Scheduled Task to run the rotate_repo_secret.ps1 daily at 02:00 (local time)
$scriptPath = "C:\Dev\Autofire\tools\scripts\rotate_repo_secret.ps1"
if (-not (Test-Path $scriptPath)) {
    Write-Error "Script not found: $scriptPath"
    exit 2
}

$action = New-ScheduledTaskAction -Execute 'pwsh.exe' -Argument "-NoProfile -WindowStyle Hidden -File '$scriptPath'"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddHours(2) -RepetitionInterval (New-TimeSpan -Days 1) -RepetitionDuration (New-TimeSpan -Days 3650)
$taskName = 'AutoFire_Rotate_PAT'
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description 'Rotate repo PAT if C:\Dev\git_new.txt is present' -Force
    Write-Output "Scheduled Task '$taskName' registered (daily at 02:00)."
    Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State, Triggers
} catch {
    Write-Error "Failed to register Scheduled Task: $_"
    exit 1
}
