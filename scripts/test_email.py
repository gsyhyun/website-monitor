#!/usr/bin/env python3
"""
测试邮件发送功能
"""
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587
EMAIL_ACCOUNT = "gshyun@qq.com"
AUTH_CODE = "sibcgumiszmwbgic"

def test_email():
    """测试邮件发送"""
    # 尝试两种方式
    ports_to_test = [465, 587]

    for port in ports_to_test:
        try:
            print("=" * 60)
            print(f"测试邮件配置 - 端口 {port}")
            print("=" * 60)
            print(f"SMTP服务器: {SMTP_SERVER}")
            print(f"SMTP端口: {port}")
            print(f"邮箱账号: {EMAIL_ACCOUNT}")
            print(f"授权码: {'*' * len(AUTH_CODE)}")
            print("=" * 60)
            print()

            # 创建测试邮件
            msg = MIMEText("这是一封测试邮件，来自网站监控系统。", "plain", "utf-8")
            msg["From"] = formataddr(("网站监控助手", EMAIL_ACCOUNT))
            msg["To"] = EMAIL_ACCOUNT
            msg["Subject"] = Header(f"【测试】网站监控系统邮件配置测试 (端口{port})", "utf-8")

            # 创建SSL上下文
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            print(f"尝试连接SMTP服务器 (端口 {port})...")

            if port == 465:
                # SSL方式
                print("使用SSL方式连接...")
                with smtplib.SMTP_SSL(SMTP_SERVER, port, context=ctx, timeout=30) as server:
                    server.ehlo()
                    print(f"✅ 成功连接到 {SMTP_SERVER}:{port}")
                    print()
                    
                    print("尝试登录邮件服务器...")
                    server.login(EMAIL_ACCOUNT, AUTH_CODE)
                    print("✅ 登录成功！")
                    print()
                    
                    print("发送测试邮件...")
                    server.sendmail(EMAIL_ACCOUNT, [EMAIL_ACCOUNT], msg.as_string())
                    print("✅ 邮件发送成功！")
                    print()
                    
                    server.quit()
                    print("✅ 断开连接")
            else:
                # STARTTLS方式
                print("使用STARTTLS方式连接...")
                with smtplib.SMTP(SMTP_SERVER, port, timeout=30) as server:
                    server.ehlo()
                    print(f"✅ 成功连接到 {SMTP_SERVER}:{port}")
                    print()
                    
                    print("启动STARTTLS...")
                    server.starttls(context=ctx)
                    print("✅ STARTTLS启动成功")
                    print()
                    
                    server.ehlo()
                    print("尝试登录邮件服务器...")
                    server.login(EMAIL_ACCOUNT, AUTH_CODE)
                    print("✅ 登录成功！")
                    print()
                    
                    print("发送测试邮件...")
                    server.sendmail(EMAIL_ACCOUNT, [EMAIL_ACCOUNT], msg.as_string())
                    print("✅ 邮件发送成功！")
                    print()
                    
                    server.quit()
                    print("✅ 断开连接")

            print()
            print("=" * 60)
            print(f"邮件测试成功！(端口 {port})")
            print("=" * 60)
            print(f"请检查邮箱 {EMAIL_ACCOUNT} 查收测试邮件")

            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ 认证失败: {e}")
            print()
            print("可能的原因：")
            print("1. 授权码不正确")
            print("2. 邮箱未开启SMTP服务")
            print("3. 授权码已过期")
            print()
            print("解决方法：")
            print("1. 登录QQ邮箱网页版")
            print("2. 进入设置 -> 账户")
            print("3. 开启SMTP服务")
            print("4. 获取授权码（16位）")
            print()
            print("注意：授权码不是QQ密码，而是16位的随机字符串")
            return False

        except smtplib.SMTPConnectError as e:
            print(f"❌ 连接失败: {e}")
            print()
            print("可能的原因：")
            print("1. SMTP服务器地址不正确")
            print("2. 端口不正确")
            print("3. 网络问题")
            print()
            print("QQ邮箱SMTP配置：")
            print("服务器: smtp.qq.com")
            print("端口: 587 (STARTTLS) 或 465 (SSL)")
            continue

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            continue

    print()
    print("=" * 60)
    print("所有端口测试失败")
    print("=" * 60)
    return False

if __name__ == "__main__":
    test_email()
