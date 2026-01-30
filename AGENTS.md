## 项目概述
- **名称**: 网站内容监控系统
- **功能**: 监控多个政府网站的更新内容，检测到变化时自动通知

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| fetch_website_node | `nodes/fetch_website_node.py` | task | 抓取网站内容并生成哈希值 | - | - |
| check_changes_node | `nodes/check_changes_node.py` | task | 检测网站内容是否有变化 | - | - |
| send_notification_node | `nodes/send_notification_node.py` | task | 发送变化通知 | - | - |
| process_current_website | `loop_graph.py` | task | 处理单个网站的完整流程 | - | - |
| monitor_websites | `graph.py` | task | 调用循环监控子图 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
| 子图名 | 文件位置 | 功能描述 | 被调用节点 |
|-------|---------|------|---------|
| loop_subgraph | `graphs/loop_graph.py` | 循环处理网站列表，执行抓取、检测、通知流程 | monitor_websites |

## 集成使用
- 本项目暂未使用外部集成服务
- 通知功能预留了邮件和飞书消息的集成接口（在send_notification_node.py中）
- 当前版本将变化通知输出到日志文件

## 监控网站列表

### 佛山自然资源局
- 批前: https://fszrzy.foshan.gov.cn/ywzt/cxgh/pqgs/index.html
- 批后: https://fszrzy.foshan.gov.cn/ywzt/cxgh/phgg/
- 通知公告: https://fszrzy.foshan.gov.cn/zwgk/tzgg/index.html

### 各区自然资源局
- 禅城区: https://www.chancheng.gov.cn/fscczrzyj/gkmlpt/index
- 南海区: https://www.nanhai.gov.cn/fsnhzrzyj/gkmlpt/mindex/
- 顺德区: https://www.shunde.gov.cn/sdszrzyjsdfj/tzgg/tzggjdt/index.html

### 公共资源交易
- 佛山公共资源交易: http://jy.ggzy.foshan.gov.cn:3680/TPBank/newweb/framehtml/onlineTradex/index.html

### 政府网站
- 意见征集: https://www.foshan.gov.cn/hdjl/yjzj/index.html
- 顺德区人民政府: https://www.shunde.gov.cn/sdqrmzf/zwgk/gzdt/tzgg/

### 住建局
- 佛山住建局: https://fszj.foshan.gov.cn/zwgk/txgg/index.html
- 顺德区住建局: https://www.shunde.gov.cn/sdqzfjssl/tzggjdt/index.html
- 南海区住建局: https://www.nanhai.gov.cn/fsnhq/bmdh/zfbm/qzjhslj/xxgkml/tzgg/index.html
- 三水区住建局: https://www.ss.gov.cn/fssscxslj/gkmlpt/index
- 高明区住建局: https://www.gaoming.gov.cn/gzjg/zfgzbm/qgtcjswj/gzdt_1106223/index.html

### 其他
- 佛山市公积金中心: https://fsgjj.foshan.gov.cn/xxgk/tztg/index.html

## 工作流程

1. **主图启动**: 接收网站列表作为输入
2. **循环处理**: 对每个网站执行以下流程：
   - **抓取内容**: 访问网站URL，提取页面中的标题和链接
   - **生成哈希**: 根据内容生成MD5哈希值
   - **对比检测**: 与历史记录对比，检测是否有变化
   - **提取新增**: 如果有变化，提取新增的内容项
   - **发送通知**: 生成通知消息并输出到日志
3. **更新记录**: 保存最新的内容哈希值到历史文件
4. **输出结果**: 返回所有通知信息和监控摘要

## 数据存储

- **历史记录文件**: `assets/website_monitoring_history.json`
- **存储内容**: 每个网站的内容哈希值、内容项、最后更新时间等

## 扩展说明

### 添加新网站
在GraphInput的`websites`参数中添加新的WebsiteInfo对象：
```json
{
  "name": "网站名称",
  "url": "网站URL",
  "category": "网站分类"
}
```

### 配置邮件通知
在`send_notification_node.py`中取消邮件相关代码的注释，并配置SMTP服务器信息。

### 配置飞书通知
在`send_notification_node.py`中取消飞书相关代码的注释，并配置webhook URL。

## 依赖包
- requests: HTTP请求
- beautifulsoup4: HTML解析
