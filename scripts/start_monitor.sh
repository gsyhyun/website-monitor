#!/bin/bash
#
# 启动网站监控定期任务（后台运行）
# 每5分钟自动监控一次
#

echo "======================================"
echo "网站监控系统启动"
echo "======================================"
echo "监控间隔: 5分钟"
echo "邮箱地址: gshyun@qq.com"
echo "日志文件: logs/monitoring.log"
echo "======================================"
echo ""

# 创建日志目录
mkdir -p logs

# 启动定期监控（后台运行）
echo "正在启动监控服务..."
nohup python3 scripts/periodic_monitor.py \
  --email gshyun@qq.com \
  >> logs/monitor.out 2>&1 &

# 获取进程ID
PID=$!
echo $PID > logs/monitor.pid

echo "✅ 监控服务已启动！"
echo ""
echo "进程ID: $PID"
echo "日志输出: logs/monitor.out"
echo "错误日志: logs/monitoring.log"
echo ""
echo "查看日志: tail -f logs/monitor.out"
echo "停止服务: bash scripts/stop_monitor.sh"
echo ""
echo "服务将在后台持续运行，每5分钟自动监控一次。"
