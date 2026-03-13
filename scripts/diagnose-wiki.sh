#!/bin/bash
# Wiki.js 诊断脚本

echo "=========================================="
echo "Wiki.js 诊断报告"
echo "=========================================="
echo ""

echo "1. 检查 Wiki.js 容器状态..."
docker ps | grep knowledge-wiki
echo ""

echo "2. 检查 Wiki.js repo 目录..."
docker exec knowledge-wiki ls -la /wiki/repo
echo ""

echo "3. 检查 Wiki.js data 目录..."
docker exec knowledge-wiki ls -la /wiki/data
echo ""

echo "4. 检查最近的 Wiki.js 日志..."
docker logs knowledge-wiki --tail 20
echo ""

echo "=========================================="
echo "可能的问题："
echo "=========================================="
echo ""
echo "1. Git Storage 未配置"
echo "   解决方案：在 Wiki.js 管理界面配置 Git Storage"
echo "   路径：Administration → Storage → Git"
echo ""
echo "2. Git 仓库路径配置错误"
echo "   检查：Repository URL 应该是 http://gitea:3000/admin/knowledge-system.git"
echo ""
echo "3. 认证失败"
echo "   检查：Username 和 Password 是否正确"
echo ""
echo "4. 同步方向错误"
echo "   检查：Sync Direction 应该是 'Sync ← Remote (Pull)'"
echo ""

echo "=========================================="
echo "手动配置步骤："
echo "=========================================="
echo ""
echo "1. 访问 http://localhost:3000"
echo "2. 登录后点击右上角头像 → Administration"
echo "3. 左侧菜单选择 Storage"
echo "4. 找到 Git 并点击"
echo "5. 配置如下："
echo "   - Authentication Type: Basic"
echo "   - Repository URL: http://gitea:3000/admin/knowledge-system.git"
echo "   - Branch: main"
echo "   - Username: admin"
echo "   - Password: [你的 Gitea 密码]"
echo "   - Local Repository Path: /wiki/data/repo"
echo "   - Sync Direction: Sync ← Remote (Pull)"
echo "   - Sync Interval: PT5M"
echo "6. 点击 Apply"
echo "7. 点击 Execute Sync 测试同步"
echo ""
