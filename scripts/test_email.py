#!/usr/bin/env python3
"""
邮件发送测试脚本
用于测试QQ邮箱授权码是否正确配置

使用方法：
python scripts/test_email.py
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid


def test_send_email():
    """测试发送邮件"""
    # QQ 邮箱配置
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    email_account = "gshyun@qq.com"
    auth_code = "sibcgumiszmwbgic"  # 你的授权码
    to_email = "gshyun@qq.com"  # 接收邮箱（测试发给自己）

    print("=" * 60)
    print("邮件发送测试")
    print("=" * 60)
    print(f"SMTP 服务器: {smtp_server}:{smtp_port}")
    print(f"发件人: {email_account}")
    print(f"收件人: {to_email}")
    print("=" * 60)

    # 创建邮件内容
    subject = "【网站监控】邮件发送测试"
    content = f"""
这是一封测试邮件，用于验证网站监控系统的邮件通知功能。

测试时间: {formatdate(localtime=True)}
测试内容:
- SMTP 服务器: {smtp_server}
- 发件人: {email_account}
- 收件人: {to_email}

如果您收到这封邮件，说明邮件配置成功！🎉
"""

    try:
        # 创建邮件对象
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = formataddr(("网站监控助手", email_account))
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()

        # 创建 SSL 上下文
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2

        print("\n正在连接 SMTP 服务器...")

        # 连接 SMTP 服务器
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=ctx, timeout=30) as server:
            print("✓ 连接成功")

            print("正在登录...")
            server.ehlo()
            server.login(email_account, auth_code)
            print("✓ 登录成功")

            print("正在发送邮件...")
            server.sendmail(email_account, [to_email], msg.as_string())
            print("✓ 邮件发送成功")
            server.quit()

        print("\n" + "=" * 60)
        print("🎉 测试成功！请检查收件箱查看邮件。")
        print("=" * 60)
        return True

    except smtplib.SMTPAuthenticationError as e:
        print("\n❌ 认证失败")
        print(f"错误信息: {e}")
        print("\n可能的原因:")
        print("1. 授权码不正确（请确认是否复制完整）")
        print("2. IMAP/SMTP 服务未开启")
        print("3. 授权码已过期，需要重新生成")
        return False

    except smtplib.SMTPConnectError as e:
        print("\n❌ 连接失败")
        print(f"错误信息: {e}")
        print("\n可能的原因:")
        print("1. 网络连接问题")
        print("2. SMTP 服务器地址或端口错误")
        return False

    except smtplib.SMTPServerDisconnected as e:
        print("\n❌ 服务器断开连接")
        print(f"错误信息: {e}")
        print("\n可能的原因:")
        print("1. 授权码不正确")
        print("2. 服务器限制")
        return False

    except Exception as e:
        print("\n❌ 发送失败")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        return False


def main():
    """主函数"""
    print("\n")
    success = test_send_email()
    print("\n")

    if success:
        print("✅ 授权码配置正确，可以使用邮件通知功能！")
        print("\n接下来你可以:")
        print("1. 启动定期监控: python scripts/periodic_monitor.py --email gshyun@qq.com")
        print("2. 或者单次运行工作流测试")
    else:
        print("❌ 授权码配置有问题，请检查后重试")
        print("\n需要帮助？")
        print("1. 确认授权码是否正确复制（16位字符）")
        print("2. 确认QQ邮箱的 IMAP/SMTP 服务已开启")
        print("3. 重新生成授权码并更新")


if __name__ == "__main__":
    main()
