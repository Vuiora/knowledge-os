#!/bin/bash

# 工程师知识系统 - 重新部署脚本
# 用于在修改 docker-compose.yml 后重新部署系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo ""
echo "=========================================="
echo "  工程师知识系统 - 重新部署"
echo "=========================================="
echo ""

# 1. 检查 NAS 挂载路径
log_info "步骤 1: 检查 NAS 挂载路径..."

NAS_BASE="/mnt/nas_share/appdata/knowledge"

if [ -d "/mnt/nas_share" ]; then
    log_success "NAS 共享路径存在"
else
    log_error "NAS 共享路径不存在: /mnt/nas_share"
    log_warning "请确保 NAS 已正确挂载"
    exit 1
fi

# 2. 创建必要的目录
log_info "步骤 2: 创建 NAS 目录结构..."

directories=(
    "${NAS_BASE}/gitea"
    "${NAS_BASE}/wiki-data"
    "${NAS_BASE}/wiki-repo"
    "${NAS_BASE}/postgres"
    "${NAS_BASE}/qdrant"
    "${NAS_BASE}/ai-cache"
    "${NAS_BASE}/mkdocs-site"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_success "创建目录: $dir"
    else
        log_info "目录已存在: $dir"
    fi
done

# 3. 设置目录权限
log_info "步骤 3: 设置目录权限..."

for dir in "${directories[@]}"; do
    chmod 755 "$dir"
    log_success "设置权限: $dir"
done

# 4. 备份现有数据（如果存在）
log_info "步骤 4: 检查是否需要备份现有数据..."

if docker volume ls | grep -q "knowledge-os_gitea-data"; then
    log_warning "检测到现有 Docker 卷，建议先备份数据"
    read -p "是否要备份现有数据？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "执行备份..."
        bash scripts/backup.sh
        log_success "备份完成"
    fi
fi

# 5. 停止现有服务
log_info "步骤 5: 停止现有服务..."

if docker-compose ps | grep -q "Up"; then
    docker-compose down
    log_success "服务已停止"
else
    log_info "没有运行中的服务"
fi

# 6. 迁移数据（如果需要）
log_info "步骤 6: 检查是否需要迁移数据..."

migrate_volume() {
    local volume_name=$1
    local target_dir=$2
    
    if docker volume ls | grep -q "$volume_name"; then
        log_info "迁移卷: $volume_name -> $target_dir"
        
        # 使用临时容器复制数据
        docker run --rm \
            -v ${volume_name}:/source \
            -v ${target_dir}:/target \
            alpine sh -c "cp -a /source/. /target/"
        
        if [ $? -eq 0 ]; then
            log_success "数据迁移成功: $volume_name"
        else
            log_error "数据迁移失败: $volume_name"
            return 1
        fi
    fi
}

# 迁移各个卷的数据
migrate_volume "knowledge-os_gitea-data" "${NAS_BASE}/gitea"
migrate_volume "knowledge-os_wiki-data" "${NAS_BASE}/wiki-data"
migrate_volume "knowledge-os_db-data" "${NAS_BASE}/postgres"
migrate_volume "knowledge-os_qdrant-data" "${NAS_BASE}/qdrant"
migrate_volume "knowledge-os_ai-cache" "${NAS_BASE}/ai-cache"
migrate_volume "knowledge-os_mkdocs-site" "${NAS_BASE}/mkdocs-site"

# 7. 删除旧的 Docker 卷（可选）
log_warning "步骤 7: 是否删除旧的 Docker 卷？"
echo "旧卷已不再使用，可以安全删除以释放空间"
read -p "删除旧卷？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "删除旧卷..."
    docker volume rm knowledge-os_gitea-data 2>/dev/null || true
    docker volume rm knowledge-os_wiki-data 2>/dev/null || true
    docker volume rm knowledge-os_wiki-repo 2>/dev/null || true
    docker volume rm knowledge-os_db-data 2>/dev/null || true
    docker volume rm knowledge-os_qdrant-data 2>/dev/null || true
    docker volume rm knowledge-os_ai-cache 2>/dev/null || true
    docker volume rm knowledge-os_mkdocs-site 2>/dev/null || true
    log_success "旧卷已删除"
fi

# 8. 启动服务
log_info "步骤 8: 启动服务..."

docker-compose up -d

if [ $? -eq 0 ]; then
    log_success "服务启动成功"
else
    log_error "服务启动失败"
    exit 1
fi

# 9. 等待服务就绪
log_info "步骤 9: 等待服务就绪..."

sleep 10

# 10. 验证服务状态
log_info "步骤 10: 验证服务状态..."

services=("knowledge-gitea" "knowledge-wiki" "knowledge-db" "knowledge-qdrant" "knowledge-webhook" "knowledge-ai" "knowledge-mkdocs")

all_running=true
for service in "${services[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
        if [ "$(docker inspect -f '{{.State.Running}}' ${service})" == "true" ]; then
            log_success "服务运行中: ${service}"
        else
            log_error "服务已停止: ${service}"
            all_running=false
        fi
    else
        log_error "服务不存在: ${service}"
        all_running=false
    fi
done

# 11. 验证数据挂载
log_info "步骤 11: 验证数据挂载..."

for dir in "${directories[@]}"; do
    if [ "$(ls -A $dir)" ]; then
        log_success "目录有数据: $dir"
    else
        log_warning "目录为空: $dir"
    fi
done

echo ""
echo "=========================================="
echo "  重新部署完成"
echo "=========================================="
echo ""

if [ "$all_running" = true ]; then
    log_success "所有服务运行正常"
    echo ""
    echo "服务访问地址："
    echo "  - Gitea:        http://localhost:3001"
    echo "  - Wiki.js:      http://localhost:3000"
    echo "  - MkDocs:       http://localhost:3002"
    echo "  - AI 助手:      http://localhost:3003"
    echo ""
    echo "数据存储位置："
    echo "  - NAS 路径:     ${NAS_BASE}"
    echo ""
    log_info "建议运行端到端测试验证系统："
    echo "  bash scripts/test-e2e.sh"
    echo ""
else
    log_error "部分服务启动失败，请检查日志："
    echo "  docker-compose logs"
    exit 1
fi
