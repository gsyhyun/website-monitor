import logging
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    GenerateSummaryInput,
    GenerateSummaryOutput,
    FetchResult,
    ContentItem
)


logger = logging.getLogger(__name__)


def generate_summary_node(
    state: GenerateSummaryInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateSummaryOutput:
    """
    title: 内容摘要生成
    desc: 爬取内容页并生成简短摘要（最多100字）
    integrations: 
    """
    ctx = runtime.context
    
    fetch_result = state.fetch_result
    logger.info(f"开始生成摘要: {fetch_result.website_name}")
    
    # 只处理前5个有链接的内容项（避免处理过多）
    items_to_process = [item for item in fetch_result.content_items[:5] if item.link and item.summary == ""]
    
    if not items_to_process:
        logger.info("没有需要处理的内容项")
        return GenerateSummaryOutput(fetch_result=fetch_result)
    
    logger.info(f"准备处理 {len(items_to_process)} 个内容项")
    
    # 使用简单方法生成摘要（不依赖大语言模型）
    for item in items_to_process:
        try:
            # 尝试爬取内容页
            summary = fetch_page_summary(item.link)
            
            if summary and len(summary) > 0:
                # 限制为100字
                item.summary = summary[:100] if len(summary) > 100 else summary
                logger.debug(f"使用页面内容生成摘要: {item.title[:20]}")
            else:
                # 如果爬取失败，使用标题作为摘要
                item.summary = item.title[:100]
                logger.debug(f"使用标题作为摘要: {item.title[:20]}")
                
        except Exception as e:
            logger.warning(f"处理内容项失败: {item.title}, 错误: {e}")
            # 使用标题作为后备摘要
            item.summary = item.title[:100]
    
    logger.info(f"摘要生成完成: {fetch_result.website_name}")
    
    return GenerateSummaryOutput(fetch_result=fetch_result)


def fetch_page_summary(url: str, max_length: int = 500) -> Optional[str]:
    """
    爬取网页内容并生成简要摘要

    Args:
        url: 网页URL
        max_length: 摘要最大长度

    Returns:
        摘要文本，失败返回None
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除不需要的标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # 提取正文文本
        text = soup.get_text(separator=' ', strip=True)
        
        # 限制长度
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text if text else None
        
    except Exception as e:
        logger.warning(f"爬取页面失败: {url}, 错误: {e}")
        return None
