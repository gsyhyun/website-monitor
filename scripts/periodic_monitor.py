#!/usr/bin/env python3
"""
网站监控定期执行脚本
每5分钟自动运行一次网站监控，检测网站更新并发送邮件通知

使用方法：
1. 配置邮箱地址（可选）
2. 运行脚本：python scripts/periodic_monitor.py
3. 按 Ctrl+C 停止脚本
"""

import sys
import time
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 导入工作流
from graphs.graph import main_graph

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitoring.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PeriodicMonitor:
    """定期监控器"""

    def __init__(self, interval_minutes: int = 5, email_address: str = None):
        """
        初始化定期监控器

        Args:
            interval_minutes: 监控间隔（分钟），默认5分钟
            email_address: 接收通知的邮箱地址（可选）
        """
        self.interval = interval_minutes * 60  # 转换为秒
        self.email_address = email_address
        self.running = False
        self.run_count = 0

        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        """处理中断信号"""
        logger.info(f"接收到信号 {signum}，准备停止监控...")
        self.running = False

    def _run_monitoring(self):
        """执行一次监控"""
        self.run_count += 1
        start_time = datetime.now()
        logger.info(f"=" * 60)
        logger.info(f"开始第 {self.run_count} 次监控 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 准备输入参数
            input_data = {}
            if self.email_address:
                input_data["email_address"] = self.email_address
                logger.info(f"邮件通知已启用，将发送到: {self.email_address}")
            else:
                logger.info("邮件通知未启用（未配置邮箱地址）")

            # 调用工作流
            result = main_graph.invoke(input_data)

            # 输出结果
            summary = result.get("monitoring_summary", {})
            notifications = result.get("all_notifications", [])

            logger.info(f"监控完成:")
            logger.info(f"  - 总网站数: {summary.get('total_websites', 0)}")
            logger.info(f"  - 已处理: {summary.get('processed', 0)}")
            logger.info(f"  - 有更新: {summary.get('websites_with_changes', 0)}")

            if notifications:
                logger.info(f"  - 通知详情:")
                for idx, notif in enumerate(notifications, 1):
                    logger.info(f"    {idx}. {notif.website_name}")

            # 记录运行时间
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"本次监控耗时: {elapsed:.2f}秒")

        except Exception as e:
            logger.error(f"监控执行失败: {e}", exc_info=True)

        logger.info(f"=" * 60)

    def start(self):
        """启动定期监控"""
        logger.info("=" * 60)
        logger.info("网站监控系统启动")
        logger.info(f"监控间隔: {self.interval // 60} 分钟")
        logger.info(f"邮箱地址: {self.email_address if self.email_address else '未配置'}")
        logger.info("按 Ctrl+C 停止监控")
        logger.info("=" * 60)

        self.running = True

        # 立即执行一次监控
        self._run_monitoring()

        # 定期执行
        while self.running:
            try:
                # 等待指定间隔
                next_run_time = datetime.now() + \
                    timedelta(seconds=self.interval)
                logger.info(f"下次运行时间: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")

                # 分段 sleep，支持中断
                sleep_interval = 10  # 每10秒检查一次中断信号
                for _ in range(self.interval // sleep_interval):
                    if not self.running:
                        break
                    time.sleep(sleep_interval)

                if self.running:
                    self._run_monitoring()

            except KeyboardInterrupt:
                logger.info("用户中断，停止监控")
                self.running = False
            except Exception as e:
                logger.error(f"监控循环异常: {e}", exc_info=True)
                if self.running:
                    logger.info(f"等待 {self.interval // 60} 分钟后重试...")
                    time.sleep(self.interval)

        logger.info("监控系统已停止")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="网站监控定期执行脚本")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="监控间隔（分钟），默认5分钟"
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="接收通知的邮箱地址"
    )

    args = parser.parse_args()

    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)

    # 启动监控
    monitor = PeriodicMonitor(
        interval_minutes=args.interval,
        email_address=args.email
    )
    monitor.start()


if __name__ == "__main__":
    main()
