#!/bin/bash
#
# GitHub Actions 一键部署脚本
# 将监控系统部署到GitHub Actions
#

set -e

echo "======================================"
echo "GitHub Actions 一键部署脚本"
echo "======================================"
echo ""

# 检查是否已初始化Git仓库
if [ -d ".git" ]; then
    echo "⚠️  检测到已存在的Git仓库"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi
fi

# 询问GitHub仓库信息
echo "请输入GitHub仓库信息："
read -p "GitHub用户名: " GITHUB_USERNAME
read -p "仓库名称 (默认: website-monitor): " REPO_NAME
REPO_NAME=${REPO_NAME:-website-monitor}

echo ""
echo "======================================"
echo "部署信息"
echo "======================================"
echo "GitHub用户名: $GITHUB_USERNAME"
echo "仓库名称: $REPO_NAME"
echo "仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo "======================================"
echo ""

read -p "确认部署？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "部署已取消"
    exit 0
fi

# 初始化Git仓库
echo "1️⃣ 初始化Git仓库..."
git init

# 添加所有文件
echo "2️⃣ 添加文件..."
git add .

# 提交更改
echo "3️⃣ 提交更改..."
git commit -m "Deploy website monitor to GitHub Actions"

# 添加远程仓库
echo "4️⃣ 关联远程仓库..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# 推送到GitHub
echo "5️⃣ 推送到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "======================================"
echo "✅ 部署成功！"
echo "======================================"
echo ""
echo "下一步操作："
echo ""
echo "1️⃣  配置GitHub Secrets："
echo "   访问: https://github.com/$GITHUB_USERNAME/$REPO_NAME/settings/secrets/actions"
echo "   添加Secret: QQ_EMAIL_AUTH_CODE = zlwdukmzjedycbbj"
echo ""
echo "2️⃣  启用GitHub Actions："
echo "   访问: https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo "   点击 'Enable workflow'"
echo ""
echo "3️⃣  测试运行："
echo "   在Actions页面点击 'Run workflow'"
echo ""
echo "4️⃣  查看日志："
echo "   访问: https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo ""
echo "======================================"
echo "现在你的监控系统已经部署到GitHub Actions了！"
echo "每5分钟会自动运行，并发送邮件到 gshyun@qq.com"
echo "======================================"
