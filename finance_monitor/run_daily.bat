@echo off
REM ValuEye - 每日定时运行脚本
REM 用法：在 Windows 任务计划程序中指向此文件

chcp 65001 >nul
cd /d "%~dp0"
python main.py >> run.log 2>&1
