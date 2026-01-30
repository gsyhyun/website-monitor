#!/usr/bin/env python3
"""
测试工作流邮件通知功能
"""

import os
import sys
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 设置环境变量（QQ邮箱授权码）
os.environ["QQ_EMAIL_AUTH_CODE"] = "sibcgumiszmwbgic"

# 导入工作流
from graphs.graph import main_graph

def main():
    print("=" * 60)
    print("工作流邮件通知测试")
    print("=" * 60)
    print("邮箱地址: gshyun@qq.com")
    print("=" * 60)

    # 准备输入参数
    input_data = {
        "email_address": "gshyun@qq.com"
    }

    try:
        print("\n正在运行工作流...")
        result = main_graph.invoke(input_data)

        # 输出结果
        summary = result.get("monitoring_summary", {})
        notifications = result.get("all_notifications", [])

        print("\n" + "=" * 60)
        print("监控完成")
        print("=" * 60)
        print(f"总网站数: {summary.get('total_websites', 0)}")
        print(f"已处理: {summary.get('processed', 0)}")
        print(f"有更新: {summary.get('websites_with_changes', 0)}")

        if notifications:
            print(f"\n✅ 发送了 {len(notifications)} 封邮件通知:")
            for idx, notif in enumerate(notifications[:5], 1):  # 只显示前5个
                print(f"  {idx}. {notif.website_name}")

            if len(notifications) > 5:
                print(f"  ... 还有 {len(notifications) - 5} 个通知")
        else:
            print("\nℹ️  本次没有检测到更新，未发送邮件")
            print("   （这是正常的，因为刚刚已经发送过测试邮件）")

        print("\n" + "=" * 60)
        print("✅ 工作流运行成功！")
        print("=" * 60)

        if notifications:
            print("\n📧 请检查邮箱 gshyun@qq.com 查看通知邮件！")
        else:
            print("\n💡 要测试邮件通知，可以：")
            print("   1. 删除历史记录文件: rm assets/website_monitoring_history.json")
            print("   2. 重新运行此脚本")

    except Exception as e:
        print("\n❌ 运行失败")
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
