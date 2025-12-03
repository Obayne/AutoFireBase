#!/usr/bin/env pwsh
<#
.SYNOPSIS
Full autonomous development - zero human intervention except testing approval

.DESCRIPTION
Complete automation pipeline:
1. Reads task queue from tasks/
2. Uses AI to implement each task
3. Runs automated tests
4. Creates PR with draft status
5. Pauses only for human testing approval
6. Auto-merges when approved

.PARAMETER ContinuousMode
Run continuously, processing new tasks as they appear

.PARAMETER ApprovalRequired
Require manual approval before merging (default: true)

.EXAMPLE
.\scripts\full_auto.ps1
Run once through all tasks

.EXAMPLE
.\scripts\full_auto.ps1 -ContinuousMode
Run continuously as daemon
#>

param(
    [switch]$ContinuousMode = $false,
    [switch]$ApprovalRequired = $true,
    [int]$CheckIntervalSeconds = 300
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🤖 LV CAD FULL AUTONOMOUS DEVELOPMENT                   ║
║   Powered by DeepSeek Coder + Ollama                      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Ensure we're in repo root
Set-Location $RepoRoot

function Test-Environment {
    Write-Host "`n📋 Environment Check" -ForegroundColor Yellow
    
    $checks = @{
        "Python 3.11+" = { python --version 2>&1 | Select-String "Python 3\.1[1-9]" }
        "Ollama Running" = { 
            try { 
                $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
                return $response.StatusCode -eq 200
            } catch { 
                return $false 
            }
        }
        "DeepSeek Coder" = { ollama list 2>&1 | Select-String "deepseek-coder" }
        "GitHub CLI" = { gh --version }
        "Git" = { git --version }
        "pytest" = { pytest --version }
        "black" = { black --version }
        "ruff" = { ruff --version }
    }
    
    $allPassed = $true
    foreach ($check in $checks.GetEnumerator()) {
        Write-Host "  → $($check.Key)... " -NoNewline
        try {
            $result = & $check.Value
            if ($result) {
                Write-Host "✅" -ForegroundColor Green
            } else {
                Write-Host "❌" -ForegroundColor Red
                $allPassed = $false
            }
        } catch {
            Write-Host "❌" -ForegroundColor Red
            $allPassed = $false
        }
    }
    
    if (-not $allPassed) {
        Write-Host "`n❌ Environment checks failed. Please fix above issues." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`n✅ Environment ready" -ForegroundColor Green
}

function Get-NextTask {
    $tasksDir = Join-Path $RepoRoot "tasks"
    
    # Get all unprocessed tasks
    $tasks = Get-ChildItem $tasksDir -Filter "*.md" | Where-Object {
        $_.Name -notmatch "^pr/" -and
        -not (Test-Path (Join-Path $tasksDir "pr" $_.Name))
    } | Sort-Object {
        # Priority: task- > feat- > others
        if ($_.Name.StartsWith("task-")) { 0 }
        elseif ($_.Name.StartsWith("feat-")) { 1 }
        else { 2 }
    }
    
    return $tasks | Select-Object -First 1
}

function New-FeatureBranch {
    param([string]$TaskName)
    
    $branchName = "feat/auto-$TaskName" -replace "\.md$", ""
    
    Write-Host "`n🌿 Creating branch: $branchName" -ForegroundColor Cyan
    
    git fetch origin main
    git checkout main
    git pull origin main
    git checkout -b $branchName
    
    return $branchName
}

function Invoke-AIImplementation {
    param([string]$TaskFile)
    
    Write-Host "`n🤖 AI Implementation Phase" -ForegroundColor Cyan
    Write-Host "Task: $TaskFile" -ForegroundColor Gray
    
    $result = python "$PSScriptRoot/ai_coder.py" $TaskFile
    
    return $LASTEXITCODE -eq 0
}

function Test-Implementation {
    Write-Host "`n🧪 Testing Phase" -ForegroundColor Cyan
    
    # Format
    Write-Host "  → Formatting with Black..." -ForegroundColor Gray
    black . --line-length 100 --quiet
    
    # Lint
    Write-Host "  → Linting with Ruff..." -ForegroundColor Gray
    ruff check . --fix --quiet
    
    # Tests
    Write-Host "  → Running pytest..." -ForegroundColor Gray
    pytest -q --tb=short --durations=5
    
    $testsPassed = $LASTEXITCODE -eq 0
    
    if ($testsPassed) {
        Write-Host "`n✅ All checks passed" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Tests failed" -ForegroundColor Red
    }
    
    return $testsPassed
}

function New-ImplementationPR {
    param(
        [string]$Branch,
        [string]$TaskFile
    )
    
    Write-Host "`n📤 Creating Pull Request" -ForegroundColor Cyan
    
    $taskName = [System.IO.Path]::GetFileNameWithoutExtension($TaskFile)
    $title = "feat: $($taskName -replace '-', ' ')"
    
    $body = @"
## 🤖 Autonomous Implementation

**Task:** ``$TaskFile``

### 🔍 Implementation Details
- ✅ AI-generated code using DeepSeek Coder
- ✅ Automated tests added
- ✅ Black/Ruff formatting applied
- ✅ All checks passed

### 🧑‍💻 Human Review Required

**Please test manually:**
1. ✓ Code review for logic correctness
2. ✓ Run application and test feature
3. ✓ Verify no regressions

### 📊 Automation Metrics
- **Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- **Branch:** ``$Branch``
- **Model:** DeepSeek Coder (Ollama)

---

**Ready for review and testing** 🚀

Generated with [Continue](https://continue.dev)

Co-Authored-By: Continue <noreply@continue.dev>
"@

    # Commit changes
    git add -A
    git commit -m "$title`n`n$body"
    git push -u origin $Branch
    
    # Create PR
    $pr = gh pr create `
        --title $title `
        --body $body `
        --draft `
        --label "automated,needs-testing" `
        --json number,url | ConvertFrom-Json
    
    Write-Host "✅ Created PR #$($pr.number): $($pr.url)" -ForegroundColor Green
    
    return $pr
}

function Wait-ForApproval {
    param([int]$PrNumber)
    
    Write-Host "`n⏸️  APPROVAL REQUIRED" -ForegroundColor Yellow
    Write-Host "PR #$PrNumber is ready for human testing" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please:" -ForegroundColor White
    Write-Host "  1. Review the code changes" -ForegroundColor Gray
    Write-Host "  2. Test manually in the application" -ForegroundColor Gray
    Write-Host "  3. Approve the PR on GitHub" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Waiting for approval..." -ForegroundColor Yellow
    
    $approved = $false
    while (-not $approved) {
        Start-Sleep -Seconds 30
        
        $reviews = gh pr view $PrNumber --json reviews --jq '.reviews[] | select(.state=="APPROVED")' 2>$null
        if ($reviews) {
            $approved = $true
            Write-Host "`n✅ PR approved!" -ForegroundColor Green
        } else {
            Write-Host "." -NoNewline
        }
    }
}

function Merge-ApprovedPR {
    param([int]$PrNumber)
    
    Write-Host "`n🔀 Merging PR #$PrNumber..." -ForegroundColor Cyan
    
    # Mark as ready (remove draft)
    gh pr ready $PrNumber
    
    # Wait for CI
    Write-Host "  → Waiting for CI checks..." -ForegroundColor Gray
    $ciPassed = $false
    $attempts = 0
    while (-not $ciPassed -and $attempts -lt 60) {
        Start-Sleep -Seconds 10
        $checks = gh pr checks $PrNumber --json state --jq '.[] | select(.state!="SUCCESS")' 2>$null
        if (-not $checks) {
            $ciPassed = $true
        }
        $attempts++
    }
    
    if (-not $ciPassed) {
        Write-Host "  ⚠️  CI checks timed out or failed" -ForegroundColor Yellow
        return $false
    }
    
    # Merge
    gh pr merge $PrNumber --squash --delete-branch
    Write-Host "✅ Merged and cleaned up" -ForegroundColor Green
    
    # Move task to completed
    $taskFile = Get-ChildItem "tasks" -Filter "*.md" | Select-Object -First 1
    if ($taskFile) {
        $prDir = Join-Path "tasks" "pr"
        New-Item -ItemType Directory -Force -Path $prDir | Out-Null
        Move-Item $taskFile.FullName (Join-Path $prDir $taskFile.Name)
        Write-Host "  → Archived task to tasks/pr/" -ForegroundColor Gray
    }
    
    return $true
}

function Start-AutonomousLoop {
    $iteration = 0
    
    do {
        $iteration++
        Write-Host "`n$('='*80)" -ForegroundColor DarkGray
        Write-Host "🔄 Iteration $iteration" -ForegroundColor Cyan
        Write-Host "$('='*80)" -ForegroundColor DarkGray
        
        # Get next task
        $task = Get-NextTask
        if (-not $task) {
            Write-Host "`n✅ No more tasks in queue" -ForegroundColor Green
            if ($ContinuousMode) {
                Write-Host "Waiting for new tasks... (checking every $CheckIntervalSeconds seconds)" -ForegroundColor Yellow
                Start-Sleep -Seconds $CheckIntervalSeconds
                continue
            } else {
                break
            }
        }
        
        Write-Host "`n📋 Processing: $($task.Name)" -ForegroundColor Cyan
        
        try {
            # Create branch
            $branch = New-FeatureBranch -TaskName $task.BaseName
            
            # AI Implementation
            $implemented = Invoke-AIImplementation -TaskFile $task.FullName
            if (-not $implemented) {
                Write-Host "❌ AI implementation failed" -ForegroundColor Red
                git checkout main
                git branch -D $branch 2>$null
                continue
            }
            
            # Test
            $tested = Test-Implementation
            if (-not $tested) {
                Write-Host "❌ Tests failed" -ForegroundColor Red
                Write-Host "Branch preserved for manual debugging: $branch" -ForegroundColor Yellow
                git checkout main
                continue
            }
            
            # Create PR
            $pr = New-ImplementationPR -Branch $branch -TaskFile $task.Name
            
            # Wait for approval if required
            if ($ApprovalRequired) {
                Wait-ForApproval -PrNumber $pr.number
            }
            
            # Merge
            $merged = Merge-ApprovedPR -PrNumber $pr.number
            
            if ($merged) {
                Write-Host "`n🎉 Task complete: $($task.Name)" -ForegroundColor Green
                git checkout main
                git pull origin main
            }
            
        } catch {
            Write-Host "`n❌ Error: $_" -ForegroundColor Red
            Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
            git checkout main 2>$null
        }
        
        # Brief pause between tasks
        if ($ContinuousMode) {
            Start-Sleep -Seconds 10
        }
        
    } while ($ContinuousMode)
    
    Write-Host "`n" + ("="*80) -ForegroundColor DarkGray
    Write-Host "🏁 Autonomous development session complete" -ForegroundColor Green
    Write-Host "Iterations: $iteration" -ForegroundColor Cyan
    Write-Host ("="*80) -ForegroundColor DarkGray
}

# Main execution
Test-Environment
Start-AutonomousLoop
