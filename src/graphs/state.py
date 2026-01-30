from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


# ============= 网站监控相关数据结构 =============

class WebsiteInfo(BaseModel):
    """网站信息"""
    name: str = Field(..., description="网站名称")
    url: str = Field(..., description="网站URL")
    category: str = Field(..., description="网站分类")


class FetchResult(BaseModel):
    """抓取结果"""
    website_name: str = Field(..., description="网站名称")
    url: str = Field(..., description="网站URL")
    content_hash: str = Field(..., description="内容哈希值，用于变化检测")
    content_summary: str = Field(..., description="内容摘要（最新N条标题或内容）")
    fetch_time: str = Field(..., description="抓取时间")
    is_success: bool = Field(default=True, description="是否抓取成功")
    error_message: str = Field(default="", description="错误信息")


class ChangeDetectionResult(BaseModel):
    """变化检测结果"""
    website_name: str = Field(..., description="网站名称")
    has_change: bool = Field(..., description="是否有变化")
    new_items: List[str] = Field(default=[], description="新增的内容项（标题）")
    old_content_hash: str = Field(default="", description="旧内容哈希值")
    new_content_hash: str = Field(default="", description="新内容哈希值")


class NotificationInfo(BaseModel):
    """通知信息"""
    website_name: str = Field(..., description="网站名称")
    has_change: bool = Field(..., description="是否有变化")
    change_details: str = Field(default="", description="变化详情")
    notification_time: str = Field(..., description="通知时间")


# ============= 全局状态 =============

class GlobalState(BaseModel):
    """全局状态定义"""
    # 输入数据
    websites: List[WebsiteInfo] = Field(default=[], description="要监控的网站列表")

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
    websites: List[WebsiteInfo] = Field(..., description="要监控的网站列表")


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


# 发送通知节点
class SendNotificationInput(BaseModel):
    """发送通知节点输入"""
    change_result: ChangeDetectionResult = Field(..., description="变化检测结果")
    website: WebsiteInfo = Field(..., description="网站信息")


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
class MonitorWebsitesInput(BaseModel):
    """主图监控节点输入"""
    websites: List[WebsiteInfo] = Field(..., description="要监控的网站列表")


class MonitorWebsitesOutput(BaseModel):
    """主图监控节点输出"""
    all_notifications: List[NotificationInfo] = Field(..., description="所有通知信息")
    monitoring_summary: Dict = Field(..., description="监控摘要")
