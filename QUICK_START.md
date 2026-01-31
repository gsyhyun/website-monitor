# 🚀 GitHub Actions 快速开始

## ⏱️ 5分钟完成部署

### 前置要求

- ✅ GitHub账号
- ✅ QQ邮箱授权码（已配置：zlwdukmzjedycbbj）

---

## 📋 快速部署步骤

### 方法1：使用一键部署脚本（推荐）⭐

```bash
# 1. 给脚本添加执行权限
chmod +x scripts/deploy_to_github.sh

# 2. 运行部署脚本
bash scripts/deploy_to_github.sh

# 3. 按照提示输入GitHub用户名和仓库名称

# 4. 等待上传完成
```

### 方法2：手动部署

```bash
# 1. 初始化Git仓库
git init

# 2. 添加所有文件
git add .

# 3. 提交更改
git commit -m "Initial commit"

# 4. 创建GitHub仓库（访问 https://github.com/new）

# 5. 关联远程仓库
git remote add origin https://github.com/你的用户名/website-monitor.git

# 6. 推送到GitHub
git branch -M main
git push -u origin main
```

---

## 🔐 配置GitHub Secrets（重要！）

### 1. 访问Secrets页面

访问：`https://github.com/你的用户名/website-monitor/settings/secrets/actions`

### 2. 添加QQ邮箱授权码

点击 "New repository secret"，填写：

- **Name**: `QQ_EMAIL_AUTH_CODE`
- **Secret**: `zlwdukmzjedycbbj`
- 点击 "Add secret"

### 3. 完成

Secrets配置完成！🎉

---

## ▶️ 启用GitHub Actions

### 1. 访问Actions页面

访问：`https://github.com/你的用户名/website-monitor/actions`

### 2. 启用工作流

点击 "Website Monitor" → "Enable workflow"

### 3. 测试运行

点击 "Run workflow" → "Run workflow"

---

## 📧 测试邮件通知

### 1. 等待工作流完成

大约1-2分钟后，工作流会完成运行。

### 2. 检查邮箱

访问你的QQ邮箱：gshyun@qq.com

### 3. 查看邮件

你应该会收到一封测试邮件，包含监控结果！

---

## ⏰ 定时运行

GitHub Actions会自动每5分钟运行一次：

- **运行时间**：每小时的0、5、10、15、20、25、30、35、40、45、50、55分钟
- **示例**：10:00, 10:05, 10:10, 10:15, ...

---

## 📊 查看监控状态

### 查看运行日志

访问：`https://github.com/你的用户名/website-monitor/actions`

### 下载日志文件

1. 在Actions页面找到运行的工作流
2. 在最下方找到 "Artifacts"
3. 下载 "logs" 压缩包

---

## 🔧 修改配置

### 修改监控间隔

编辑 `.github/workflows/monitor.yml`：

```yaml
schedule:
  - cron: '*/5 * * * *'  # 每5分钟
  # - cron: '*/10 * * * *'  # 每10分钟
  # - cron: '0 * * * *'  # 每小时
```

### 修改邮箱地址

编辑 `.github/workflows/monitor.yml`：

```yaml
env:
  QQ_EMAIL_ACCOUNT: gshyun@qq.com  # 修改为你的邮箱
```

---

## ⚠️ 常见问题

### Q1: 为什么没有收到邮件？

**解决方案**：
1. 检查垃圾邮件文件夹
2. 检查GitHub Secrets是否配置正确
3. 查看GitHub Actions日志

### Q2: 工作流运行失败？

**解决方案**：
1. 查看GitHub Actions日志
2. 检查代码语法
3. 确认依赖已正确安装

### Q3: 如何修改监控网站？

**解决方案**：
编辑 `src/graphs/state.py` 中的 `DEFAULT_WEBSITES` 列表

---

## 🎉 完成！

恭喜！你的监控系统已经成功部署到GitHub Actions！

即使你的电脑离线，监控系统也会持续工作，每5分钟自动监控佛山政府网站，并发送邮件通知！

---

## 📞 需要帮助？

查看详细文档：[GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)
