import json
import logging
import os
from datetime import datetime
from typing import Dict, List
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    CheckChangesInput,
    CheckChangesOutput,
    ChangeDetectionResult,
    FetchResult,
    WebsiteInfo,
    ContentItem
)


logger = logging.getLogger(__name__)


def check_changes_node(
    state: CheckChangesInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CheckChangesOutput:
    """
    title: 内容变化检测
    desc: 检测网站内容是否有更新，对比当前和历史内容，提取新增内容
    integrations: 
    """
    ctx = runtime.context
    
    fetch_result = state.fetch_result
    website = state.website
    
    logger.info(f"开始检测网站内容变化: {website.name}")
    
    # 如果抓取失败，直接返回无变化
    if not fetch_result.is_success:
        logger.warning(f"网站 {website.name} 抓取失败，跳过变化检测")
        return CheckChangesOutput(change_result=ChangeDetectionResult(
            website_name=website.name,
            has_change=False,
            new_items=[],
            old_content_hash="",
            new_content_hash=""
        ))
    
    # 定义历史记录文件路径
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "")
    history_file = os.path.join(workspace_path, "assets", "website_monitoring_history.json")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    # 读取历史记录
    history: Dict[str, Dict] = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception as e:
            logger.error(f"读取历史记录文件失败: {e}")
            history = {}
    
    # 获取该网站的历史记录
    website_key = website.url
    old_record = history.get(website_key, {})
    old_content_hash = old_record.get("content_hash", "")
    old_items = old_record.get("items", [])
    
    # 提取当前内容项（ContentItem -> 标题列表）
    current_items_data = fetch_result.content_items
    current_items = [item.title for item in current_items_data]
    
    # 对比哈希值
    has_change = (old_content_hash != fetch_result.content_hash)
    
    # 提取新增的内容项
    new_items: List[ContentItem] = []
    if has_change:
        old_items_set = set(old_items)
        for item in current_items_data:
            if item.title not in old_items_set:
                new_items.append(item)
        
        logger.info(f"网站 {website.name} 检测到变化，新增 {len(new_items)} 条内容")
    else:
        logger.info(f"网站 {website.name} 无变化")
    
    # 更新历史记录（保存标题列表）
    history[website_key] = {
        "content_hash": fetch_result.content_hash,
        "items": current_items,  # 保存标题列表
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "website_name": website.name
    }
    
    # 保存历史记录
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存历史记录失败: {e}")
    
    # 构建检测结果
    change_result = ChangeDetectionResult(
        website_name=website.name,
        has_change=has_change,
        new_items=new_items,
        old_content_hash=old_content_hash,
        new_content_hash=fetch_result.content_hash
    )
    
    return CheckChangesOutput(change_result=change_result)
