@echo off
REM 一键创建 Windows 定时任务（每天 08:30 运行）
REM 需要以管理员身份运行

echo ========================================
echo   大学生理财监控 - 定时任务配置
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set BAT_PATH=%SCRIPT_DIR%run_daily.bat

echo 将创建以下定时任务：
echo   任务名称: ValuEye
echo   触发时间: 每天 08:30
echo   执行脚本: %BAT_PATH%
echo.

schtasks /create /tn "ValuEye" /tr "\"%BAT_PATH%\"" /sc daily /st 08:30 /f

if errorlevel 1 (
    echo.
    echo 创建失败！请以管理员身份运行此脚本。
    echo 右键点击此文件 -^> 以管理员身份运行
    pause
    exit /b 1
)

echo.
echo 定时任务创建成功！
echo 每天早上 8:30 将自动运行市场监控。
echo.
echo 管理任务：
echo   查看: schtasks /query /tn "ValuEye"
echo   删除: schtasks /delete /tn "ValuEye" /f
echo.
pause
