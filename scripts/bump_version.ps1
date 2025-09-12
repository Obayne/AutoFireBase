param(
  [ValidateSet('major','minor','patch')]
  [string]$Part = 'patch',
  [string]$Message = ''
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path 'VERSION.txt')) { Write-Error 'VERSION.txt not found'; exit 1 }
$ver = (Get-Content VERSION.txt -Raw).Trim()
if (-not ($ver -match '^(\d+)\.(\d+)\.(\d+)$')) { Write-Error "Invalid version '$ver' in VERSION.txt"; exit 1 }
$maj = [int]$Matches[1]; $min = [int]$Matches[2]; $pat = [int]$Matches[3]
switch ($Part) {
  'major' { $maj++; $min=0; $pat=0 }
  'minor' { $min++; $pat=0 }
  'patch' { $pat++ }
}
$new = "$maj.$min.$pat"
$tag = "v$new"

Write-Host "Bumping version: $ver -> $new"
Set-Content VERSION.txt $new

# Update CHANGELOG.md (simple prepend into Unreleased section)
if (-not (Test-Path 'CHANGELOG.md')) {
  Set-Content CHANGELOG.md "# Changelog`n`nAll notable changes to this project will be documented in this file.`n`n## [Unreleased]`n`n## [$new] - $(Get-Date -Format 'yyyy-MM-dd')`n- $Message`n"
} else {
  $ch = Get-Content CHANGELOG.md -Raw
  if ($ch -notmatch '## \[Unreleased\]') { $ch = "# Changelog`n`n## [Unreleased]`n`n" + $ch }
  $date = Get-Date -Format 'yyyy-MM-dd'
  $insert = "`n## [$new] - $date`n- $Message`n"
  $ch = $ch -replace '(?s)(## \[Unreleased\].*?)(\r?\n## )', "$1$insert`n## "
  $escaped = [regex]::Escape($new)
  if ($ch -notmatch "\[${escaped}\]") { $ch += $insert }
  Set-Content CHANGELOG.md $ch
}

git add VERSION.txt CHANGELOG.md
git commit -m "chore(release): $new`n`n$Message"
git tag $tag
Write-Host "Created tag $tag. Push with: git push && git push origin $tag"

