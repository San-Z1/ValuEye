#!/bin/bash
# 大学生理财监控脚本 - Linux/Mac启动脚本
# 作者：Claude Code
# 创建时间：2026-05-14

echo "🚀 启动大学生理财监控系统..."
echo "⏰ 开始时间: $(date)"

# 进入脚本目录
cd "$(dirname "$0")"

# 运行Python脚本
python3 market_monitor.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 理财监控完成！"
    echo "⏰ 结束时间: $(date)"
else
    echo "❌ 程序运行出错，请检查Python安装"
    exit 1
fi