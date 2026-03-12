#!/bin/bash

# 工程师知识系统 - 备份脚本
# 备份 Git 仓库和 Docker 卷数据

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="knowledge-system-backup-${TIMESTAMP}"

echo "=========================================="
echo "工程师知识系统 - 备份"
echo "=========================================="
echo ""
echo "备份时间: $(date)"
echo "备份目录: $BACKUP_DIR"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 1. 备份 Git 仓库（最重要）
echo -e "${BLUE}1. 备份 Git 仓库...${NC}"
if [ -d .git ]; then
    BUNDLE_FILE="$BACKUP_DIR/${BACKUP_NAME}.bundle"
    git bundle create "$BUNDLE_FILE" --all
    
    if [ -f "$BUNDLE_FILE" ]; then
        BUNDLE_SIZE=$(du -h "$BUNDLE_FILE" | cut -f1)
        echo -e "${GREEN}✓ Git bundle 创建成功: $BUNDLE_FILE ($BUNDLE_SIZE)${NC}"
    else
        echo -e "${RED}✗ Git bundle 创建失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Git 仓库不存在，跳过${NC}"
fi
echo ""

# 2. 备份 Docker 卷
echo -e "${BLUE}2. 备份 Docker 卷...${NC}"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker 未运行${NC}"
    exit 1
fi

# 备份函数
backup_volume() {
    local volume_name=$1
    local backup_file="$BACKUP_DIR/${BACKUP_NAME}-${volume_name}.tar.gz"
    
    echo -n "  备份 $volume_name... "
    
    # 使用临时容器备份卷
    if docker run --rm \
        -v "${volume_name}:/data" \
        -v "$(pwd)/$BACKUP_DIR:/backup" \
        alpine \
        tar -czf "/backup/$(basename $backup_file)" -C /data . > /dev/null 2>&1; then
        
        if [ -f "$backup_file" ]; then
            local size=$(du -h "$backup_file" | cut -f1)
            echo -e "${GREEN}✓ ($size)${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}✗ 失败${NC}"
    return 1
}

# 获取项目名称（从 docker-compose.yml 或使用默认值）
PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')

# 备份各个卷
volumes=(
    "${PROJECT_NAME}_gitea-data"
    "${PROJECT_NAME}_wiki-data"
    "${PROJECT_NAME}_db-data"
    "${PROJECT_NAME}_qdrant-data"
    "${PROJECT_NAME}_ai-cache"
    "${PROJECT_NAME}_mkdocs-site"
)

backup_success=0
backup_failed=0

for volume in "${volumes[@]}"; do
    # 检查卷是否存在
    if docker volume inspect "$volume" > /dev/null 2>&1; then
        if backup_volume "$volume"; then
            backup_success=$((backup_success + 1))
        else
            backup_failed=$((backup_failed + 1))
        fi
    else
        echo -e "  ${YELLOW}⚠ 卷 $volume 不存在，跳过${NC}"
    fi
done

echo ""
echo -e "${GREEN}✓ 成功备份 $backup_success 个卷${NC}"
if [ $backup_failed -gt 0 ]; then
    echo -e "${RED}✗ 失败 $backup_failed 个卷${NC}"
fi
echo ""

# 3. 备份配置文件
echo -e "${BLUE}3. 备份配置文件...${NC}"
CONFIG_BACKUP="$BACKUP_DIR/${BACKUP_NAME}-config.tar.gz"

tar -czf "$CONFIG_BACKUP" \
    .env \
    docker-compose.yml \
    .obsidian/ \
    scripts/ \
    2>/dev/null || true

if [ -f "$CONFIG_BACKUP" ]; then
    CONFIG_SIZE=$(du -h "$CONFIG_BACKUP" | cut -f1)
    echo -e "${GREEN}✓ 配置文件备份成功: $CONFIG_BACKUP ($CONFIG_SIZE)${NC}"
else
    echo -e "${YELLOW}⚠ 配置文件备份失败或为空${NC}"
fi
echo ""

# 4. 创建备份清单
echo -e "${BLUE}4. 创建备份清单...${NC}"
MANIFEST_FILE="$BACKUP_DIR/${BACKUP_NAME}-manifest.txt"

cat > "$MANIFEST_FILE" << EOF
工程师知识系统备份清单
========================================
备份时间: $(date)
备份名称: $BACKUP_NAME
主机名: $(hostname)
========================================

备份文件:
EOF

# 列出所有备份文件
ls -lh "$BACKUP_DIR/${BACKUP_NAME}"* 2>/dev/null | awk '{print $9, "(" $5 ")"}' >> "$MANIFEST_FILE" || true

echo -e "${GREEN}✓ 备份清单创建成功: $MANIFEST_FILE${NC}"
echo ""

# 5. 计算总备份大小
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo "=========================================="
echo -e "${GREEN}备份完成！${NC}"
echo "=========================================="
echo ""
echo "备份位置: $BACKUP_DIR"
echo "备份总大小: $TOTAL_SIZE"
echo ""
echo "备份文件:"
ls -lh "$BACKUP_DIR/${BACKUP_NAME}"* 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "恢复说明:"
echo "  1. Git 仓库恢复:"
echo "     git clone ${BACKUP_NAME}.bundle knowledge-system-restored"
echo ""
echo "  2. Docker 卷恢复:"
echo "     docker run --rm -v <volume_name>:/data -v \$(pwd)/backups:/backup alpine sh -c 'cd / && tar -xzf /backup/<backup_file>'"
echo ""
echo "  3. 配置文件恢复:"
echo "     tar -xzf ${BACKUP_NAME}-config.tar.gz"
echo ""

# 6. 清理旧备份（可选）
if [ -n "$BACKUP_RETENTION_DAYS" ]; then
    echo -e "${BLUE}清理旧备份（保留 $BACKUP_RETENTION_DAYS 天）...${NC}"
    find "$BACKUP_DIR" -name "knowledge-system-backup-*" -type f -mtime +$BACKUP_RETENTION_DAYS -delete
    echo -e "${GREEN}✓ 旧备份清理完成${NC}"
    echo ""
fi

echo "备份脚本执行完成！"
echo ""
