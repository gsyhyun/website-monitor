import hashlib
import logging
import re
from datetime import datetime, date
from typing import Optional
from urllib.parse import urljoin
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import (
    FetchWebsiteInput,
    FetchWebsiteOutput,
    FetchResult,
    WebsiteInfo,
    ContentItem
)


logger = logging.getLogger(__name__)


def extract_date_from_text(text: str) -> Optional[str]:
    """
    从文本中提取日期
    
    Args:
        text: 文本内容
        
    Returns:
        日期字符串（格式：YYYY-MM-DD），如果没有找到返回None
    """
    # 匹配常见的日期格式：2026-01-30, 2026/01/30, 20260130等
    date_patterns = [
        r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日号]?',  # 2026-01-30, 2026年1月30日
        r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',  # 2026-01-30
        r'(\d{4})(\d{2})(\d{2})',  # 20260130
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            year, month, day = match.groups()
            try:
                # 验证日期是否有效
                datetime(int(year), int(month), int(day))
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            except ValueError:
                continue
    
    return None


def extract_date_from_url(url: str) -> Optional[str]:
    """
    从URL中提取日期
    
    Args:
        url: URL链接
        
    Returns:
        日期字符串（格式：YYYY-MM-DD），如果没有找到返回None
    """
    # 从URL中提取日期（例如：post_20260130.html）
    date_pattern = r'(\d{4})[-/]?(\d{2})[-/]?(\d{2})'
    match = re.search(date_pattern, url)
    
    if match:
        year, month, day = match.groups()
        try:
            # 验证日期是否有效
            datetime(int(year), int(month), int(day))
            return f"{year}-{month}-{day}"
        except ValueError:
            return None
    
    return None


def fetch_website_node(
    state: FetchWebsiteInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> FetchWebsiteOutput:
    """
    title: 网站内容抓取
    desc: 抓取指定网站的内容，提取当天最新的标题、链接，并进行日期过滤
    integrations: 
    """
    ctx = runtime.context
    
    website = state.website
    logger.info(f"开始抓取网站: {website.name}, URL: {website.url}")
    
    # 获取今天的日期
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    
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
        
        # 提取链接和文本内容
        content_items = []
        links = soup.find_all('a', href=True)
        
        # 过滤出有意义的链接（只保留通知相关的内容）
        meaningful_links = []
        notification_keywords = ['通知', '公告', '通告', '公示', '声明']  # 只抓取这些关键词的内容
        
        for link in links[:100]:  # 限制检查前100个链接
            text = link.get_text(strip=True)
            if text and len(text) > 3 and len(text) < 200:  # 排除过短或过长的文本
                # 排除常见的无意义链接
                skip_keywords = ['首页', '导航', '联系我们', '登录', '注册', '更多', '下一页', '上一页', 
                               '返回', '跳转', '刷新', '版权', '隐私', '友情链接', '信息公开', '工作动态',
                               '机构概况', '法规政策', '行政执法', '数据开放', '银行承办', '办事指南',
                               '我的收藏', '互动交流', '政务服务', '工作机构']
                
                # 必须包含通知关键词，且不包含跳过关键词
                has_notification_keyword = any(keyword in text for keyword in notification_keywords)
                has_skip_keyword = any(keyword in text for keyword in skip_keywords)
                
                if has_notification_keyword and not has_skip_keyword:
                    meaningful_links.append({
                        'text': text,
                        'href': link.get('href', ''),
                        'element': link  # 保存链接元素，用于提取日期
                    })
        
        # 构建完整URL并创建ContentItem
        for item in meaningful_links[:50]:  # 最多取50条
            text = item['text']
            href = item['href']
            link_element = item.get('element')
            
            # 构建完整URL
            if href.startswith('http'):
                full_url = href
            else:
                full_url = urljoin(website.url, href)
            
            # 尝试提取日期
            item_date = extract_date_from_url(full_url) or extract_date_from_text(text)
            
            # 如果没有提取到日期，尝试查找附近的日期元素
            if not item_date and link_element:
                # 查找父元素中的日期信息
                parent = link_element.find_parent()
                if parent:
                    parent_text = parent.get_text()
                    item_date = extract_date_from_text(parent_text)
            
            # 创建ContentItem
            content_item = ContentItem(
                title=text,
                link=full_url,
                summary="",  # 暂时为空，稍后填充
                date=item_date  # 提取到的日期
            )
            content_items.append(content_item)
        
        # 如果没有抓取到内容，尝试获取页面标题
        if not content_items:
            page_title = soup.title.string if soup.title else "无标题"
            content_items.append(ContentItem(
                title=page_title,
                link=website.url,
                summary="页面标题",
                date=today_str
            ))
        
        # 生成内容摘要（用于哈希计算）
        content_summary = " | ".join([item.title for item in content_items[:20]])
        
        # 生成内容哈希值（使用所有标题）
        content_for_hash = "|||".join([item.title for item in content_items])
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
            error_message="",
            content_items=content_items
        )
        
        logger.info(f"成功抓取网站: {website.name}, 提取到 {len(content_items)} 条内容")
        
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
            error_message=error_msg,
            content_items=[]
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
            error_message=error_msg,
            content_items=[]
        )
        
        return FetchWebsiteOutput(fetch_result=fetch_result)
