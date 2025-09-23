# AutoFire Project Hub (PowerShell Menu) - Clean Fixed Version

param(
  [string]$ConfigPath = "$(Split-Path -Parent $PSCommandPath)\agent.config.json"
)

function Load-Config {
  param([string]$Path)
  if (Test-Path $Path) { return (Get-Content -Raw $Path | ConvertFrom-Json) }
  throw "Config not found: $Path"
}

function Today-LogDir {
  param([string]$Repo,[string]$LogsRoot="logs")
  $date = Get-Date -Format "yyyy-MM-dd"
  $p = Join-Path $Repo $LogsRoot
  $p = Join-Path $p $date
  New-Item -ItemType Directory -Force -Path $p | Out-Null
  return $p
}

function Pause-Enter { Write-Host ""; Read-Host "Press Enter to continue" | Out-Null }

$cfg = Load-Config -Path $ConfigPath
$Repo = $cfg.repoPath
$Main = $cfg.mainBranch
$VersionFile = Join-Path $Repo $cfg.versionFile
$Updater = $cfg.updaterDir
$Logs = Today-LogDir -Repo $Repo

Write-Host ""
Write-Host "==== AutoFire Project Hub ====" -ForegroundColor Cyan
Write-Host "Repo: $Repo"
Write-Host "Main branch: $Main"
Write-Host "Logs: $Logs"
Write-Host ""

function Start-Day {
  Push-Location $Repo
  try {
    git status
    $ans = Read-Host "Pull latest from origin/$Main (y/N)"
    if ($ans -match "^[yY]") { git pull --ff-only origin $Main }
    Start-Process explorer.exe $Repo
    Start-Process explorer.exe $Logs
  } finally { Pop-Location }
}

function Build-Project {
  Push-Location (Join-Path $PSScriptRoot "scripts")
  try {
    .\Build_AutoFire.ps1 -Repo $Repo *>&1 | Tee-Object -FilePath (Join-Path $Logs "build.log")
  } finally { Pop-Location }
  Pause-Enter
}

function Run-Tests {
  Push-Location (Join-Path $PSScriptRoot "scripts")
  try {
    .\Run_Tests.ps1 -Repo $Repo *>&1 | Tee-Object -FilePath (Join-Path $Logs "tests.log")
  } finally { Pop-Location }
  Pause-Enter
}

function Create-Branch {
  $name = Read-Host "Feature name (e.g., ui-array-spacing)"
  if (-not $name) { return }
  $branch = "feat/$name"
  Push-Location $Repo
  try {
    git checkout $Main
    git pull --ff-only
    git checkout -b $branch
    Write-Host "Now on $branch"
  } finally { Pop-Location }
  Pause-Enter
}

function Commit-Helper {
  $types = @("feat","fix","chore","docs","refactor","perf","test","build","ci")
  $t = Read-Host ("Type " + ($types -join "|"))
  if (-not $types.Contains($t)) { Write-Host "Unknown type."; return }
  $scope = Read-Host "Scope (optional, e.g., ui)"
  $msg = Read-Host "Message (imperative)"
  if (-not $msg) { return }
  $scopeTxt = if ($scope) { "($scope)" } else { "" }
  $full = "$t${scopeTxt}: $msg"   # FIXED with ${}
  Push-Location $Repo
  try {
    git add -A
    git commit -m "$full"
    Write-Host "Committed: $full"
  } finally { Pop-Location }
  Pause-Enter
}

function Bump-Version {
  param([ValidateSet("patch","minor","major")]$Kind="patch")
  $cur = "0.0.0"
  if (Test-Path $VersionFile) {
    $txt = Get-Content -Raw $VersionFile
    if ($txt -match "(\d+\.\d+\.\d+)") { $cur = $Matches[1] }
  }
  $parts = $cur.Split(".")
  while ($parts.Count -lt 3) { $parts += "0" }
  $maj=[int]$parts[0]; $min=[int]$parts[1]; $pat=[int]$parts[2]
  switch ($Kind) {
    "patch" { $pat++ }
    "minor" { $min++; $pat=0 }
    "major" { $maj++; $min=0; $pat=0 }
  }
  $new = "$maj.$min.$pat"
  Set-Content -Encoding UTF8 -Path $VersionFile -Value $new
  return $new
}

function WrapUp-Clean {
  $bump = Read-Host "Version bump? (patch|minor|major|skip) [patch]"
  if (-not $bump) { $bump = "patch" }
  $newVer = $null
  if ($bump -ne "skip") {
    $newVer = Bump-Version -Kind $bump
    Write-Host "Version -> $newVer"
    Push-Location $Repo
    try {
      git add $VersionFile
      git commit -m "chore(release): bump to $newVer"
      $ans = Read-Host "Tag v$newVer and push? (y/N)"
      if ($ans -match "^[yY]") {
        git tag -a "v$newVer" -m "AutoFire $newVer"
        git push origin $Main --tags
      }
    } finally { Pop-Location }
  }

  Build-Project

  if ($Updater) {
    $dist = Join-Path $Repo "dist"
    if (Test-Path $dist) {
      $zips = Get-ChildItem $dist -Filter *.zip | Sort-Object LastWriteTime -Descending
      if ($zips) {
        $dst = Join-Path $Updater $zips[0].Name
        Copy-Item $zips[0].FullName $dst -Force
        Write-Host "Copied build -> $dst"
      }
    }
  }

  & (Join-Path $PSScriptRoot "tools\Backup_Snapshot.ps1") -Repo $Repo -OutName "postwrap"
  & (Join-Path $PSScriptRoot "tools\Safe_Clean.ps1") -Repo $Repo
  $do = Read-Host "Run cleanup now? (y/N)"
  if ($do -match "^[yY]") {
    & (Join-Path $PSScriptRoot "tools\Safe_Clean.ps1") -Repo $Repo -Execute
  }
  Pause-Enter
}

function CILab {
  $map = @{
    "1" = @{ name="GitHub Actions"; path=".github/workflows/ci.yml"; prompt="ci_prompts\github_actions.prompt.txt" }
    "2" = @{ name="GitLab CI";      path=".gitlab-ci.yml";         prompt="ci_prompts\gitlab_ci.prompt.txt" }
    "3" = @{ name="CircleCI";       path=".circleci/config.yml";   prompt="ci_prompts\circleci.prompt.txt" }
    "4" = @{ name="Travis CI";      path=".travis.yml";            prompt="ci_prompts\travis.prompt.txt" }
    "5" = @{ name="Azure";          path="azure-pipelines.yml";    prompt="ci_prompts\azure_pipelines.prompt.txt" }
    "6" = @{ name="Codex CI";       path="codex-ci.yml";           prompt="ci_prompts\codex_ci.prompt.txt" }
    "7" = @{ name="Gemini CI";      path="gemini-ci.yml";          prompt="ci_prompts\gemini_ci.prompt.txt" }
    "8" = @{ name="Custom";         path="custom-ci.yml";          prompt="ci_prompts\custom.prompt.txt" }
  }
  Write-Host ""
  Write-Host "== CI Lab ==" -ForegroundColor Cyan
  $map.GetEnumerator() | ForEach-Object { Write-Host ("[{0}] {1}" -f $_.Key, $_.Value.name) }
  $sel = Read-Host "Pick one"
  if (-not $map.ContainsKey($sel)) { return }
  $ci = $map[$sel]
  $promptFile = Join-Path (Split-Path -Parent $PSCommandPath) $ci.prompt
  $target = Join-Path $Repo $ci.path

  $text = if (Test-Path $promptFile) { Get-Content -Raw $promptFile } else { "(Prompt file missing.)" }
  $tmp = Join-Path $env:TEMP "CI_PROMPT.txt"
  $text | Set-Content -Encoding UTF8 $tmp
  Start-Process notepad.exe $tmp

  $ans = Read-Host "Create/open target file now? ($($ci.path)) (y/N)"
  if ($ans -match "^[yY]") {
    $parent = Split-Path -Parent $target
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    if (-not (Test-Path $target)) { "# Paste the generated YAML here" | Set-Content -Encoding UTF8 $target }
    Start-Process notepad.exe $target
  }
  Pause-Enter
}

function Quick-Links {
  $links = $cfg.quickLinks
  if (-not $links) { Write-Host "No quick links set."; Pause-Enter; return }
  $i=1
  foreach ($l in $links) {
    Write-Host ("[{0}] {1} -> {2}" -f $i, $l.name, $l.path)
    $i++
  }
  $sel = Read-Host "Pick a number (Enter to cancel)"
  if (-not $sel) { return }
  $n = [int]$sel
  if ($n -ge 1 -and $n -le $links.Count) {
    Start-Process explorer.exe $links[$n-1].path
  }
}

do {
  Write-Host ""
  Write-Host "[1] Start My Day"
  Write-Host "[2] Build Project"
  Write-Host "[3] Run Tests"
  Write-Host "[4] Create Feature Branch"
  Write-Host "[5] Commit Helper"
  Write-Host "[6] Wrap Up & Clean"
  Write-Host "[7] CI Lab"
  Write-Host "[8] Quick Links"
  Write-Host "[0] Exit"
  $choice = Read-Host "Select an option"
  switch ($choice) {
    "1" { Start-Day }
    "2" { Build-Project }
    "3" { Run-Tests }
    "4" { Create-Branch }
    "5" { Commit-Helper }
    "6" { WrapUp-Clean }
    "7" { CILab }
    "8" { Quick-Links }
    "0" { break }
    default { Write-Host "Unknown option." }
  }
} while ($true)

Write-Host "Goodbye!"
