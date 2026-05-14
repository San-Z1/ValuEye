@echo off
REM 大学生理财监控脚本 - Windows启动批处理
REM 作者：SanZ1
REM 创建时间：2026-05-14

echo 🚀 启动大学生理财监控系统...
echo ⏰ 开始时间: %date% %time%

REM 设置Python环境（如果需要使用虚拟环境）
REM call C:\Python39\Scripts\activate.bat

REM 进入脚本目录
cd /d "C:\Users\Xujusheng\Desktop\新建文件夹 (2)"

REM 运行Python脚本
python market_monitor.py

REM 检查Python是否安装
if errorlevel 1 (
    echo ❌ Python未安装或未添加到系统环境变量
    echo 💡 请安装Python并添加到环境变量，或修改此脚本的Python路径
    pause
    exit /b 1
)

echo.
echo ✅ 理财监控完成！
echo ⏰ 结束时间: %date% %time%

REM 如果从任务计划程序运行，可以不暂停
REM 如果是手动运行，取消下面这行的注释
REM pause