#!/bin/bash
#
# 快速查看监控动态（适合预览区域）
# 显示当前状态和最新的监控结果
#

# 清屏
clear

# 添加颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}网站监控系统 - 实时动态${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 1. 进程状态
echo -e "${YELLOW}【进程状态】${NC}"
if [ -f logs/monitor.pid ]; then
    PID=$(cat logs/monitor.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "✅ 监控服务: ${GREEN}运行中${NC} (PID: $PID)"
        
        # 显示进程信息
        PS_INFO=$(ps -p $PID -o etime=,pcpu=,pmem= 2>/dev/null)
        if [ -n "$PS_INFO" ]; then
            echo "   运行时长: $(echo $PS_INFO | awk '{print $1}')"
            echo "   CPU使用率: $(echo $PS_INFO | awk '{print $2}')%"
            echo "   内存使用: $(echo $PS_INFO | awk '{print $3}')%"
        fi
    else
        echo -e "❌ 监控服务: ${RED}已停止${NC}"
        echo "   提示: 运行 'bash scripts/start_monitor.sh' 启动服务"
    fi
else
    echo -e "❌ 监控服务: ${RED}未启动${NC}"
    echo "   提示: 运行 'bash scripts/start_monitor.sh' 启动服务"
fi

echo ""

# 2. 最新监控摘要
echo -e "${YELLOW}【最新监控摘要】${NC}"
if [ -f logs/monitor.out ]; then
    # 提取最新的监控结果（最后10条）
    LAST_RUN=$(tail -n 100 logs/monitor.out | grep -E "监控完成|监控网站数|检测到变化" | tail -6)
    if [ -n "$LAST_RUN" ]; then
        echo "$LAST_RUN"
    else
        echo "   暂无监控记录"
    fi
else
    echo "   暂无监控记录"
fi

echo ""

# 3. 下次运行时间
echo -e "${YELLOW}【下次运行】${NC}"
NEXT_RUN=$(tail -n 100 logs/monitor.out | grep "下次运行时间:" | tail -1)
if [ -n "$NEXT_RUN" ]; then
    echo "   $NEXT_RUN"
else
    echo "   未知"
fi

echo ""

# 4. 通知统计
echo -e "${YELLOW}【通知统计】${NC}"
if [ -f assets/website_notifications.json ]; then
    # 计算通知数量
    NOTIFICATION_COUNT=$(grep -c '"has_change": true' assets/website_notifications.json 2>/dev/null || echo "0")
    echo -e "   总通知数: ${GREEN}$NOTIFICATION_COUNT${NC} 条"
    
    # 显示最近一次通知
    LAST_NOTIF=$(grep -A 3 '"has_change": true' assets/website_notifications.json | grep '"website_name"' | tail -1)
    if [ -n "$LAST_NOTIF" ]; then
        echo "   最新: $LAST_NOTIF"
    fi
    
    # 统计今天的通知数量
    TODAY=$(date '+%Y-%m-%d')
    TODAY_COUNT=$(grep "$TODAY" assets/website_notifications.json | grep "notification_time" | wc -l)
    echo "   今日新增: $TODAY_COUNT 条"
else
    echo "   总通知数: 0 条"
fi

echo ""

# 5. 最新通知详情（最近2条）
echo -e "${YELLOW}【最新通知】${NC}"
if [ -f assets/website_notifications.json ]; then
    # 提取最近2条有变化的通知
    echo ""
    grep -B 1 -A 8 '"has_change": true' assets/website_notifications.json 2>/dev/null | head -25
else
    echo "   暂无通知记录"
fi

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "运行 'bash scripts/monitor_live.sh' 获取实时动态"
echo -e "运行 'bash scripts/start_monitor.sh' 启动监控服务"
echo -e "运行 'bash scripts/stop_monitor.sh' 停止监控服务"
echo -e "${BLUE}======================================${NC}"
