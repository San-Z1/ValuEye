@echo off
REM ValuEye - 手动运行，双击即可查看报告
chcp 65001 >nul
cd /d "%~dp0"
python main.py
echo.
pause
