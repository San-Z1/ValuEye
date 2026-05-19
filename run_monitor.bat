@echo off
REM 大学生理财监控脚本 - Windows启动批处理
REM 作者：SanZ1
REM 创建时间：2026-05-14

echo 启动大学生理财监控系统...
echo 开始时间: %date% %time%

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 运行主程序
python -m finance_monitor.main
if errorlevel 1 (
    echo.
    echo 运行失败，请检查：
    echo   1. 是否已安装 Python 3.8+
    echo   2. 是否已安装依赖：pip install -r finance_monitor\requirements.txt
    echo.
)

echo.
echo 完成时间: %date% %time%
pause
