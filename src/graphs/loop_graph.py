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


# 列表循环节点：处理当前网站
def process_current_website(state: GlobalState) -> GlobalState:
    """
    处理当前网站的完整监控流程
    """
    # 获取当前网站
    current_website = state.current_website
    if current_website is None:
        logger.warning("当前网站为空，跳过处理")
        return state
    
    logger.info(f"开始处理网站: {current_website.name}")
    
    try:
        # 1. 抓取网站内容
        from graphs.state import FetchWebsiteInput
        fetch_input = FetchWebsiteInput(website=current_website)
        fetch_output = fetch_website_node(
            fetch_input,
            {},  # config
            None  # runtime, 子图中可以传None
        )
        
        # 更新状态
        state.fetch_result = fetch_output.fetch_result
        
        # 2. 检测变化
        from graphs.state import CheckChangesInput
        check_input = CheckChangesInput(
            fetch_result=fetch_output.fetch_result,
            website=current_website
        )
        check_output = check_changes_node(
            check_input,
            {},  # config
            None  # runtime
        )
        
        # 更新状态
        state.change_result = check_output.change_result
        
        # 3. 发送通知
        from graphs.state import SendNotificationInput
        notify_input = SendNotificationInput(
            change_result=check_output.change_result,
            website=current_website
        )
        notify_output = send_notification_node(
            notify_input,
            {},  # config
            None  # runtime
        )
        
        # 收集通知信息
        if notify_output.notification.has_change:
            state.all_notifications.append(notify_output.notification)
        
        logger.info(f"网站 {current_website.name} 处理完成")
        
    except Exception as e:
        logger.error(f"处理网站 {current_website.name} 时发生异常: {e}")
    
    return state


# 循环条件：检查是否还有未处理的网站
def has_more_websites(state: GlobalState) -> str:
    """
    判断是否还有网站需要处理
    """
    # 获取当前索引（从附加字段中获取）
    current_index = getattr(state, '_loop_index', 0)
    
    if current_index >= len(state.websites):
        return "完成"
    else:
        return "继续"


# 设置下一个网站
def set_next_website(state: GlobalState) -> GlobalState:
    """
    设置下一个要处理的网站
    """
    current_index = getattr(state, '_loop_index', 0)
    next_index = current_index + 1
    
    # 检查是否还有下一个网站
    if next_index < len(state.websites):
        state.current_website = state.websites[next_index]
        state._loop_index = next_index
    else:
        state.current_website = None
        state._loop_index = next_index
    
    return state


# 初始化循环
def initialize_loop(state: GlobalState) -> GlobalState:
    """
    初始化循环，设置第一个网站
    """
    if state.websites and len(state.websites) > 0:
        state.current_website = state.websites[0]
        state._loop_index = 0
        state.all_notifications = []
        state.monitoring_summary = {
            "total_websites": len(state.websites),
            "processed": 0,
            "websites_with_changes": 0
        }
    else:
        state.current_website = None
        state._loop_index = 0
        state.all_notifications = []
        state.monitoring_summary = {}
    
    return state


# 更新监控摘要
def update_summary(state: GlobalState) -> GlobalState:
    """
    更新监控摘要
    """
    state.monitoring_summary["processed"] = getattr(state, '_loop_index', 0) + 1
    state.monitoring_summary["websites_with_changes"] = len(state.all_notifications)
    
    return state


# 构建子图
def build_loop_graph() -> StateGraph:
    """
    构建循环监控子图
    """
    # 创建子图
    subgraph = StateGraph(GlobalState)
    
    # 添加节点
    subgraph.add_node("initialize", initialize_loop)
    subgraph.add_node("process", process_current_website)
    subgraph.add_node("set_next", set_next_website)
    subgraph.add_node("update_summary", update_summary)
    
    # 设置入口点
    subgraph.set_entry_point("initialize")
    
    # 添加边
    subgraph.add_edge("initialize", "process")
    subgraph.add_edge("process", "update_summary")
    subgraph.add_edge("update_summary", "set_next")
    
    # 添加条件边
    subgraph.add_conditional_edges(
        source="set_next",
        path=has_more_websites,
        path_map={
            "继续": "process",
            "完成": END
        }
    )
    
    return subgraph.compile()


# 编译子图
loop_subgraph = build_loop_graph()
