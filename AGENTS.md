## 项目概述
- **名称**: 网站内容监控系统
- **功能**: 监控多个政府网站的更新内容，检测到变化时自动通知

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| fetch_website_node | `nodes/fetch_website_node.py` | task | 抓取网站内容并生成哈希值 | - | - |
| check_changes_node | `nodes/check_changes_node.py` | task | 检测网站内容是否有变化 | - | - |
| send_notification_node | `nodes/send_notification_node.py` | task | 记录通知到文件 | - | - |
| monitor_all_websites | `graph.py` | task | 批量处理所有网站（自动使用默认15个网站或自定义列表） | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 默认网站列表

当不输入任何参数时，系统会自动监控以下15个佛山政府网站：

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

## 集成使用
- 本项目暂未使用外部集成服务
- 通知功能将变化记录保存到 `assets/website_notifications.json` 文件中
- 预留了邮件和飞书消息的集成接口（在send_notification_node.py中）

## 工作流程

1. **主图启动**: 
   - 如果不输入参数，自动使用默认的15个佛山政府网站
   - 如果输入自定义网站列表，使用用户指定的网站
2. **批量处理**: 对所有网站执行以下流程：
   - **抓取内容**: 访问网站URL，提取页面中的标题和链接
   - **生成哈希**: 根据内容生成MD5哈希值
   - **对比检测**: 与历史记录对比，检测是否有变化
   - **提取新增**: 如果有变化，提取新增的内容项
   - **记录通知**: 生成通知消息并保存到文件
3. **更新记录**: 保存最新的内容哈希值到历史文件
4. **输出结果**: 返回所有通知信息和监控摘要

## 数据存储

- **历史记录文件**: `assets/website_monitoring_history.json`
- **通知记录文件**: `assets/website_notifications.json`
- **历史记录内容**: 每个网站的内容哈希值、内容项、最后更新时间等
- **通知记录内容**: 最多保留最近100条通知记录

## 使用方式

### 方式一：使用默认网站列表（推荐）
不输入任何参数，系统自动监控15个佛山政府网站：
```json
{}
```

### 方式二：使用自定义网站列表
输入自定义的网站列表：
```json
{
  "websites": [
    {
      "name": "网站名称",
      "url": "网站URL",
      "category": "网站分类"
    }
  ]
}
```

## 扩展说明

### 添加新网站到默认列表
编辑 `src/graphs/state.py` 中的 `DEFAULT_WEBSITES` 列表，添加新的网站信息。

### 配置邮件通知
在`send_notification_node.py`中取消邮件相关代码的注释，并配置SMTP服务器信息。

### 配置飞书通知
在`send_notification_node.py`中取消飞书相关代码的注释，并配置webhook URL。

## 依赖包
- requests: HTTP请求
- beautifulsoup4: HTML解析

## 技术实现说明

- **默认网站列表**: 使用 Pydantic 的 validator 实现，当输入为空时自动填充默认列表
- **批量处理**: 在单个节点中循环处理所有网站，避免递归限制
- **历史记录**: 基于文件存储，每次运行时更新内容哈希值
- **通知管理**: 通知信息保存到JSON文件，最多保留100条记录
- **错误处理**: 单个网站处理失败不影响其他网站的监控
