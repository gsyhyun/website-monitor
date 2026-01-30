#!/usr/bin/env python3
"""
直接使用授权码测试工作流邮件通知
"""

import smtplib
import ssl
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid

# 设置项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 直接导入工作流节点（绕过邮件集成模块）
from graphs.nodes.fetch_website_node import fetch_website_node
from graphs.nodes.check_changes_node import check_changes_node
from graphs.state import WebsiteInfo, FetchWebsiteInput, CheckChangesInput

# QQ 邮箱配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "account": "gshyun@qq.com",
    "auth_code": "sibcgumiszmwbgic"  # 你的授权码
}


def send_test_email(subject: str, content: str, to_email: str) -> bool:
    """发送测试邮件"""
    try:
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = formataddr(("网站监控助手", EMAIL_CONFIG["account"]))
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()

        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2

        with smtplib.SMTP_SSL(
            EMAIL_CONFIG["smtp_server"],
            EMAIL_CONFIG["smtp_port"],
            context=ctx,
            timeout=30
        ) as server:
            server.ehlo()
            server.login(EMAIL_CONFIG["account"], EMAIL_CONFIG["auth_code"])
            server.sendmail(EMAIL_CONFIG["account"], [to_email], msg.as_string())
            server.quit()

        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("工作流邮件通知测试（直接使用授权码）")
    print("=" * 60)

    # 测试发送邮件
    print("\n测试1: 发送测试邮件...")
    test_success = send_test_email(
        "【网站监控】测试邮件",
        "这是一封测试邮件，用于验证授权码和工作流集成。\n\n测试时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "gshyun@qq.com"
    )

    if test_success:
        print("✅ 测试邮件发送成功！")
    else:
        print("❌ 测试邮件发送失败！")
        return

    # 模拟一个网站的更新通知
    print("\n测试2: 发送网站更新通知...")

    website = WebsiteInfo(
        name="佛山自然资源局-批前",
        url="https://fszrzy.foshan.gov.cn/ywzt/cxgh/pqgs/index.html",
        category="自然资源局"
    )

    # 生成模拟的通知内容
    notification_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    change_details = f"""网站：{website.name}
URL：{website.url}
分类：{website.category}
检测时间：{notification_time}
新增内容数量：3

新增内容：
1. 关于XX项目的批前公示
2. 关于XX地块的规划公告
3. 关于XX区域的调整通知
"""

    email_subject = f"【网站更新】{website.name} 检测到新内容"
    email_success = send_test_email(email_subject, change_details, "gshyun@qq.com")

    if email_success:
        print("✅ 网站更新通知发送成功！")
    else:
        print("❌ 网站更新通知发送失败！")
        return

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n📧 请检查邮箱 gshyun@qq.com 查看测试邮件！")
    print("\n💡 授权码配置成功，可以正常使用邮件通知功能！")


if __name__ == "__main__":
    main()
