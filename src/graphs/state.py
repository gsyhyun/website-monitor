from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ============= 网站监控相关数据结构 =============

class WebsiteInfo(BaseModel):
    """网站信息"""
    name: str = Field(..., description="网站名称")
    url: str = Field(..., description="网站URL")
    category: str = Field(..., description="网站分类")


class ContentItem(BaseModel):
    """内容项（包含标题、链接和摘要）"""
    title: str = Field(..., description="内容标题")
    link: str = Field(default="", description="内容链接")
    summary: str = Field(default="", description="100字简要内容")
    date: Optional[str] = Field(default=None, description="发布日期")


class FetchResult(BaseModel):
    """抓取结果"""
    website_name: str = Field(..., description="网站名称")
    url: str = Field(..., description="网站URL")
    content_hash: str = Field(..., description="内容哈希值，用于变化检测")
    content_summary: str = Field(..., description="内容摘要（最新N条标题或内容）")
    fetch_time: str = Field(..., description="抓取时间")
    is_success: bool = Field(default=True, description="是否抓取成功")
    error_message: str = Field(default="", description="错误信息")
    content_items: List[ContentItem] = Field(default=[], description="抓取的内容项列表（标题、链接、摘要）")


class ChangeDetectionResult(BaseModel):
    """变化检测结果"""
    website_name: str = Field(..., description="网站名称")
    has_change: bool = Field(..., description="是否有变化")
    new_items: List[ContentItem] = Field(default=[], description="新增的内容项（包含标题、链接、摘要）")
    old_content_hash: str = Field(default="", description="旧内容哈希值")
    new_content_hash: str = Field(default="", description="新内容哈希值")


class NotificationInfo(BaseModel):
    """通知信息"""
    website_name: str = Field(..., description="网站名称")
    has_change: bool = Field(..., description="是否有变化")
    change_details: str = Field(default="", description="变化详情")
    notification_time: str = Field(..., description="通知时间")
    new_items: List[ContentItem] = Field(default=[], description="新增的内容项（包含标题、链接、摘要）")


# ============= 默认网站列表 =============
DEFAULT_WEBSITES = [
    # 佛山自然资源局
    WebsiteInfo(
        name="佛山自然资源局-批前",
        url="https://fszrzy.foshan.gov.cn/ywzt/cxgh/pqgs/index.html",
        category="自然资源局"
    ),
    WebsiteInfo(
        name="佛山自然资源局-批后",
        url="https://fszrzy.foshan.gov.cn/ywzt/cxgh/phgg/",
        category="自然资源局"
    ),
    WebsiteInfo(
        name="佛山自然资源局-通知公告",
        url="https://fszrzy.foshan.gov.cn/zwgk/tzgg/index.html",
        category="自然资源局"
    ),
    # 各区自然资源局
    WebsiteInfo(
        name="禅城区自然资源局",
        url="https://www.chancheng.gov.cn/fscczrzyj/gkmlpt/index",
        category="自然资源局"
    ),
    WebsiteInfo(
        name="南海区自然资源局",
        url="https://www.nanhai.gov.cn/fsnhzrzyj/gkmlpt/mindex/",
        category="自然资源局"
    ),
    WebsiteInfo(
        name="顺德区自然资源局",
        url="https://www.shunde.gov.cn/sdszrzyjsdfj/tzgg/tzggjdt/index.html",
        category="自然资源局"
    ),
    # 公共资源交易
    WebsiteInfo(
        name="佛山公共资源交易网站",
        url="http://jy.ggzy.foshan.gov.cn:3680/TPBank/newweb/framehtml/onlineTradex/index.html",
        category="公共资源交易"
    ),
    # 政府网站
    WebsiteInfo(
        name="佛山市政府-意见征集",
        url="https://www.foshan.gov.cn/hdjl/yjzj/index.html",
        category="市政府"
    ),
    WebsiteInfo(
        name="顺德区人民政府网",
        url="https://www.shunde.gov.cn/sdqrmzf/zwgk/gzdt/tzgg/",
        category="区政府"
    ),
    # 住建局
    WebsiteInfo(
        name="佛山住建局",
        url="https://fszj.foshan.gov.cn/zwgk/txgg/index.html",
        category="住建局"
    ),
    WebsiteInfo(
        name="顺德区住建局",
        url="https://www.shunde.gov.cn/sdqzfjssl/tzggjdt/index.html",
        category="住建局"
    ),
    WebsiteInfo(
        name="南海区住建局",
        url="https://www.nanhai.gov.cn/fsnhq/bmdh/zfbm/qzjhslj/xxgkml/tzgg/index.html",
        category="住建局"
    ),
    WebsiteInfo(
        name="三水区住建局",
        url="https://www.ss.gov.cn/fssscxslj/gkmlpt/index",
        category="住建局"
    ),
    WebsiteInfo(
        name="高明区住建局",
        url="https://www.gaoming.gov.cn/gzjg/zfgzbm/qgtcjswj/gzdt_1106223/index.html",
        category="住建局"
    ),
    # 其他
    WebsiteInfo(
        name="佛山市公积金中心",
        url="https://fsgjj.foshan.gov.cn/xxgk/tztg/index.html",
        category="公积金中心"
    )
]


# ============= 全局状态 =============

class GlobalState(BaseModel):
    """全局状态定义"""
    # 输入数据
    websites: Optional[List[WebsiteInfo]] = Field(
        default=None,
        description="要监控的网站列表"
    )
    email_address: Optional[str] = Field(
        default=None,
        description="接收通知的邮箱地址"
    )

    # 监控过程数据
    current_website: Optional[WebsiteInfo] = Field(default=None, description="当前处理的网站")
    fetch_result: Optional[FetchResult] = Field(default=None, description="抓取结果")
    change_result: Optional[ChangeDetectionResult] = Field(default=None, description="变化检测结果")

    # 循环控制
    loop_index: int = Field(default=0, description="循环索引")

    # 输出数据
    all_notifications: List[NotificationInfo] = Field(default=[], description="所有通知信息")
    monitoring_summary: Dict = Field(default={}, description="监控摘要")


# ============= 工作流输入输出 =============

class GraphInput(BaseModel):
    """工作流输入"""
    websites: Optional[List[WebsiteInfo]] = Field(
        default=None,
        description="要监控的网站列表，为空时使用默认的15个佛山政府网站"
    )
    email_address: Optional[str] = Field(
        default=None,
        description="接收通知的邮箱地址，为空时不发送邮件"
    )

    @field_validator('websites', mode='before')
    @classmethod
    def set_default_websites(cls, v):
        """如果网站列表为空，使用默认列表"""
        if v is None or (isinstance(v, list) and len(v) == 0):
            return DEFAULT_WEBSITES
        return v


class GraphOutput(BaseModel):
    """工作流输出"""
    all_notifications: List[NotificationInfo] = Field(default=[], description="所有通知信息")
    monitoring_summary: Dict = Field(default={}, description="监控摘要")


# ============= 节点输入输出定义 =============

# 抓取节点
class FetchWebsiteInput(BaseModel):
    """抓取网站节点输入"""
    website: WebsiteInfo = Field(..., description="要抓取的网站信息")


class FetchWebsiteOutput(BaseModel):
    """抓取网站节点输出"""
    fetch_result: FetchResult = Field(..., description="抓取结果")


# 变化检测节点
class CheckChangesInput(BaseModel):
    """变化检测节点输入"""
    fetch_result: FetchResult = Field(..., description="抓取结果")
    website: WebsiteInfo = Field(..., description="网站信息")


class CheckChangesOutput(BaseModel):
    """变化检测节点输出"""
    change_result: ChangeDetectionResult = Field(..., description="变化检测结果")


# 内容摘要生成节点
class GenerateSummaryInput(BaseModel):
    """内容摘要生成节点输入"""
    fetch_result: FetchResult = Field(..., description="抓取结果")


class GenerateSummaryOutput(BaseModel):
    """内容摘要生成节点输出"""
    fetch_result: FetchResult = Field(..., description="包含摘要的抓取结果")


# 发送通知节点
class SendNotificationInput(BaseModel):
    """发送通知节点输入"""
    change_result: ChangeDetectionResult = Field(..., description="变化检测结果")
    website: WebsiteInfo = Field(..., description="网站信息")
    email_address: Optional[str] = Field(
        default=None,
        description="接收通知的邮箱地址，为空时不发送邮件"
    )


class SendNotificationOutput(BaseModel):
    """发送通知节点输出"""
    notification: NotificationInfo = Field(..., description="通知信息")
    is_sent: bool = Field(default=True, description="是否发送成功")


# 循环监控节点
class LoopMonitorInput(BaseModel):
    """循环监控节点输入"""
    websites: List[WebsiteInfo] = Field(..., description="要监控的网站列表")


class LoopMonitorOutput(BaseModel):
    """循环监控节点输出"""
    all_notifications: List[NotificationInfo] = Field(..., description="所有通知信息")
    monitoring_summary: Dict = Field(..., description="监控摘要")


# 主图监控节点
class MonitorAllWebsitesInput(BaseModel):
    """主图监控节点输入"""
    websites: Optional[List[WebsiteInfo]] = Field(
        default=None,
        description="要监控的网站列表"
    )
    email_address: Optional[str] = Field(
        default=None,
        description="接收通知的邮箱地址，为空时不发送邮件"
    )


class MonitorAllWebsitesOutput(BaseModel):
    """主图监控节点输出"""
    all_notifications: List[NotificationInfo] = Field(..., description="所有通知信息")
    monitoring_summary: Dict = Field(..., description="监控摘要")


class MonitorWebsitesInput(BaseModel):
    """主图监控节点输入"""
    websites: List[WebsiteInfo] = Field(..., description="要监控的网站列表")


class MonitorWebsitesOutput(BaseModel):
    """主图监控节点输出"""
    all_notifications: List[NotificationInfo] = Field(..., description="所有通知信息")
    monitoring_summary: Dict = Field(..., description="监控摘要")


# 初始化网站节点
class InitializeWebsitesInput(BaseModel):
    """初始化网站节点输入"""
    websites: Optional[List[WebsiteInfo]] = Field(default=None, description="输入的网站列表")


class InitializeWebsitesOutput(BaseModel):
    """初始化网站节点输出"""
    websites: List[WebsiteInfo] = Field(..., description="初始化后的网站列表")
