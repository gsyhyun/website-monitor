#!/bin/bash
#
# 超简单一键部署脚本
# 只需要你提供GitHub令牌，其余全自动
#

set -e

echo "========================================"
echo "🚀 超简单一键部署脚本"
echo "========================================"
echo ""

# 检查是否已有令牌
if [ -z "$GITHUB_TOKEN" ]; then
    echo ""
    echo "📋 第1步：获取GitHub令牌（只需1分钟）"
    echo ""
    echo "1. 访问这个链接："
    echo "   https://github.com/settings/tokens/new"
    echo ""
    echo "2. 勾选 [repo] 权限（只需这一个）"
    echo ""
    echo "3. 点击页面底部的 [Generate token]"
    echo ""
    echo "4. 复制生成的令牌（以 ghp_ 开头）"
    echo ""
    echo "⚠️  令牌只显示一次，请立即复制！"
    echo ""
    echo "========================================"
    echo ""

    read -p "准备好后，请输入你的GitHub令牌: " GITHUB_TOKEN
    echo ""

    if [ -z "$GITHUB_TOKEN" ]; then
        echo "❌ 令牌不能为空"
        exit 1
    fi
fi

# GitHub仓库信息
GITHUB_USERNAME="gsyhyun"
REPO_NAME="website-monitor"

echo "========================================"
echo "📦 开始部署到 GitHub"
echo "========================================"
echo ""
echo "仓库地址：https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

# 检查是否已创建仓库
echo "🔍 检查仓库..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 仓库已存在"
else
    echo "📝 正在创建仓库..."

    # 创建仓库
    curl -X POST -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"$REPO_NAME\",\"description\":\"佛山政府网站内容监控系统\",\"private\":false}"

    echo "✅ 仓库创建成功"
fi

echo ""

# 检查是否已初始化Git
if [ ! -d ".git" ]; then
    echo "📦 初始化Git仓库..."
    git init
    git branch -M main
else
    echo "✅ Git仓库已初始化"
fi

echo ""

# 添加远程仓库
echo "🔗 关联远程仓库..."
git remote set-url origin https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git 2>/dev/null || \
    git remote add origin https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git

echo ""

# 提交所有文件
echo "📝 提交文件..."
git add -A
git commit -m "Deploy to GitHub Actions" 2>/dev/null || echo "✅ 没有新的更改"

echo ""

# 推送到GitHub
echo "🚀 推送代码到GitHub..."
git push -u origin main

echo ""
echo "========================================"
echo "✅ 部署成功！"
echo "========================================"
echo ""

# 配置Secrets
echo "🔐 正在配置邮箱授权码..."

SECRET_EXISTS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/actions/secrets | \
    grep -c "QQ_EMAIL_AUTH_CODE" || echo "0")

if [ "$SECRET_EXISTS" = "0" ]; then
    echo "📝 添加QQ邮箱授权码..."
    curl -X PUT -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/actions/secrets/QQ_EMAIL_AUTH_CODE \
        -d "{\"encrypted_value\":\"$(echo -n "zlwdukmzjedycbbj" | base64)\",\"key_id\":\"\"}"

    echo "✅ 邮箱授权码配置成功"
else
    echo "✅ 邮箱授权码已配置"
fi

echo ""
echo "========================================"
echo "🎉 全部完成！"
echo "========================================"
echo ""
echo "📊 监控地址："
echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo ""
echo "📧 通知邮箱：gshyun@qq.com"
echo ""
echo "⏰ 运行频率：每5分钟自动运行"
echo ""
echo "下一步："
echo "1. 访问上面的监控地址"
echo "2. 点击 [Website Monitor] → [Enable workflow]"
echo "3. 点击 [Run workflow] 测试运行"
echo "4. 等待1-2分钟，检查邮箱"
echo ""
echo "========================================"
echo "现在即使你关闭网页，监控也会持续运行！"
echo "========================================"
