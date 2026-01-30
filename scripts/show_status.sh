#!/bin/bash
#
# 查看监控实时动态
# 显示最新的监控结果和运行状态
#

clear

echo "======================================"
echo "网站监控系统 - 实时动态"
echo "======================================"
echo ""

# 检查进程是否运行
if [ -f logs/monitor.pid ]; then
    PID=$(cat logs/monitor.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 监控服务状态: 运行中 (PID: $PID)"
    else
        echo "❌ 监控服务状态: 已停止"
    fi
else
    echo "❌ 监控服务状态: 未启动"
fi

echo ""

# 显示最后一次监控结果
echo "--------------------------------------"
echo "最新监控结果"
echo "--------------------------------------"
echo ""

if [ -f logs/monitor.out ]; then
    # 提取最新的监控结果
    tail -n 100 logs/monitor.out | grep -A 10 "监控完成:"
else
    echo "暂无监控记录"
fi

echo ""

# 显示最新通知
echo "--------------------------------------"
echo "最新通知（最近3条）"
echo "--------------------------------------"
echo ""

if [ -f assets/website_notifications.json ]; then
    head -50 assets/website_notifications.json | jq -r '.[] | "网站: \(.website_name)\n时间: \(.notification_time)\n更新数: \(.new_items | length)\n"' 2>/dev/null || \
    grep -A 3 "website_name" assets/website_notifications.json | head -20
else
    echo "暂无通知记录"
fi

echo ""
echo "======================================"
echo "按 Ctrl+C 退出，或等待 10 秒后刷新..."
echo "======================================"
