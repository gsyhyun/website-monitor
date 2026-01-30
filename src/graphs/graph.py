import logging
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
    MonitorAllWebsitesInput,
    MonitorAllWebsitesOutput,
    WebsiteInfo,
    FetchResult,
    ChangeDetectionResult,
    NotificationInfo
)
from graphs.nodes.fetch_website_node import fetch_website_node
from graphs.nodes.check_changes_node import check_changes_node
from graphs.nodes.send_notification_node import send_notification_node


logger = logging.getLogger(__name__)


def monitor_all_websites_node(
    state: MonitorAllWebsitesInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MonitorAllWebsitesOutput:
    """
    title: 网站监控主节点
    desc: 监控所有网站，如果没有提供网站列表则使用默认的15个佛山政府网站
    integrations:
    """
    ctx = runtime.context

    # 如果没有提供网站列表，使用默认列表
    if not state.websites:
        from graphs.state import DEFAULT_WEBSITES
        websites_to_monitor = DEFAULT_WEBSITES
        logger.info(f"使用默认网站列表，共 {len(DEFAULT_WEBSITES)} 个网站")
    else:
        websites_to_monitor = state.websites
        logger.info(f"使用自定义网站列表，共 {len(state.websites)} 个网站")

    # 初始化状态
    all_notifications = []
    monitoring_summary = {
        "total_websites": len(websites_to_monitor),
        "processed": 0,
        "websites_with_changes": 0
    }

    # 遍历所有网站
    for index, website in enumerate(websites_to_monitor):
        logger.info(f"处理第 {index + 1}/{len(websites_to_monitor)} 个网站: {website.name}")

        try:
            # 1. 抓取网站内容
            from graphs.state import FetchWebsiteInput
            fetch_input = FetchWebsiteInput(website=website)
            fetch_output = fetch_website_node(
                fetch_input,
                {},
                None
            )

            # 2. 检测变化
            from graphs.state import CheckChangesInput
            check_input = CheckChangesInput(
                fetch_result=fetch_output.fetch_result,
                website=website
            )
            check_output = check_changes_node(
                check_input,
                {},
                None
            )

            # 3. 发送通知
            from graphs.state import SendNotificationInput
            notify_input = SendNotificationInput(
                change_result=check_output.change_result,
                website=website
            )
            notify_output = send_notification_node(
                notify_input,
                {},
                None
            )

            # 收集通知信息
            if notify_output.notification.has_change:
                all_notifications.append(notify_output.notification)
                monitoring_summary["websites_with_changes"] += 1

            monitoring_summary["processed"] += 1
            logger.info(f"网站 {website.name} 处理完成")

        except Exception as e:
            logger.error(f"处理网站 {website.name} 时发生异常: {e}")
            monitoring_summary["processed"] += 1

    logger.info(f"所有网站处理完成，共 {len(all_notifications)} 个网站有更新")

    return MonitorAllWebsitesOutput(
        all_notifications=all_notifications,
        monitoring_summary=monitoring_summary
    )


# 构建主图
def build_main_graph() -> StateGraph:
    """
    构建主图
    """
    # 创建状态图，指定入参和出参
    builder = StateGraph(
        GlobalState,
        input_schema=GraphInput,
        output_schema=GraphOutput
    )

    # 添加节点
    builder.add_node("monitor_all_websites", monitor_all_websites_node, metadata={"type": "task"})

    # 设置入口点
    builder.set_entry_point("monitor_all_websites")

    # 添加边到结束节点
    builder.add_edge("monitor_all_websites", END)

    # 编译图
    return builder.compile()


# 编译主图
main_graph = build_main_graph()
