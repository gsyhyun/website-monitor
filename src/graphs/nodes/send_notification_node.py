import logging
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
    title: 发送通知
    desc: 检测到网站内容更新后，生成并发送通知消息
    integrations: 
    """
    ctx = runtime.context
    
    change_result = state.change_result
    website = state.website
    
    logger.info(f"开始处理通知: {website.name}")
    
    # 生成通知时间
    notification_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
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
    
    # 输出到日志
    logger.info(f"检测到网站更新！\n{change_details}")
    
    # TODO: 这里可以添加邮件、飞书等集成服务的通知逻辑
    # 示例（需要配置集成服务）：
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
    
    # TODO: 飞书通知示例
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
    
    return SendNotificationOutput(notification=notification, is_sent=True)
