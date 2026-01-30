#!/bin/bash
#
# 停止网站监控定期任务
#

if [ -f logs/monitor.pid ]; then
    PID=$(cat logs/monitor.pid)

    if ps -p $PID > /dev/null 2>&1; then
        echo "正在停止监控服务 (PID: $PID)..."
        kill $PID
        rm logs/monitor.pid
        echo "✅ 监控服务已停止"
    else
        echo "❌ 进程不存在 (PID: $PID)"
        rm logs/monitor.pid
    fi
else
    echo "❌ 未找到监控服务进程文件"
fi

# 清理可能残留的进程
pkill -f "periodic_monitor.py"
