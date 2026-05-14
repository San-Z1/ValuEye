#!/bin/bash
# 大学生理财监控脚本 - Linux/Mac启动脚本
# 作者：SanZ1
# 创建时间：2026-05-14

echo "启动大学生理财监控系统..."
echo "开始时间: $(date)"

# 进入脚本所在目录
cd "$(dirname "$0")"

# 运行 v2 主程序
python3 finance_monitor/main.py

echo ""
echo "完成时间: $(date)"
