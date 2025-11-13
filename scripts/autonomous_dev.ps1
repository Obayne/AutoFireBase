#!/usr/bin/env pwsh
<#
.SYNOPSIS
Fully autonomous development pipeline - implements features from task queue automatically

.DESCRIPTION
This script:
1. Reads tasks from tasks/ directory
2. Creates GitHub issues with agent:auto label
3. Waits for agent orchestrator to scaffold
4. Uses local AI (DeepSeek Coder) to implement
5. Runs tests automatically
6. Creates PR when ready
7. Only pauses for human testing/approval

.PARAMETER TaskFile
Specific task file to process (default: processes all)

.PARAMETER SkipTests
Skip automated testing (not recommended)

.PARAMETER AutoMerge
Auto-merge PRs that pass all checks (requires approval)

.EXAMPLE
.\scripts\autonomous_dev.ps1
Process all tasks autonomously

.EXAMPLE
.\scripts\autonomous_dev.ps1 -TaskFile "task-db-connection-manager.md"
Process specific task
#>

param(
    [string]$TaskFile = "",
    [switch]$SkipTests = $false,
    [switch]$AutoMerge = $false,
    [int]$MaxIterations = 10,
    [int]$PauseBetweenTasks = 30
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent

Write-Host "🤖 LV CAD Autonomous Development Pipeline" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check prerequisites
function Test-Prerequisites {
    Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow
    
    $missing = @()
    
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        $missing += "GitHub CLI (gh)"
    }
    
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        $missing += "Ollama"
    }
    
    if (-not (Get-Command pytest -ErrorAction SilentlyContinue)) {
        $missing += "pytest"
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "❌ Missing: $($missing -join ', ')" -ForegroundColor Red
        exit 1
    }
    
    # Check Ollama is running
    try {
        $ollamaCheck = curl.exe -s http://localhost:11434/api/tags 2>$null
        if (-not $ollamaCheck) {
            Write-Host "❌ Ollama is not running. Start with: ollama serve" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Cannot connect to Ollama" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ All prerequisites met" -ForegroundColor Green
}

# Get all task files
function Get-TaskFiles {
    $tasksDir = Join-Path $RepoRoot "tasks"
    if ($TaskFile) {
        $file = Join-Path $tasksDir $TaskFile
        if (Test-Path $file) {
            return @($file)
        } else {
            Write-Host "❌ Task file not found: $TaskFile" -ForegroundColor Red
            exit 1
        }
    }
    
    # Get all task files, prioritize by prefix
    $allTasks = Get-ChildItem $tasksDir -Filter "*.md" | Where-Object { $_.Name -notmatch "^pr/" }
    
    # Sort: task- first, then feat-
    $taskFiles = $allTasks | Sort-Object { 
        if ($_.Name.StartsWith("task-")) { 0 }
        elseif ($_.Name.StartsWith("feat-")) { 1 }
        else { 2 }
    }
    
    return $taskFiles
}

# Create GitHub issue from task
function New-TaskIssue {
    param([string]$TaskPath)
    
    $taskName = [System.IO.Path]::GetFileNameWithoutExtension($TaskPath)
    $content = Get-Content $TaskPath -Raw
    
    # Extract title from first line or use filename
    $title = if ($content -match "^#\s*(.+)") { 
        $matches[1] 
    } elseif ($content -match "Task:\s*(.+)") {
        $matches[1]
    } else { 
        $taskName -replace "-", " " 
    }
    
    # Determine labels based on filename
    $labels = @("agent:auto")
    if ($taskName -match "cad-core|cad_core") { $labels += "area:cad_core" }
    elseif ($taskName -match "backend") { $labels += "area:backend" }
    elseif ($taskName -match "frontend") { $labels += "area:frontend" }
    
    Write-Host "`n📝 Creating issue: $title" -ForegroundColor Cyan
    
    $labelArgs = $labels | ForEach-Object { "--label", $_ }
    
    # Check if issue already exists
    $existing = gh issue list --label "agent:auto" --search "$title" --json number,title --limit 1 | ConvertFrom-Json
    if ($existing -and $existing.Count -gt 0) {
        Write-Host "⏭️  Issue already exists: #$($existing[0].number)" -ForegroundColor Yellow
        return $existing[0].number
    }
    
    $issue = gh issue create --title $title --body-file $TaskPath @labelArgs --json number | ConvertFrom-Json
    Write-Host "✅ Created issue #$($issue.number)" -ForegroundColor Green
    return $issue.number
}

# Wait for agent orchestrator to create branch
function Wait-ForAgentScaffold {
    param([int]$IssueNumber, [int]$TimeoutSeconds = 300)
    
    Write-Host "`n⏳ Waiting for agent orchestrator to scaffold..." -ForegroundColor Yellow
    
    $start = Get-Date
    while ((Get-Date) -lt $start.AddSeconds($TimeoutSeconds)) {
        Start-Sleep -Seconds 10
        
        # Check for new branch related to this issue
        git fetch origin --quiet 2>$null
        $branches = git branch -r | Where-Object { $_ -match "feat/agent-" }
        
        if ($branches) {
            $latestBranch = $branches | Select-Object -First 1 | ForEach-Object { $_.Trim() -replace "origin/", "" }
            Write-Host "✅ Found scaffold branch: $latestBranch" -ForegroundColor Green
            return $latestBranch
        }
        
        Write-Host "." -NoNewline
    }
    
    Write-Host "`n⚠️  Timeout waiting for scaffold. Creating branch manually..." -ForegroundColor Yellow
    return $null
}

# Use AI to implement the task
function Invoke-AIImplementation {
    param(
        [string]$Branch,
        [string]$TaskPath
    )
    
    Write-Host "`n🤖 Using DeepSeek Coder to implement task..." -ForegroundColor Cyan
    
    git checkout $Branch 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout -b $Branch
    }
    
    $taskContent = Get-Content $TaskPath -Raw
    
    # Create AI prompt
    $prompt = @"
You are implementing a task for LV CAD (Low Volt Layer Vision), a Python CAD application.

TASK:
$taskContent

CONSTRAINTS:
- Keep changes under 300 lines total
- Follow Black formatting (line length 100)
- Add pytest tests for all new code
- No Qt imports in backend/ or cad_core/
- Use existing patterns from the codebase
- Update existing tests if behavior changes

ARCHITECTURE:
- frontend/ = Qt UI, views, input handling
- backend/ = non-UI logic, persistence, services
- cad_core/ = pure geometry algorithms
- tests/ = pytest suite

Respond with ONLY the implementation plan in JSON format:
{
  "files_to_create": ["path/to/file.py"],
  "files_to_modify": ["path/to/existing.py"],
  "tests_to_add": ["tests/path/test_feature.py"],
  "implementation_steps": ["step 1", "step 2"]
}
"@

    # Call Ollama API for plan
    $planResponse = curl.exe -s http://localhost:11434/api/generate -d @"
{
  "model": "deepseek-coder:latest",
  "prompt": "$($prompt -replace '"', '\"' -replace "`n", '\n')",
  "stream": false,
  "options": {
    "temperature": 0.3
  }
}
"@ | ConvertFrom-Json
    
    $aiPlan = $planResponse.response
    Write-Host "`n📋 AI Implementation Plan:" -ForegroundColor Cyan
    Write-Host $aiPlan
    
    # TODO: Parse plan and execute file changes
    # For now, create a marker file to indicate AI is working
    $markerFile = Join-Path $RepoRoot ".ai_implementation_pending"
    $aiPlan | Out-File $markerFile
    
    Write-Host "`n⚠️  AI implementation requires manual code generation." -ForegroundColor Yellow
    Write-Host "See .ai_implementation_pending for plan" -ForegroundColor Yellow
    
    return $false  # Not yet fully implemented
}

# Run automated tests
function Invoke-AutomatedTests {
    Write-Host "`n🧪 Running automated tests..." -ForegroundColor Cyan
    
    Push-Location $RepoRoot
    try {
        # Format check
        Write-Host "  → Checking formatting..." -ForegroundColor Gray
        black --check . --line-length 100 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ⚠️  Auto-formatting..." -ForegroundColor Yellow
            black . --line-length 100
        }
        
        # Lint
        Write-Host "  → Running Ruff..." -ForegroundColor Gray
        ruff check . --fix 2>$null
        
        # Pytest
        Write-Host "  → Running pytest..." -ForegroundColor Gray
        pytest -q --tb=short
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ All tests passed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Tests failed" -ForegroundColor Red
            return $false
        }
    } finally {
        Pop-Location
    }
}

# Create PR
function New-AutomatedPR {
    param([string]$Branch, [string]$TaskPath)
    
    Write-Host "`n📤 Creating pull request..." -ForegroundColor Cyan
    
    $taskName = [System.IO.Path]::GetFileNameWithoutExtension($TaskPath)
    $title = "feat: $($taskName -replace '-', ' ')"
    
    $body = @"
## Automated Implementation

This PR was generated by the autonomous development pipeline.

### Task
See: ``tasks/$([System.IO.Path]::GetFileName($TaskPath))``

### Changes
- Implemented as per task specification
- Added tests for new functionality
- Followed Black/Ruff formatting

### Testing Required
🧑‍💻 **Human testing needed:**
1. Review code changes
2. Run manual smoke tests
3. Verify functionality

---
*Generated by autonomous_dev.ps1*

Generated with [Continue](https://continue.dev)

Co-Authored-By: Continue <noreply@continue.dev>
"@

    # Check if PR already exists
    $existing = gh pr list --head $Branch --json number | ConvertFrom-Json
    if ($existing -and $existing.Count -gt 0) {
        Write-Host "⏭️  PR already exists: #$($existing[0].number)" -ForegroundColor Yellow
        return $existing[0].number
    }
    
    git add -A
    git commit -m "$title`n`nGenerated with [Continue](https://continue.dev)`n`nCo-Authored-By: Continue <noreply@continue.dev>"
    git push -u origin $Branch
    
    $pr = gh pr create --title $title --body $body --draft --json number | ConvertFrom-Json
    Write-Host "✅ Created PR #$($pr.number)" -ForegroundColor Green
    
    return $pr.number
}

# Main pipeline
function Start-AutonomousPipeline {
    Test-Prerequisites
    
    $tasks = Get-TaskFiles
    Write-Host "`n📋 Found $($tasks.Count) tasks to process" -ForegroundColor Cyan
    
    $iteration = 0
    foreach ($task in $tasks) {
        if ($iteration -ge $MaxIterations) {
            Write-Host "`n⚠️  Reached max iterations ($MaxIterations)" -ForegroundColor Yellow
            break
        }
        
        Write-Host "`n" + ("="*80) -ForegroundColor DarkGray
        Write-Host "Processing: $($task.Name)" -ForegroundColor Cyan
        Write-Host ("="*80) -ForegroundColor DarkGray
        
        try {
            # Step 1: Create issue
            $issueNum = New-TaskIssue -TaskPath $task.FullName
            
            # Step 2: Wait for or create scaffold
            $branch = Wait-ForAgentScaffold -IssueNumber $issueNum -TimeoutSeconds 120
            if (-not $branch) {
                $branch = "feat/auto-$($task.BaseName)"
                git checkout -b $branch 2>$null
            }
            
            # Step 3: AI implementation
            $implemented = Invoke-AIImplementation -Branch $branch -TaskPath $task.FullName
            
            if (-not $implemented) {
                Write-Host "`n⏸️  PAUSED: Manual implementation needed" -ForegroundColor Yellow
                Write-Host "Branch: $branch" -ForegroundColor Cyan
                Write-Host "Press Enter when ready to continue, or Ctrl+C to stop..." -ForegroundColor Yellow
                Read-Host
            }
            
            # Step 4: Run tests
            if (-not $SkipTests) {
                $testsPassed = Invoke-AutomatedTests
                if (-not $testsPassed) {
                    Write-Host "`n⏸️  PAUSED: Tests failed - manual fix needed" -ForegroundColor Yellow
                    Write-Host "Press Enter when fixed, or Ctrl+C to stop..." -ForegroundColor Yellow
                    Read-Host
                }
            }
            
            # Step 5: Create PR
            $prNum = New-AutomatedPR -Branch $branch -TaskPath $task.FullName
            
            Write-Host "`n✅ Task complete - PR #$prNum ready for review" -ForegroundColor Green
            
            # Pause between tasks
            if ($PauseBetweenTasks -gt 0 -and $iteration -lt $tasks.Count - 1) {
                Write-Host "`n⏳ Waiting $PauseBetweenTasks seconds before next task..." -ForegroundColor Gray
                Start-Sleep -Seconds $PauseBetweenTasks
            }
            
        } catch {
            Write-Host "`n❌ Error processing task: $_" -ForegroundColor Red
            Write-Host "Continuing to next task..." -ForegroundColor Yellow
        }
        
        $iteration++
    }
    
    Write-Host "`n🎉 Autonomous pipeline complete!" -ForegroundColor Green
    Write-Host "Processed $iteration tasks" -ForegroundColor Cyan
}

# Run pipeline
Start-AutonomousPipeline
