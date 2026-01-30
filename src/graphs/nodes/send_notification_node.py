import json
import logging
import os
from datetime import datetime
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import SendNotificationInput, SendNotificationOutput, NotificationInfo, ChangeDetectionResult, WebsiteInfo


logger = logging.getLogger(__name__)


def send_notification_node(
    state: SendNotificationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendNotificationOutput:
    """
    title: 记录通知到文件
    desc: 检测到网站内容更新后，将通知信息保存到文件中
    integrations:
    """
    ctx = runtime.context

    change_result = state.change_result
    website = state.website

    logger.info(f"开始处理通知: {website.name}")

    # 生成通知时间
    notification_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 定义通知文件路径
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "")
    notification_file = os.path.join(workspace_path, "assets", "website_notifications.json")

    # 确保目录存在
    os.makedirs(os.path.dirname(notification_file), exist_ok=True)

    # 如果没有变化，返回空通知
    if not change_result.has_change:
        notification = NotificationInfo(
            website_name=website.name,
            has_change=False,
            change_details="无更新",
            notification_time=notification_time
        )
        return SendNotificationOutput(notification=notification, is_sent=False)

    # 生成变化详情
    change_details = f"网站：{website.name}\n"
    change_details += f"URL：{website.url}\n"
    change_details += f"检测时间：{notification_time}\n"
    change_details += f"新增内容数量：{len(change_result.new_items)}\n"

    if change_result.new_items:
        change_details += "\n新增内容：\n"
        for idx, item in enumerate(change_result.new_items, 1):
            change_details += f"{idx}. {item}\n"

    # 构建通知信息
    notification = NotificationInfo(
        website_name=website.name,
        has_change=True,
        change_details=change_details,
        notification_time=notification_time
    )

    # 读取现有通知记录
    notifications = []
    if os.path.exists(notification_file):
        try:
            with open(notification_file, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
        except Exception as e:
            logger.error(f"读取通知文件失败: {e}")
            notifications = []

    # 添加新通知（只保留最近100条）
    notification_dict = {
        "website_name": notification.website_name,
        "has_change": notification.has_change,
        "change_details": notification.change_details,
        "notification_time": notification.notification_time
    }
    notifications.insert(0, notification_dict)
    if len(notifications) > 100:
        notifications = notifications[:100]

    # 保存通知到文件
    try:
        with open(notification_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
        logger.info(f"通知已保存到文件: {notification_file}")
        is_sent = True
    except Exception as e:
        logger.error(f"保存通知文件失败: {e}")
        is_sent = False

    # 输出到日志
    logger.info(f"检测到网站更新！\n{change_details}")

    # 注意：当前版本将通知保存到本地文件
    # 如需发送邮件或飞书通知，请配置相应的集成服务
    # 邮件/飞书集成的示例代码见下方注释：
    #
    # # 邮件通知示例：
    # try:
    #     from integrations.email import send_email
    #     send_email(
    #         to="your_email@example.com",
    #         subject=f"网站更新通知: {website.name}",
    #         body=change_details
    #     )
    #     logger.info("邮件通知发送成功")
    # except Exception as e:
    #     logger.error(f"邮件通知发送失败: {e}")
    #
    # # 飞书通知示例：
    # try:
    #     from integrations.feishu import send_feishu_message
    #     send_feishu_message(
    #         webhook_url="your_webhook_url",
    #         message=change_details
    #     )
    #     logger.info("飞书通知发送成功")
    # except Exception as e:
    #     logger.error(f"飞书通知发送失败: {e}")

    logger.info(f"通知处理完成: {website.name}")

    return SendNotificationOutput(notification=notification, is_sent=is_sent)
