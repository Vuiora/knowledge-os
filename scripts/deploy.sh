#!/bin/bash

# 工程师知识系统 - 部署脚本

set -e

echo "=========================================="
echo "工程师知识系统 - 部署"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Docker
echo -e "${BLUE}检查 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker 已安装${NC}"

if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose 已安装${NC}"
echo ""

# 检查 .env 文件
echo -e "${BLUE}检查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env 文件不存在${NC}"
    echo "正在从 .env.example 创建..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ 请编辑 .env 文件设置密码和 API 密钥${NC}"
    exit 1
fi
echo -e "${GREEN}✓ .env 文件存在${NC}"
echo ""

# 检查目录结构
echo -e "${BLUE}检查目录结构...${NC}"
if [ ! -d "knowledge" ]; then
    echo -e "${YELLOW}⚠ knowledge/ 目录不存在，正在创建...${NC}"
    bash scripts/init.sh
fi
echo -e "${GREEN}✓ 目录结构完整${NC}"
echo ""

# 停止现有服务
echo -e "${BLUE}停止现有服务...${NC}"
docker compose down 2>/dev/null || true
echo -e "${GREEN}✓ 现有服务已停止${NC}"
echo ""

# 构建镜像
echo -e "${BLUE}构建 Docker 镜像...${NC}"
docker compose build
echo -e "${GREEN}✓ 镜像构建完成${NC}"
echo ""

# 启动服务
echo -e "${BLUE}启动服务...${NC}"
docker compose up -d
echo -e "${GREEN}✓ 服务启动完成${NC}"
echo ""

# 等待服务启动
echo -e "${BLUE}等待服务启动...${NC}"
sleep 10

# 健康检查函数
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "  检查 $service_name... "
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$health_url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 运行中${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo -e "${RED}✗ 超时${NC}"
    return 1
}

# 检查各服务健康状态
echo -e "${BLUE}检查服务健康状态...${NC}"

# 检查 Gitea
check_service_health "Gitea" "http://localhost:3001" || echo -e "${YELLOW}  提示：Gitea 可能需要更长时间启动${NC}"

# 检查 Wiki.js
check_service_health "Wiki.js" "http://localhost:3000" || echo -e "${YELLOW}  提示：Wiki.js 可能需要更长时间启动${NC}"

# 检查 AI Assistant
check_service_health "AI Assistant" "http://localhost:3003/health" || echo -e "${YELLOW}  提示：AI Assistant 可能需要更长时间启动${NC}"

# 检查 MkDocs
check_service_health "MkDocs" "http://localhost:3002" || echo -e "${YELLOW}  提示：MkDocs 可能需要更长时间启动${NC}"

# 检查 Webhook Handler
check_service_health "Webhook Handler" "http://localhost:9000/health" || echo -e "${YELLOW}  提示：Webhook Handler 可能需要更长时间启动${NC}"

echo ""

# 检查服务状态
echo -e "${BLUE}Docker 容器状态：${NC}"
docker compose ps
echo ""

# 显示访问信息
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "服务访问地址："
echo "  - Gitea:          http://localhost:3001"
echo "  - Wiki.js:        http://localhost:3000"
echo "  - AI Assistant:   http://localhost:3003"
echo "  - MkDocs:         http://localhost:3002"
echo "  - Webhook:        http://localhost:9000"
echo ""

# 初始配置向导
echo "=========================================="
echo -e "${BLUE}初始配置向导${NC}"
echo "=========================================="
echo ""
echo "请按照以下步骤完成初始配置："
echo ""
echo -e "${YELLOW}步骤 1: 配置 Gitea${NC}"
echo "  1. 访问 http://localhost:3001"
echo "  2. 完成初始安装向导"
echo "  3. 创建管理员账户（建议使用 .env 中的 GITEA_USER）"
echo "  4. 登录后，创建新仓库: knowledge-system"
echo "  5. 在用户设置中生成 API Token，更新到 .env 的 GITEA_TOKEN"
echo ""
echo -e "${YELLOW}步骤 2: 配置 Git 远程仓库${NC}"
echo "  在项目目录执行："
echo "    git remote add origin http://localhost:3001/admin/knowledge-system.git"
echo "    git add ."
echo "    git commit -m 'Initial commit'"
echo "    git push -u origin main"
echo ""
echo -e "${YELLOW}步骤 3: 配置 Gitea Webhook${NC}"
echo "  1. 在 Gitea 仓库页面，进入 Settings > Webhooks"
echo "  2. 点击 'Add Webhook' > 'Gitea'"
echo "  3. 配置："
echo "     - Target URL: http://webhook-handler:9000/hooks/knowledge-sync"
echo "     - HTTP Method: POST"
echo "     - POST Content Type: application/json"
echo "     - Secret: (使用 .env 中的 WEBHOOK_SECRET)"
echo "     - Trigger On: Push events"
echo "  4. 点击 'Add Webhook'"
echo ""
echo -e "${YELLOW}步骤 4: 配置 Wiki.js${NC}"
echo "  1. 访问 http://localhost:3000"
echo "  2. 完成初始安装向导"
echo "  3. 创建管理员账户"
echo "  4. 进入 Administration > Storage"
echo "  5. 配置 Git Storage:"
echo "     - Authentication Type: Basic"
echo "     - Repository URL: http://gitea:3000/admin/knowledge-system.git"
echo "     - Branch: main"
echo "     - Username: admin (或您的 Gitea 用户名)"
echo "     - Password: (您的 Gitea 密码)"
echo "     - Local Repository Path: ./data/repo"
echo "     - Sync Direction: Bi-directional"
echo "     - Sync Interval: 5 minutes"
echo "  6. 点击 'Apply' 并等待首次同步完成"
echo "  7. 在 Administration > API 中生成 API Key，更新到 .env 的 WIKI_TOKEN"
echo ""
echo -e "${YELLOW}步骤 5: 配置 Obsidian${NC}"
echo "  1. 打开 Obsidian"
echo "  2. 选择 'Open folder as vault'"
echo "  3. 选择项目的 knowledge/ 目录"
echo "  4. 安装 Obsidian Git 插件（Community Plugins）"
echo "  5. 配置插件："
echo "     - Vault backup interval: 10 (分钟)"
echo "     - Auto pull interval: 10 (分钟)"
echo "     - Commit message: vault backup: {{date}}"
echo "  6. 开始创建和编辑知识文档！"
echo ""
echo -e "${YELLOW}步骤 6: 测试自动同步${NC}"
echo "  1. 在 Obsidian 中创建一个测试文档"
echo "  2. 等待自动提交（或手动提交：Ctrl+P > Obsidian Git: Commit and push）"
echo "  3. 检查 Gitea 是否收到提交"
echo "  4. 等待 5 分钟，检查 Wiki.js 是否显示新文档"
echo "  5. 检查 AI 助手是否索引了新文档："
echo "     curl http://localhost:3003/api/search?q=测试"
echo ""
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 按照上述步骤完成初始配置"
echo "  2. 运行验证脚本: bash scripts/verify-git-sync.sh"
echo ""
echo "查看日志："
echo "  docker compose logs -f"
echo ""
echo "停止服务："
echo "  docker compose down"
echo ""
