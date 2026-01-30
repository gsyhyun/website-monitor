#!/bin/bash
#
# 启动网站监控定期任务（使用nohup后台运行）
# 每5分钟自动监控一次
#

# 邮件配置（QQ邮箱）
export QQ_SMTP_SERVER="smtp.qq.com"
export QQ_SMTP_PORT="465"
export QQ_EMAIL_ACCOUNT="gshyun@qq.com"
export QQ_EMAIL_AUTH_CODE="zlwdukmzjedycbbj"

echo "======================================"
echo "网站监控系统启动"
echo "======================================"
echo "监控间隔: 5分钟"
echo "邮箱地址: gshyun@qq.com"
echo "======================================"
echo ""

# 创建日志目录
mkdir -p logs

# 停止旧进程
if [ -f logs/monitor.pid ]; then
    OLD_PID=$(cat logs/monitor.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "停止旧进程 (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
    rm logs/monitor.pid
fi

# 清理残留进程
pkill -9 -f "periodic_monitor.py"

sleep 2

# 启动定期监控（使用nohup后台运行）
echo "正在启动监控服务..."
nohup python3 scripts/periodic_monitor.py \
  --email gshyun@qq.com \
  > logs/monitor.out 2>&1 &

# 获取进程ID
PID=$!
echo $PID > logs/monitor.pid

# 等待2秒确认进程启动
sleep 2

# 检查进程是否真的在运行
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 监控服务已成功启动！"
    echo ""
    echo "进程ID: $PID"
    echo "日志输出: logs/monitor.out"
    echo ""
    echo "查看日志: tail -f logs/monitor.out"
    echo "停止服务: bash scripts/stop_monitor.sh"
    echo ""
    echo "服务将在后台持续运行，每5分钟自动监控一次。"
else
    echo "❌ 监控服务启动失败！"
    echo "请检查日志: tail -n 20 logs/monitor.out"
    exit 1
fi
