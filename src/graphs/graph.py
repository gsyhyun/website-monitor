from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
    MonitorWebsitesInput,
    MonitorWebsitesOutput
)
from graphs.loop_graph import loop_subgraph


def monitor_websites_node(
    state: MonitorWebsitesInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MonitorWebsitesOutput:
    """
    title: 网站监控主节点
    desc: 调用循环监控子图，对所有网站进行监控
    integrations:
    """
    ctx = runtime.context

    # 准备子图输入
    input_state = GlobalState(
        websites=state.websites
    )

    # 调用子图
    result_dict = loop_subgraph.invoke(input_state, config)

    # 构建输出
    output = MonitorWebsitesOutput(
        all_notifications=result_dict.get("all_notifications", []),
        monitoring_summary=result_dict.get("monitoring_summary", {})
    )

    return output


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
    builder.add_node("monitor_websites", monitor_websites_node)
    
    # 设置入口点
    builder.set_entry_point("monitor_websites")
    
    # 添加边到结束节点
    builder.add_edge("monitor_websites", END)
    
    # 编译图
    return builder.compile()


# 编译主图
main_graph = build_main_graph()
