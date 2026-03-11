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

# 检查服务状态
echo -e "${BLUE}检查服务状态...${NC}"
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
echo "  - AI Assistant:   http://localhost:8000"
echo "  - MkDocs:         http://localhost:8080"
echo "  - Webhook:        http://localhost:9000"
echo ""
echo "下一步："
echo "  1. 访问 Gitea (http://localhost:3001) 完成初始设置"
echo "  2. 创建管理员账户"
echo "  3. 创建仓库: knowledge-system"
echo "  4. 配置 Webhook:"
echo "     URL: http://webhook-handler:9000/hooks/knowledge-sync"
echo "     Secret: (使用 .env 中的 WEBHOOK_SECRET)"
echo "  5. 访问 Wiki.js (http://localhost:3000) 完成初始设置"
echo "  6. 配置 Git Storage 指向 Gitea 仓库"
echo ""
echo "查看日志："
echo "  docker compose logs -f"
echo ""
echo "停止服务："
echo "  docker compose down"
echo ""
