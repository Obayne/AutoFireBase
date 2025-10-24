# Rotate repository secret when a new PAT is supplied in C:\Dev\git_new.txt
# Usage: drop a new token (plain text) into C:\Dev\git_new.txt and the scheduled task will pick it up and update the repo secret.
# The script uploads using the local helper `tools/create_repo_secret.py` which encrypts and uploads the secret.

$tokenFile = 'C:\Dev\git_new.txt'
$repoOwner = 'Obayne'
$repoName = 'AutoFireBase'
$secretName = 'AUTOBOT_TOKEN'

Set-Location 'C:\Dev\Autofire'

if (-not (Test-Path $tokenFile)) {
    Write-Output "No token file present at $tokenFile; skipping rotation"
    exit 0
}

try {
    Write-Output "Found token file. Rotating repo secret $secretName for $repoOwner/$repoName"
    python .\tools\create_repo_secret.py --owner $repoOwner --repo $repoName --name $secretName --token-path $tokenFile
    if (Test-Path $tokenFile) {
        Remove-Item $tokenFile -Force
        Write-Output "Removed local token file: $tokenFile"
    }
    python .\tools\automation\append_activity.py "Rotated repo secret '$secretName' from local token file $tokenFile"
} catch {
    Write-Error "Secret rotation failed: $_"
    python .\tools\automation\append_activity.py "Failed secret rotation attempt: $($_.Exception.Message)"
}
