import logging
from typing import List, Optional
from langgraph.graph import StateGraph, END
from graphs.state import (
    # 使用全局状态作为子图状态
    GlobalState,
    WebsiteInfo,
    FetchResult,
    ChangeDetectionResult,
    NotificationInfo
)
from graphs.nodes.fetch_website_node import fetch_website_node
from graphs.nodes.check_changes_node import check_changes_node
from graphs.nodes.send_notification_node import send_notification_node


logger = logging.getLogger(__name__)


# 初始化循环
def initialize_loop(state: GlobalState) -> GlobalState:
    """
    初始化循环，准备处理所有网站
    """
    state.all_notifications = []
    state.current_website = None
    state.loop_index = 0
    state.monitoring_summary = {}

    return state


# 循环处理所有网站
def process_all_websites(state: GlobalState) -> GlobalState:
    """
    在单个节点中循环处理所有网站
    """
    # 如果没有提供网站列表，返回空结果
    if not state.websites:
        logger.warning("没有提供网站列表，跳过处理")
        state.all_notifications = []
        state.monitoring_summary = {
            "total_websites": 0,
            "processed": 0,
            "websites_with_changes": 0
        }
        return state

    logger.info(f"开始处理 {len(state.websites)} 个网站")

    state.all_notifications = []
    state.monitoring_summary = {
        "total_websites": len(state.websites),
        "processed": 0,
        "websites_with_changes": 0
    }

    # 遍历所有网站
    for index, website in enumerate(state.websites):
        logger.info(f"处理第 {index + 1}/{len(state.websites)} 个网站: {website.name}")
        state.current_website = website

        try:
            # 1. 抓取网站内容
            from graphs.state import FetchWebsiteInput
            fetch_input = FetchWebsiteInput(website=website)
            fetch_output = fetch_website_node(
                fetch_input,
                {},  # config
                None  # runtime
            )

            state.fetch_result = fetch_output.fetch_result

            # 2. 检测变化
            from graphs.state import CheckChangesInput
            check_input = CheckChangesInput(
                fetch_result=fetch_output.fetch_result,
                website=website
            )
            check_output = check_changes_node(
                check_input,
                {},  # config
                None  # runtime
            )

            state.change_result = check_output.change_result

            # 3. 发送通知
            from graphs.state import SendNotificationInput
            notify_input = SendNotificationInput(
                change_result=check_output.change_result,
                website=website
            )
            notify_output = send_notification_node(
                notify_input,
                {},  # config
                None  # runtime
            )

            # 收集通知信息
            if notify_output.notification.has_change:
                state.all_notifications.append(notify_output.notification)
                state.monitoring_summary["websites_with_changes"] += 1

            state.monitoring_summary["processed"] += 1
            logger.info(f"网站 {website.name} 处理完成")

        except Exception as e:
            logger.error(f"处理网站 {website.name} 时发生异常: {e}")
            state.monitoring_summary["processed"] += 1

    logger.info(f"所有网站处理完成，共 {len(state.all_notifications)} 个网站有更新")

    return state


# 构建子图
def build_loop_graph():
    """
    构建循环监控子图
    """
    # 创建子图
    subgraph = StateGraph(GlobalState)

    # 添加节点
    subgraph.add_node("initialize", initialize_loop)
    subgraph.add_node("process_all", process_all_websites)

    # 设置入口点
    subgraph.set_entry_point("initialize")

    # 添加边（线性流程）
    subgraph.add_edge("initialize", "process_all")
    subgraph.add_edge("process_all", END)

    return subgraph.compile()


# 编译子图
loop_subgraph = build_loop_graph()
