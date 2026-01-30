import hashlib
import logging
from datetime import datetime
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import FetchWebsiteInput, FetchWebsiteOutput, FetchResult, WebsiteInfo


logger = logging.getLogger(__name__)


def fetch_website_node(
    state: FetchWebsiteInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> FetchWebsiteOutput:
    """
    title: 网站内容抓取
    desc: 抓取指定网站的内容，提取关键信息并生成内容摘要和哈希值
    integrations: 
    """
    ctx = runtime.context
    
    website = state.website
    logger.info(f"开始抓取网站: {website.name}, URL: {website.url}")
    
    try:
        # 导入requests和beautifulsoup4
        import requests
        from bs4 import BeautifulSoup
        
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送请求
        response = requests.get(website.url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取页面标题
        page_title = soup.title.string if soup.title else "无标题"
        
        # 提取链接和文本内容（提取前20条）
        items = []
        links = soup.find_all('a', href=True)
        
        # 过滤出有意义的链接（排除纯导航、页脚等）
        meaningful_links = []
        for link in links[:50]:  # 限制检查前50个链接
            text = link.get_text(strip=True)
            if text and len(text) > 3 and len(text) < 200:  # 排除过短或过长的文本
                # 排除常见的无意义链接
                skip_keywords = ['首页', '导航', '联系我们', '登录', '注册', '更多', '下一页', '上一页']
                if not any(keyword in text for keyword in skip_keywords):
                    meaningful_links.append(text)
        
        # 取前20条有意义的链接文本
        items = meaningful_links[:20]
        
        # 生成内容摘要（将所有项合并为字符串）
        content_summary = " | ".join(items) if items else "未找到有效内容"
        
        # 生成内容哈希值（使用所有链接文本）
        content_for_hash = "|||".join(items)
        content_hash = hashlib.md5(content_for_hash.encode('utf-8')).hexdigest()
        
        # 生成抓取时间
        fetch_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建结果
        fetch_result = FetchResult(
            website_name=website.name,
            url=website.url,
            content_hash=content_hash,
            content_summary=content_summary,
            fetch_time=fetch_time,
            is_success=True,
            error_message=""
        )
        
        logger.info(f"成功抓取网站: {website.name}, 提取到 {len(items)} 条内容")
        
        return FetchWebsiteOutput(fetch_result=fetch_result)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"请求失败: {str(e)}"
        logger.error(f"抓取网站 {website.name} 失败: {error_msg}")
        
        fetch_result = FetchResult(
            website_name=website.name,
            url=website.url,
            content_hash="",
            content_summary="",
            fetch_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            is_success=False,
            error_message=error_msg
        )
        
        return FetchWebsiteOutput(fetch_result=fetch_result)
        
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        logger.error(f"抓取网站 {website.name} 发生异常: {error_msg}")
        
        fetch_result = FetchResult(
            website_name=website.name,
            url=website.url,
            content_hash="",
            content_summary="",
            fetch_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            is_success=False,
            error_message=error_msg
        )
        
        return FetchWebsiteOutput(fetch_result=fetch_result)
