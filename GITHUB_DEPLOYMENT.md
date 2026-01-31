# GitHub Actions 部署指南

## 📝 部署步骤

### 1. 创建GitHub仓库

1. 访问 https://github.com
2. 点击右上角的 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `website-monitor`（或其他名称）
   - Description: 佛山政府网站监控系统
   - 选择 "Public" 或 "Private"（建议选择Private）
4. 点击 "Create repository"

### 2. 上传代码

#### 方法1：使用GitHub网页界面上传

1. 在新创建的仓库中，点击 "uploading an existing file"
2. 将以下文件拖拽到上传区域：
   - `src/` 目录（所有源代码）
   - `scripts/` 目录（所有脚本）
   - `config/` 目录（所有配置）
   - `assets/` 目录（可以不上传，首次运行会自动创建）
   - `requirements-github.txt`（依赖文件）
   - `.github/workflows/monitor.yml`（GitHub Actions配置）
   - `.coze`（配置文件）

3. 在底部输入提交信息："Initial commit"
4. 点击 "Commit changes"

#### 方法2：使用Git命令行上传

```bash
# 在项目根目录初始化Git仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit"

# 关联GitHub仓库
git remote add origin https://github.com/你的用户名/website-monitor.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 3. 配置GitHub Secrets（重要！）

1. 在你的GitHub仓库页面，点击 "Settings"
2. 左侧菜单点击 "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 添加以下Secret：

| Name | Secret | 说明 |
|------|--------|------|
| QQ_EMAIL_AUTH_CODE | `zlwdukmzjedycbbj` | QQ邮箱授权码 |

5. 点击 "Add secret"

### 4. 启用GitHub Actions

1. 点击 "Actions" 标签
2. 你会看到 "Website Monitor" 工作流
3. 点击 "Enable workflow"（如果是首次）

### 5. 测试运行

1. 在Actions页面，点击 "Website Monitor"
2. 点击 "Run workflow" → "Run workflow"
3. 等待几分钟，查看运行结果

### 6. 查看日志

1. 在Actions页面，点击运行的工作流
2. 点击 "monitor" job
3. 可以看到详细的运行日志

## ⏰ 定时运行说明

GitHub Actions会按照以下时间表自动运行：

- **运行频率**：每5分钟
- **运行时间**：整点的第0、5、10、15、20、25、30、35、40、45、50、55分钟
- **示例**：10:00, 10:05, 10:10, 10:15, ...

## 📊 监控结果

### 查看邮件通知

- 邮件会自动发送到：gshyun@qq.com
- 包含：网站名称、URL、新增内容列表

### 查看运行日志

1. 访问GitHub仓库的Actions页面
2. 点击最新的工作流运行记录
3. 查看详细日志

### 下载日志文件

1. 在Actions页面，找到运行的工作流
2. 在最下方找到 "Artifacts"
3. 下载 "logs" 压缩包

## 🔧 修改监控配置

### 修改监控间隔

编辑 `.github/workflows/monitor.yml` 文件：

```yaml
schedule:
  - cron: '*/5 * * * *'  # 每5分钟
  # - cron: '*/10 * * * *'  # 每10分钟
  # - cron: '0 * * * *'  # 每小时
```

### 修改监控网站

编辑 `src/graphs/state.py` 文件中的 `DEFAULT_WEBSITES` 列表。

### 修改邮箱地址

编辑 `.github/workflows/monitor.yml` 文件中的环境变量：

```yaml
env:
  QQ_EMAIL_ACCOUNT: gshyun@qq.com  # 修改为你的邮箱
```

## ⚠️ 注意事项

### GitHub Actions 限制

- **免费版**：每月2000分钟运行时间
- **最小间隔**：5分钟
- **最大并发**：20个并发任务

### 邮箱限制

- QQ邮箱可能对频繁发送邮件有限制
- 建议监控间隔不要太短（至少5分钟）
- 如果邮件发送失败，检查垃圾邮件文件夹

### 代码更新

每次修改代码后，需要提交并推送到GitHub：
```bash
git add .
git commit -m "Update monitor"
git push
```

## 🚀 优化建议

### 1. 添加错误通知

可以在GitHub Actions中添加失败时的通知：

```yaml
- name: Send notification on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: '网站监控运行失败！'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 2. 优化日志

添加日志压缩和清理：

```yaml
- name: Clean old logs
  run: |
    find logs/ -type f -name "*.log" -mtime +7 -delete
```

### 3. 添加健康检查

创建一个健康检查接口，定期验证服务状态。

## 📞 获取帮助

如果遇到问题：

1. 查看GitHub Actions文档：https://docs.github.com/en/actions
2. 查看工作流日志
3. 检查代码语法
4. 验证GitHub Secrets配置

## 🎉 完成！

现在你的监控系统已经部署到GitHub Actions，可以24/7免费运行了！

即使你的电脑离线，监控系统也会持续工作，每5分钟自动监控佛山政府网站，并发送邮件通知！
