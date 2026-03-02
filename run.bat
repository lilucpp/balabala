@echo off
echo ===================================
echo    balabala 每日报告生成器
echo ===================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查配置文件
if not exist "config.yaml" (
    echo [提示] 配置文件不存在，正在从模板创建...
    copy config.yaml.example config.yaml
    echo [提示] 请编辑 config.yaml 填写你的配置信息
    notepad config.yaml
    echo.
    echo 配置完成后请重新运行此脚本
    pause
    exit /b 0
)

echo 正在运行 balabala...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行失败，请检查日志: logs\balabala.log
    pause
    exit /b 1
) else (
    echo.
    echo [成功] 程序运行完成！
    echo 日志文件: logs\balabala.log
    timeout /t 3 >nul
)
