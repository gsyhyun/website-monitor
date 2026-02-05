# 🎉 部署完成90%！

## ✅ 已完成的步骤

1. ✅ 创建GitHub仓库：https://github.com/gsyhyun/website-monitor
2. ✅ 推送所有代码到GitHub
3. ✅ 配置邮箱授权码Secret

---

## 📋 最后一步：添加 GitHub Actions Workflow

由于GitHub的安全限制，需要你手动添加workflow文件。只需**30秒**！

### 操作步骤：

1. **点击这个链接**打开GitHub编辑器：
   https://github.com/gsyhyun/website-monitor/new/main

2. **创建文件夹**：
   - 在文件名输入框中输入：`.github/workflows/monitor.yml`
   - （系统会自动创建文件夹）

3. **复制并粘贴以下内容**：

```yaml
name: Website Monitor

on:
  schedule:
    # 每5分钟运行一次
    - cron: '*/5 * * * *'
  
  # 允许手动触发
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-github.txt
      
      - name: Run monitor
        env:
          QQ_EMAIL_AUTH_CODE: ${{ secrets.QQ_EMAIL_AUTH_CODE }}
        run: |
          python scripts/periodic_monitor.py
      
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: logs
          path: /app/work/logs/bypass/
          retention-days: 30
```

4. **滚动到页面底部**，点击绿色按钮：
   ```
   Commit changes...
   ```

5. 选择：
   - `Commit directly to the main branch`
   - 点击绿色按钮：`Commit changes`

---

## 🚀 启用监控

添加workflow文件后：

1. 访问：https://github.com/gsyhyun/website-monitor/actions
2. 点击 "Website Monitor" 工作流
3. 点击 "Enable workflow" 按钮
4. 点击 "Run workflow" 按钮进行测试

---

## 📧 测试邮箱通知

等待1-2分钟后，检查邮箱 `gshyun@qq.com`，你应该会收到测试邮件！

---

## ⏰ 自动运行

启用后，GitHub Actions会每5分钟自动运行：
```
运行时间示例：
10:00, 10:05, 10:10, 10:15, ...
```

---

## 📊 查看运行状态

访问：https://github.com/gsyhyun/website-monitor/actions

可以看到：
- 每次运行的记录
- 运行日志
- 成功/失败状态

---

## 🎉 完成！

添加workflow文件后，你的监控系统就会：
- ✅ 每5分钟自动运行
- ✅ 监控15个佛山政府网站
- ✅ 检测新内容并发送邮件通知
- ✅ 24/7持续运行（即使你关闭浏览器）

---

需要帮助吗？请告诉我！
