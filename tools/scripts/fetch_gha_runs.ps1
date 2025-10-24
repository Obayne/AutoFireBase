# Fetch GitHub Actions runs for a branch and download logs for failed jobs
# Usage: Set GITHUB_TOKEN in your user or process env and run from repo root
param(
    [string]$Owner = 'Obayne',
    [string]$Repo = 'AutoFireBase',
    [string]$Branch = 'copilot/vscode1761173822319',
    [string]$OutDir = 'C:/Dev/pwsh-diagnostics'
)
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$token = [Environment]::GetEnvironmentVariable('GITHUB_TOKEN','User')
if (-not $token) { Write-Error 'GITHUB_TOKEN not set (user env)'; exit 1 }
$headers = @{ Authorization = 'token ' + $token; 'User-Agent' = 'autobot' }
$base = "https://api.github.com/repos/$Owner/$Repo"
Write-Host "Querying runs for branch: $Branch"
$runs = Invoke-RestMethod -Headers $headers -Uri ("$base/actions/runs?branch=$Branch&per_page=50") -Method Get
$outSummary = Join-Path $OutDir 'fetch_gha_runs_summary.txt'
Remove-Item -Path $outSummary -ErrorAction SilentlyContinue
foreach ($run in $runs.workflow_runs | Sort-Object created_at -Descending) {
    $line = "{0} | {1} | {2} | {3} | {4}" -f $run.id, $run.name, $run.status, $run.conclusion, $run.html_url
    Add-Content -Path $outSummary -Value $line
}
Write-Host "Saved run summary to: $outSummary"
$failed = $runs.workflow_runs | Where-Object { $_.status -eq 'completed' -and $_.conclusion -ne 'success' }
foreach ($fr in $failed) {
    Write-Host "Downloading logs for run: $($fr.id) - $($fr.name)"
    $runZip = Join-Path $OutDir ("run-$($fr.id)-logs.zip")
    Invoke-WebRequest -Headers $headers -Uri ("$base/actions/runs/$($fr.id)/logs") -OutFile $runZip -UseBasicParsing
    Write-Host "  Saved: $runZip"
    $jobsResp = Invoke-RestMethod -Headers $headers -Uri ("$base/actions/runs/$($fr.id)/jobs") -Method Get
    foreach ($job in $jobsResp.jobs) {
        if ($job.conclusion -ne 'success') {
            Write-Host "  Job failed: $($job.name) ($($job.id))"
            $jobZip = Join-Path $OutDir ("job-$($job.id)-logs.zip")
            Invoke-WebRequest -Headers $headers -Uri ("$base/actions/jobs/$($job.id)/logs") -OutFile $jobZip -UseBasicParsing
            Write-Host "    Saved job logs: $jobZip"
        }
    }
}
Write-Host 'Done.'
