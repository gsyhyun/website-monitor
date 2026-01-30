## 项目概述
- **名称**: 网站内容监控系统
- **功能**: 监控多个政府网站的更新内容，检测到变化时自动通知

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| fetch_website_node | `nodes/fetch_website_node.py` | task | 抓取网站内容并生成哈希值 | - | - |
| check_changes_node | `nodes/check_changes_node.py` | task | 检测网站内容是否有变化 | - | - |
| send_notification_node | `nodes/send_notification_node.py` | task | 记录通知并发送邮件 | - | - |
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
- **邮件集成**: 使用邮件集成服务实现通知功能，需要配置邮件凭证
  - 邮件配置通过环境变量自动读取
  - 支持在启动时指定接收通知的邮箱地址
  - 未配置邮箱时，通知仅保存到本地文件
- 通知功能将变化记录保存到 `assets/website_notifications.json` 文件中

## 工作流程

1. **主图启动**:
   - 如果不输入参数，自动使用默认的15个佛山政府网站
   - 如果输入自定义网站列表，使用用户指定的网站
   - 支持配置邮箱地址接收通知
2. **批量处理**: 对所有网站执行以下流程：
   - **抓取内容**: 访问网站URL，提取页面中的标题和链接
   - **生成哈希**: 根据内容生成MD5哈希值
   - **对比检测**: 与历史记录对比，检测是否有变化
   - **提取新增**: 如果有变化，提取新增的内容项
   - **记录通知**: 生成通知消息并保存到文件
   - **发送邮件**: 如果配置了邮箱地址，发送邮件通知
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

### 方式三：配置邮件通知
提供邮箱地址，接收更新通知：
```json
{
  "email_address": "your_email@example.com"
}
```

### 方式四：定期执行（每5分钟）
使用定期执行脚本自动监控：
```bash
# 不配置邮件
python scripts/periodic_monitor.py

# 配置邮件通知
python scripts/periodic_monitor.py --email your_email@example.com

# 自定义监控间隔（例如每10分钟）
python scripts/periodic_monitor.py --interval 10 --email your_email@example.com
```

**定期执行说明**：
- 脚本会每5分钟自动运行一次监控
- 检测到网站更新时会发送邮件通知（如果配置了邮箱地址）
- 按 Ctrl+C 停止脚本
- 日志会保存到 `logs/monitoring.log` 文件中

## 扩展说明

### 添加新网站到默认列表
编辑 `src/graphs/state.py` 中的 `DEFAULT_WEBSITES` 列表，添加新的网站信息。

### 配置邮件通知
系统已集成邮件服务，使用方式如下：

1. **配置邮件凭证**（环境变量）：
   - 在运行环境中配置邮件服务器的 SMTP 信息
   - 包括：SMTP 服务器、端口、邮箱账号、授权码
   - 系统会自动从环境变量读取这些信息

2. **启动监控时指定邮箱**：
   ```bash
   # 使用定期执行脚本
   python scripts/periodic_monitor.py --email your_email@example.com

   # 或者在工作流调用时传入
   {
     "email_address": "your_email@example.com"
   }
   ```

3. **邮件内容**：
   - 主题：`【网站更新】{网站名称} 检测到新内容`
   - 内容：包含网站名称、URL、检测时间、新增内容列表

### 配置飞书通知
在`send_notification_node.py`中取消飞书相关代码的注释，并配置webhook URL。

## 定期监控

### 脚本说明
- **文件位置**: `scripts/periodic_monitor.py`
- **功能**: 自动定期监控网站更新，并发送邮件通知
- **日志**: 运行日志保存在 `logs/monitoring.log`

### 使用方法

1. **基础使用（每5分钟）**:
   ```bash
   python scripts/periodic_monitor.py
   ```

2. **配置邮件通知**:
   ```bash
   python scripts/periodic_monitor.py --email your_email@example.com
   ```

3. **自定义监控间隔**:
   ```bash
   # 每10分钟监控一次
   python scripts/periodic_monitor.py --interval 10

   # 每30分钟监控一次，并发送邮件
   python scripts/periodic_monitor.py --interval 30 --email your_email@example.com
   ```

4. **后台运行**:
   ```bash
   # Linux/Mac
   nohup python scripts/periodic_monitor.py --email your_email@example.com > logs/monitor.out 2>&1 &

   # Windows (PowerShell)
   Start-Process -FilePath "python" -ArgumentList "scripts/periodic_monitor.py", "--email", "your_email@example.com" -WindowStyle Hidden
   ```

5. **停止监控**:
   - 在终端中按 `Ctrl+C`
   - 或者查找并终止进程：`ps aux | grep periodic_monitor.py` 然后 `kill <PID>`

### 日志监控
实时查看日志：
```bash
# 查看最新日志
tail -f logs/monitor.out

# 查看包含"更新"的日志
grep "更新" logs/monitor.out

# 查看包含"错误"的日志
grep "错误" logs/monitor.out
```

### 监控管理脚本

系统提供了便捷的监控管理脚本：

#### 1. 启动监控服务
```bash
# 使用默认配置启动（每5分钟监控一次）
bash scripts/start_monitor.sh

# 指定邮箱启动
bash scripts/start_monitor.sh --email your_email@example.com

# 指定监控间隔（例如每10分钟）
bash scripts/start_monitor.sh --interval 10 --email your_email@example.com
```

#### 2. 停止监控服务
```bash
bash scripts/stop_monitor.sh
```

#### 3. 查看监控动态（实时）⭐ 推荐
```bash
# 实时监控动态（持续刷新显示）
bash scripts/monitor_live.sh
```

**功能说明**：
- 显示监控进程状态（运行中/已停止）
- 显示运行时长、CPU和内存使用率
- 显示最新监控摘要
- 显示下次运行时间
- 显示通知统计信息
- 每3秒自动刷新，按 Ctrl+C 退出

#### 4. 查看当前状态（一次性）
```bash
# 显示当前状态摘要
bash scripts/show_status.sh
```

**显示内容**：
- 监控服务运行状态
- 最新监控结果
- 最新通知记录

#### 5. 快速查看动态（推荐）⭐⭐⭐
```bash
# 快速查看当前状态和最新动态（适合预览区域）
bash scripts/quick_status.sh
```

**功能说明**：
- 带彩色输出，更直观
- 显示监控进程状态（运行中/已停止）
- 显示运行时长、CPU和内存使用率
- 显示最新监控摘要
- 显示下次运行时间
- 显示通知统计信息（总数、今日新增）
- 显示最新2条通知详情
- **适合在预览区域快速查看**

### 实时监控动态示例

运行 `bash scripts/monitor_live.sh` 后，会显示类似以下内容：

```
======================================
网站监控系统 - 实时监控
======================================
更新时间: 2025-01-10 14:30:25

【进程状态】
✅ 监控服务: 运行中 (PID: 12345)
   运行时长: 01:23:45
   CPU使用率: 0.5%
   内存使用: 0.8%

【最新监控摘要】
监控完成:
时间: 2025-01-10 14:30:00
监控网站数: 15
检测到变化: 2个网站

【下次运行】
下次运行时间: 2025-01-10 14:35:00

【通知统计】
总通知数: 5 条
今日新增: 3 条
最新: "website_name": "佛山自然资源局"

【最新通知】
- 佛山自然资源局-批后
  新增: 2项
  时间: 2025-01-10 14:30:00
  
- 佛山自然资源局-通知公告
  新增: 1项
  时间: 2025-01-10 14:25:00

======================================
按 Ctrl+C 退出 | 每3秒自动刷新
======================================
```

## 依赖包
- requests: HTTP请求
- beautifulsoup4: HTML解析
- coze_workload_identity: 工作负载身份管理（获取邮件配置）
- cozeloop: 邮件集成装饰器

## 技术实现说明

- **默认网站列表**: 使用 Pydantic 的 validator 实现，当输入为空时自动填充默认列表
- **批量处理**: 在单个节点中循环处理所有网站，避免递归限制
- **历史记录**: 基于文件存储，每次运行时更新内容哈希值
- **通知管理**: 通知信息保存到JSON文件，最多保留100条记录
- **邮件通知**: 集成邮件服务，支持SSL加密、重试机制、错误处理
- **定期执行**: 提供定期执行脚本，支持自定义监控间隔和邮箱配置
- **错误处理**: 单个网站处理失败不影响其他网站的监控
