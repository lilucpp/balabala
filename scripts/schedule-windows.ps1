#!/usr/bin/env pwsh
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    为balabala创建Windows定时任务

.DESCRIPTION
    在Windows任务计划程序中创建一个每天运行的定时任务
#>

$taskName = "balabala-daily-report"
$taskDescription = "balabala每日报告生成器 - 每天自动发送早安报告"

# 获取项目路径
$projectPath = (Get-Location).Path
$pythonPath = (Get-Command python).Source
$mainScript = Join-Path $projectPath "main.py"

Write-Host "正在为balabala创建定时任务..." -ForegroundColor Green
Write-Host "项目路径: $projectPath" -ForegroundColor Cyan
Write-Host "Python路径: $pythonPath" -ForegroundColor Cyan

# 创建触发器（每天7:00）
$trigger = New-ScheduledTaskTrigger -Daily -At "07:00"

# 创建操作
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $mainScript `
    -WorkingDirectory $projectPath

# 创建设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# 创建任务对象
$task = New-ScheduledTask `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $taskDescription

# 注册任务
# 尝试删除已存在的任务
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "删除已存在的任务..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 注册新任务
Register-ScheduledTask `
    -TaskName $taskName `
    -InputObject $task `
    -Force

Write-Host "`n✅ 定时任务创建成功！" -ForegroundColor Green
Write-Host "任务名称: $taskName" -ForegroundColor Cyan
Write-Host "运行时间: 每天 07:00" -ForegroundColor Cyan
Write-Host "`n你可以通过以下命令管理任务：" -ForegroundColor Yellow
Write-Host "  查看任务: Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  立即运行: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  停止任务: Stop-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host "  删除任务: Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
