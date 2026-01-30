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
    desc: 爬取内容页并使用大语言模型生成100字摘要
    integrations: 大语言模型
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
    
    # 尝试使用大语言模型生成摘要
    try:
        # 导入大语言模型集成
        from coze_workload_identity import Client
        client = Client()
        llm_credential = client.get_integration_credential("integration-doubao-seed")
        
        if llm_credential:
            import json
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            # 解析大语言模型配置
            llm_config = json.loads(llm_credential)
            
            # 初始化大语言模型
            llm = ChatOpenAI(
                base_url=llm_config.get("base_url", ""),
                api_key=llm_config.get("api_key", ""),
                model=llm_config.get("model", "doubao-pro-32k"),
                temperature=0.3,
                max_tokens=200
            )
            
            # 为每个内容项生成摘要
            for item in items_to_process:
                try:
                    # 爬取内容页
                    summary = fetch_page_summary(item.link)
                    
                    if summary:
                        # 使用大语言模型生成100字摘要
                        prompt = f"请将以下内容概括为100字以内的简要说明：\n\n{summary}"
                        
                        messages = [HumanMessage(content=prompt)]
                        response = llm.invoke(messages)
                        
                        if response and response.content:
                            item.summary = response.content.strip()
                            logger.info(f"成功生成摘要: {item.title[:20]}...")
                        else:
                            # 如果大语言模型失败，使用原始摘要
                            item.summary = summary[:100] if len(summary) > 100 else summary
                    else:
                        # 如果爬取失败，使用标题作为摘要
                        item.summary = item.title[:100]
                        
                except Exception as e:
                    logger.warning(f"处理内容项失败: {item.title}, 错误: {e}")
                    # 使用标题作为后备摘要
                    item.summary = item.title[:100]
        
        else:
            logger.warning("大语言模型配置未找到，使用简单摘要")
            # 如果没有大语言模型配置，使用简单的摘要方法
            for item in items_to_process:
                summary = fetch_page_summary(item.link)
                if summary:
                    item.summary = summary[:100] if len(summary) > 100 else summary
                else:
                    item.summary = item.title[:100]
    
    except ImportError:
        logger.warning("大语言模型集成未导入，使用简单摘要")
        # 后退到简单摘要
        for item in items_to_process:
            summary = fetch_page_summary(item.link)
            if summary:
                item.summary = summary[:100] if len(summary) > 100 else summary
            else:
                item.summary = item.title[:100]
    
    except Exception as e:
        logger.error(f"生成摘要失败: {e}")
        # 降级处理：使用标题作为摘要
        for item in items_to_process:
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
