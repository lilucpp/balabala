#!/usr/bin/env pwsh
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Create Windows scheduled task for balabala

.DESCRIPTION
    Create a daily scheduled task in Windows Task Scheduler
#>

$taskName = "balabala-daily-report"
$taskDescription = "balabala Daily Report Generator - Automatically send morning reports"

# Get project path
$projectPath = (Get-Location).Path
$pythonPath = (Get-Command python).Source
$mainScript = Join-Path $projectPath "main.py"

Write-Host "Creating scheduled task for balabala..." -ForegroundColor Green
Write-Host "Project path: $projectPath" -ForegroundColor Cyan
Write-Host "Python path: $pythonPath" -ForegroundColor Cyan

# Create trigger (daily at 7:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At "07:00"

# Create action
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $mainScript `
    -WorkingDirectory $projectPath

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Create task object
$task = New-ScheduledTask `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $taskDescription

# Register task
# Try to delete existing task first
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Deleting existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Register new task
Register-ScheduledTask `
    -TaskName $taskName `
    -InputObject $task `
    -Force

Write-Host "`n[OK] Scheduled task created successfully!" -ForegroundColor Green
Write-Host "Task name: $taskName" -ForegroundColor Cyan
Write-Host "Run time: Daily at 07:00" -ForegroundColor Cyan
Write-Host "`nYou can manage the task with these commands:" -ForegroundColor Yellow
Write-Host "  View task: Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  Run now: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  Stop task: Stop-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  Delete task: Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
