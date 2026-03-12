#!/bin/bash

# 工程师知识系统 - 恢复脚本
# 从备份恢复 Git 仓库和 Docker 卷数据

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKUP_DIR="${BACKUP_DIR:-./backups}"

echo "=========================================="
echo "工程师知识系统 - 恢复"
echo "=========================================="
echo ""

# 检查备份目录
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}✗ 备份目录不存在: $BACKUP_DIR${NC}"
    exit 1
fi

# 列出可用的备份
echo -e "${BLUE}可用的备份:${NC}"
echo ""

backups=($(ls -1 "$BACKUP_DIR"/*.bundle 2>/dev/null | xargs -n 1 basename | sed 's/.bundle$//' | sort -r))

if [ ${#backups[@]} -eq 0 ]; then
    echo -e "${RED}✗ 未找到备份文件${NC}"
    exit 1
fi

# 显示备份列表
for i in "${!backups[@]}"; do
    backup_name="${backups[$i]}"
    backup_date=$(echo "$backup_name" | grep -oP '\d{8}_\d{6}' | sed 's/_/ /')
    echo "  $((i+1)). $backup_name"
    echo "     日期: $backup_date"
    
    # 显示备份文件大小
    bundle_file="$BACKUP_DIR/${backup_name}.bundle"
    if [ -f "$bundle_file" ]; then
        size=$(du -h "$bundle_file" | cut -f1)
        echo "     大小: $size"
    fi
    echo ""
done

# 选择备份
echo -n "请选择要恢复的备份编号 (1-${#backups[@]}): "
read -r selection

if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#backups[@]} ]; then
    echo -e "${RED}✗ 无效的选择${NC}"
    exit 1
fi

BACKUP_NAME="${backups[$((selection-1))]}"
echo ""
echo -e "${GREEN}选择的备份: $BACKUP_NAME${NC}"
echo ""

# 确认恢复
echo -e "${YELLOW}警告: 恢复操作将覆盖现有数据！${NC}"
echo -n "确认继续? (yes/no): "
read -r confirm

if [ "$confirm" != "yes" ]; then
    echo "恢复已取消"
    exit 0
fi

echo ""

# 1. 恢复 Git 仓库
echo -e "${BLUE}1. 恢复 Git 仓库...${NC}"
BUNDLE_FILE="$BACKUP_DIR/${BACKUP_NAME}.bundle"

if [ -f "$BUNDLE_FILE" ]; then
    # 检查是否已有 Git 仓库
    if [ -d .git ]; then
        echo -e "${YELLOW}⚠ 现有 Git 仓库将被备份到 .git.backup${NC}"
        mv .git .git.backup
    fi
    
    # 从 bundle 恢复
    git clone "$BUNDLE_FILE" temp_restore
    mv temp_restore/.git .git
    rm -rf temp_restore
    
    # 检出文件
    git reset --hard HEAD
    
    echo -e "${GREEN}✓ Git 仓库恢复成功${NC}"
else
    echo -e "${RED}✗ Bundle 文件不存在: $BUNDLE_FILE${NC}"
    exit 1
fi
echo ""

# 2. 恢复 Docker 卷
echo -e "${BLUE}2. 恢复 Docker 卷...${NC}"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker 未运行${NC}"
    exit 1
fi

# 停止服务
echo "  停止 Docker 服务..."
docker compose down 2>/dev/null || true

# 恢复函数
restore_volume() {
    local volume_name=$1
    local backup_file="$BACKUP_DIR/${BACKUP_NAME}-${volume_name}.tar.gz"
    
    echo -n "  恢复 $volume_name... "
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${YELLOW}⚠ 备份文件不存在，跳过${NC}"
        return 1
    fi
    
    # 删除现有卷（如果存在）
    docker volume rm "$volume_name" 2>/dev/null || true
    
    # 创建新卷
    docker volume create "$volume_name" > /dev/null
    
    # 恢复数据
    if docker run --rm \
        -v "${volume_name}:/data" \
        -v "$(pwd)/$BACKUP_DIR:/backup" \
        alpine \
        sh -c "cd /data && tar -xzf /backup/$(basename $backup_file)" > /dev/null 2>&1; then
        
        echo -e "${GREEN}✓${NC}"
        return 0
    fi
    
    echo -e "${RED}✗ 失败${NC}"
    return 1
}

# 获取项目名称
PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')

# 恢复各个卷
volumes=(
    "${PROJECT_NAME}_gitea-data"
    "${PROJECT_NAME}_wiki-data"
    "${PROJECT_NAME}_db-data"
    "${PROJECT_NAME}_qdrant-data"
    "${PROJECT_NAME}_ai-cache"
    "${PROJECT_NAME}_mkdocs-site"
)

restore_success=0
restore_failed=0

for volume in "${volumes[@]}"; do
    if restore_volume "$volume"; then
        restore_success=$((restore_success + 1))
    else
        restore_failed=$((restore_failed + 1))
    fi
done

echo ""
echo -e "${GREEN}✓ 成功恢复 $restore_success 个卷${NC}"
if [ $restore_failed -gt 0 ]; then
    echo -e "${YELLOW}⚠ 跳过 $restore_failed 个卷${NC}"
fi
echo ""

# 3. 恢复配置文件
echo -e "${BLUE}3. 恢复配置文件...${NC}"
CONFIG_BACKUP="$BACKUP_DIR/${BACKUP_NAME}-config.tar.gz"

if [ -f "$CONFIG_BACKUP" ]; then
    # 备份现有配置
    if [ -f .env ]; then
        cp .env .env.backup
        echo "  现有 .env 已备份到 .env.backup"
    fi
    
    # 恢复配置
    tar -xzf "$CONFIG_BACKUP" 2>/dev/null || true
    echo -e "${GREEN}✓ 配置文件恢复成功${NC}"
else
    echo -e "${YELLOW}⚠ 配置备份文件不存在，跳过${NC}"
fi
echo ""

# 4. 重启服务
echo -e "${BLUE}4. 重启 Docker 服务...${NC}"
docker compose up -d

echo -e "${GREEN}✓ 服务启动完成${NC}"
echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 10

echo "=========================================="
echo -e "${GREEN}恢复完成！${NC}"
echo "=========================================="
echo ""
echo "恢复的备份: $BACKUP_NAME"
echo ""
echo "服务访问地址:"
echo "  - Gitea:          http://localhost:3001"
echo "  - Wiki.js:        http://localhost:3000"
echo "  - AI Assistant:   http://localhost:3003"
echo "  - MkDocs:         http://localhost:3002"
echo ""
echo "下一步:"
echo "  1. 检查服务状态: docker compose ps"
echo "  2. 查看日志: docker compose logs -f"
echo "  3. 验证数据完整性"
echo ""
