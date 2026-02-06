import json
import logging
import os
import smtplib
import ssl
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import SendNotificationInput, SendNotificationOutput, NotificationInfo, ChangeDetectionResult, WebsiteInfo

# 尝试导入邮件集成相关模块（如果已配置）
try:
    from coze_workload_identity import Client
    from cozeloop.decorator import observe
    EMAIL_INTEGRATION_AVAILABLE = True
except ImportError:
    EMAIL_INTEGRATION_AVAILABLE = False
    logging.warning("邮件集成模块未找到，邮件通知功能将不可用")


logger = logging.getLogger(__name__)


def get_email_config():
    """获取邮件配置信息"""
    # 优先从环境变量读取配置（本地测试）
    smtp_server = os.getenv("QQ_SMTP_SERVER", "")
    smtp_port = os.getenv("QQ_SMTP_PORT", "")
    account = os.getenv("QQ_EMAIL_ACCOUNT", "")
    auth_code = os.getenv("QQ_EMAIL_AUTH_CODE", "")

    if smtp_server and smtp_port and account and auth_code:
        logger.info("使用环境变量中的邮件配置")
        return {
            "smtp_server": smtp_server,
            "smtp_port": int(smtp_port),
            "account": account,
            "auth_code": auth_code
        }

    # 如果环境变量不可用，尝试从邮件集成获取
    if EMAIL_INTEGRATION_AVAILABLE:
        try:
            client = Client()
            email_credential = client.get_integration_credential("integration-email-imap-smtp")
            config = json.loads(email_credential)
            
            # 尝试从环境变量覆盖授权码（用于本地测试）
            # 如果设置了 QQ_EMAIL_AUTH_CODE 环境变量，使用它
            auth_code_override = os.getenv("QQ_EMAIL_AUTH_CODE")
            if auth_code_override:
                config["auth_code"] = auth_code_override
                logger.info(f"使用环境变量中的授权码（QQ_EMAIL_AUTH_CODE）")

            return config
        except Exception as e:
            logger.error(f"从集成获取邮件配置失败: {e}")
            raise Exception(f"无法获取邮件配置: {e}")

    raise Exception("邮件配置不可用：既没有环境变量配置，邮件集成也不可用")


@observe
def send_email_notification(subject: str, content: str, to_addrs: list) -> dict:
    """
    发送邮件通知

    Args:
        subject: 邮件主题
        content: 邮件正文（纯文本）
        to_addrs: 收件人列表

    Returns:
        发送结果字典
    """
    if not to_addrs:
        return {"status": "error", "message": "收件人为空"}

    try:
        config = get_email_config()

        # 创建纯文本邮件
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = formataddr(("网站监控助手", config["account"]))
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = Header(subject, "utf-8")
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()

        # 创建SSL上下文
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # 不验证证书（避免SSL错误）

        # 尝试发送邮件（重试3次）
        attempts = 3
        last_err = None
        for i in range(attempts):
            try:
                logger.info(f"尝试第 {i+1} 次发送邮件...")
                
                # 根据端口选择连接方式
                if config["smtp_port"] == 465:
                    # SSL方式
                    logger.info(f"使用SSL连接 {config['smtp_server']}:{config['smtp_port']}")
                    with smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"], context=ctx, timeout=30) as server:
                        server.ehlo()
                        logger.info(f"正在登录邮件服务器...")
                        server.login(config["account"], config["auth_code"])
                        logger.info(f"登录成功，正在发送邮件给 {len(to_addrs)} 位收件人...")
                        server.sendmail(config["account"], to_addrs, msg.as_string())
                        server.quit()
                else:
                    # STARTTLS方式
                    logger.info(f"使用STARTTLS连接 {config['smtp_server']}:{config['smtp_port']}")
                    with smtplib.SMTP(config["smtp_server"], config["smtp_port"], timeout=30) as server:
                        server.ehlo()
                        server.starttls(context=ctx)
                        server.ehlo()
                        logger.info(f"正在登录邮件服务器...")
                        server.login(config["account"], config["auth_code"])
                        logger.info(f"登录成功，正在发送邮件给 {len(to_addrs)} 位收件人...")
                        server.sendmail(config["account"], to_addrs, msg.as_string())
                        server.quit()
                        
                logger.info("邮件发送成功")
                return {"status": "success", "message": f"邮件成功发送给 {len(to_addrs)} 位收件人"}
                
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, smtplib.SMTPDataError, smtplib.SMTPHeloError, ssl.SSLError, OSError, ConnectionError) as e:
                last_err = e
                logger.warning(f"第 {i+1} 次发送失败: {str(e)}")
                time.sleep(1 * (i + 1))

        if last_err:
            return {"status": "error", "message": f"发送失败: {str(last_err)}"}

        return {"status": "error", "message": "发送失败: 未知错误"}

    except smtplib.SMTPAuthenticationError as e:
        return {"status": "error", "message": f"认证失败: {str(e)}"}
    except smtplib.SMTPRecipientsRefused as e:
        return {"status": "error", "message": f"收件人被拒绝: {str(e)}"}
    except smtplib.SMTPSenderRefused as e:
        return {"status": "error", "message": f"发件人被拒绝: {e.smtp_code} {e.smtp_error}"}
    except smtplib.SMTPDataError as e:
        return {"status": "error", "message": f"数据被拒绝: {e.smtp_code} {e.smtp_error}"}
    except smtplib.SMTPConnectError as e:
        return {"status": "error", "message": f"连接失败: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"发送失败: {str(e)}"}


def send_notification_node(
    state: SendNotificationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendNotificationOutput:
    """
    title: 记录并发送通知
    desc: 检测到网站内容更新后，将通知信息保存到文件中，并发送邮件通知
    integrations: 邮件
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

    # 生成简报内容（纯中文，直接简单）
    change_details = f"{website.name}有新内容\n\n"
    change_details += f"发现{len(change_result.new_items)}条新文章：\n\n"

    if change_result.new_items:
        for idx, item in enumerate(change_result.new_items[:20], 1):
            change_details += f"{idx}. {item.title}\n"
            if item.link:
                change_details += f"   {item.link}\n"
            change_details += "\n"

    # 构建通知信息（包含完整的新增内容项）
    notification = NotificationInfo(
        website_name=website.name,
        has_change=True,
        change_details=change_details,
        notification_time=notification_time,
        new_items=change_result.new_items
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
    # 序列化 ContentItem 为字典
    notification_dict = {
        "website_name": notification.website_name,
        "has_change": notification.has_change,
        "change_details": notification.change_details,
        "notification_time": notification.notification_time,
        "new_items": [
            {
                "title": item.title,
                "link": item.link,
                "summary": item.summary,
                "date": item.date
            }
            for item in notification.new_items
        ]
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

    # 检查是否为首次运行（通过判断历史记录文件是否存在或为空）
    # 如果是首次运行，就不发送邮件，只保存到文件
    is_first_run = False
    history_file = os.path.join(workspace_path, "assets", "website_monitoring_history.json")
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                # 检查历史记录中是否已经存在该网站
                website_key = website.url
                if not history.get(website_key):
                    is_first_run = True
        except:
            is_first_run = True
    else:
        is_first_run = True
    
    # 发送邮件通知
    email_sent = False
    if state.email_address and change_result.has_change and not is_first_run:
        try:
            logger.info(f"准备发送邮件通知到: {state.email_address}")
            email_result = send_email_notification(
                subject=f"{website.name}发现{len(change_result.new_items)}条新内容",
                content=change_details,
                to_addrs=[state.email_address]
            )

            if email_result.get("status") == "success":
                logger.info(f"✅ 邮件通知发送成功: {state.email_address}")
                email_sent = True
            else:
                logger.error(f"❌ 邮件通知发送失败: {email_result.get('message')}")
        except Exception as e:
            logger.error(f"❌ 邮件通知发送异常: {e}")
    elif state.email_address and change_result.has_change and is_first_run:
        logger.info(f"⚠️  首次运行，跳过邮件通知（仅保存到文件）")
    else:
        logger.info("未配置邮箱地址，跳过邮件通知")

    # 输出到日志
    logger.info(f"检测到网站更新！\n{change_details}")

    logger.info(f"通知处理完成: {website.name}")

    return SendNotificationOutput(notification=notification, is_sent=is_sent)
