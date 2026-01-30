#!/bin/bash
#
# 实时监控动态
# 持续显示监控系统的运行状态和最新动态
#

clear

echo "======================================"
echo "网站监控系统 - 实时监控"
echo "======================================"
echo ""
echo "显示内容："
echo "  - 监控进程状态"
echo "  - 实时日志输出"
echo "  - 最新监控结果"
echo ""
echo "按 Ctrl+C 退出"
echo "======================================"
echo ""
echo ""

while true; do
    # 清屏并显示头部（每隔5次刷新一次，避免闪烁）
    clear
    echo "======================================"
    echo "网站监控系统 - 实时监控"
    echo "======================================"
    echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 检查进程状态
    echo "【进程状态】"
    if [ -f logs/monitor.pid ]; then
        PID=$(cat logs/monitor.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ 监控服务: 运行中 (PID: $PID)"
            
            # 显示进程信息
            PS_INFO=$(ps -p $PID -o etime=,pcpu=,pmem=,cmd= 2>/dev/null)
            if [ -n "$PS_INFO" ]; then
                echo "   运行时长: $(echo $PS_INFO | awk '{print $1}')"
                echo "   CPU使用率: $(echo $PS_INFO | awk '{print $2}')%"
                echo "   内存使用: $(echo $PS_INFO | awk '{print $3}')%"
            fi
        else
            echo "❌ 监控服务: 已停止"
            echo "   提示: 运行 'bash scripts/start_monitor.sh' 启动服务"
        fi
    else
        echo "❌ 监控服务: 未启动"
        echo "   提示: 运行 'bash scripts/start_monitor.sh' 启动服务"
    fi
    
    echo ""
    
    # 显示最新监控摘要
    echo "【最新监控摘要】"
    if [ -f logs/monitor.out ]; then
        # 提取最新的监控结果
        LAST_RUN=$(tail -n 200 logs/monitor.out | grep "监控完成:" -A 5 | head -6)
        if [ -n "$LAST_RUN" ]; then
            echo "$LAST_RUN"
        else
            echo "   暂无监控记录"
        fi
    else
        echo "   暂无监控记录"
    fi
    
    echo ""
    
    # 显示下次运行时间
    echo "【下次运行】"
    NEXT_RUN=$(tail -n 100 logs/monitor.out | grep "下次运行时间:" | tail -1)
    if [ -n "$NEXT_RUN" ]; then
        echo "   $NEXT_RUN"
    else
        echo "   未知"
    fi
    
    echo ""
    
    # 显示最新通知数量
    echo "【通知统计】"
    if [ -f assets/website_notifications.json ]; then
        NOTIFICATION_COUNT=$(grep -c '"has_change": true' assets/website_notifications.json 2>/dev/null || echo "0")
        echo "   总通知数: $NOTIFICATION_COUNT 条"
        
        # 显示最近一次通知
        LAST_NOTIF=$(head -10 assets/website_notifications.json | grep -A 1 "website_name" | tail -1 2>/dev/null)
        if [ -n "$LAST_NOTIF" ]; then
            echo "   最新: $LAST_NOTIF"
        fi
    else
        echo "   总通知数: 0 条"
    fi
    
    echo ""
    echo "======================================"
    echo "按 Ctrl+C 退出 | 每3秒自动刷新"
    echo "======================================"
    
    # 等待3秒后刷新
    sleep 3
done
