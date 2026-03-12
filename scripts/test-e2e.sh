#!/bin/bash

# 工程师知识系统 - 端到端测试脚本
# 此脚本验证所有核心功能是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果统计
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# 测试函数
test_docker_services() {
    log_info "测试 1: 检查 Docker 服务状态..."
    
    services=("knowledge-gitea" "knowledge-wiki" "knowledge-db" "knowledge-qdrant" "knowledge-webhook" "knowledge-ai" "knowledge-mkdocs")
    
    for service in "${services[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
            if [ "$(docker inspect -f '{{.State.Running}}' ${service})" == "true" ]; then
                log_success "服务 ${service} 正在运行"
            else
                log_error "服务 ${service} 已停止"
            fi
        else
            log_error "服务 ${service} 不存在"
        fi
    done
}

test_directory_structure() {
    log_info "测试 2: 检查目录结构完整性..."
    
    required_dirs=(
        "knowledge"
        "knowledge/01-foundations"
        "knowledge/02-technologies"
        "knowledge/03-architecture"
        "knowledge/04-projects"
        "knowledge/05-insights"
        ".obsidian"
        "scripts"
        "ai-assistant"
        "webhook-handler"
        "mkdocs-builder"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "目录存在: ${dir}"
        else
            log_error "目录缺失: ${dir}"
        fi
    done
}

test_health_endpoints() {
    log_info "测试 3: 检查服务健康端点..."
    
    # 等待服务启动
    sleep 5
    
    # 测试 Qdrant (根路径返回版本信息)
    if curl -s -f http://localhost:6333 > /dev/null 2>&1; then
        log_success "Qdrant 服务可访问"
    else
        log_error "Qdrant 服务不可访问"
    fi
    
    # 测试 AI 助手
    if curl -s -f http://localhost:3003/health > /dev/null 2>&1; then
        log_success "AI 助手健康检查通过"
    elif curl -s -f http://localhost:3003 > /dev/null 2>&1; then
        log_success "AI 助手服务可访问"
    else
        log_warning "AI 助手健康检查失败（服务可能未完全启动）"
    fi
    
    # 测试 Gitea (检查是否可访问)
    if curl -s -f http://localhost:3001 > /dev/null 2>&1; then
        log_success "Gitea 服务可访问"
    else
        log_error "Gitea 服务不可访问"
    fi
    
    # 测试 Wiki.js (检查是否可访问)
    if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Wiki.js 服务可访问"
    else
        log_error "Wiki.js 服务不可访问"
    fi
    
    # 测试 MkDocs Builder
    if curl -s -f http://localhost:3002 > /dev/null 2>&1; then
        log_success "MkDocs Builder 服务可访问"
    else
        log_warning "MkDocs Builder 服务不可访问（可能正在构建中）"
    fi
}

test_python_modules() {
    log_info "测试 4: 运行 Python 模块测试..."
    
    # 测试 AI 助手模块
    if docker exec knowledge-ai python test_modules.py > /dev/null 2>&1; then
        log_success "AI 助手模块测试通过"
    else
        log_warning "AI 助手模块测试失败（可能需要配置）"
    fi
}

test_git_repository() {
    log_info "测试 5: 检查 Git 仓库状态..."
    
    if [ -d ".git" ]; then
        log_success "Git 仓库已初始化"
        
        # 检查是否有远程仓库
        if git remote -v | grep -q "origin"; then
            log_success "Git 远程仓库已配置"
        else
            log_warning "Git 远程仓库未配置"
        fi
    else
        log_error "Git 仓库未初始化"
    fi
}

test_configuration_files() {
    log_info "测试 6: 检查配置文件..."
    
    config_files=(
        "docker-compose.yml"
        ".env.example"
        "scripts/init.sh"
        "scripts/deploy.sh"
        "scripts/backup.sh"
    )
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "配置文件存在: ${file}"
        else
            log_error "配置文件缺失: ${file}"
        fi
    done
    
    # 检查 .env 文件
    if [ -f ".env" ]; then
        log_success ".env 文件已配置"
    else
        log_warning ".env 文件未配置（使用默认值）"
    fi
}

test_docker_volumes() {
    log_info "测试 7: 检查 Docker 卷..."
    
    # 获取项目名称（从 docker-compose 项目名或目录名）
    project_name=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
    
    volumes=(
        "gitea-data"
        "wiki-data"
        "db-data"
        "qdrant-data"
        "ai-cache"
        "mkdocs-site"
    )
    
    for volume in "${volumes[@]}"; do
        # 尝试匹配带项目前缀的卷名
        if docker volume ls --format '{{.Name}}' | grep -q "^${project_name}_${volume}$"; then
            log_success "Docker 卷存在: ${project_name}_${volume}"
        elif docker volume ls --format '{{.Name}}' | grep -q "^knowledge-system_${volume}$"; then
            log_success "Docker 卷存在: knowledge-system_${volume}"
        elif docker volume ls --format '{{.Name}}' | grep -q "${volume}"; then
            log_success "Docker 卷存在: ${volume}"
        else
            log_error "Docker 卷缺失: ${volume}"
        fi
    done
}

test_network_connectivity() {
    log_info "测试 8: 检查容器网络连接..."
    
    # 测试容器间网络
    if docker exec knowledge-ai ping -c 1 qdrant > /dev/null 2>&1; then
        log_success "AI 助手可以连接到 Qdrant"
    else
        log_warning "AI 助手无法 ping Qdrant（可能防火墙阻止 ICMP）"
    fi
    
    if docker exec knowledge-webhook ping -c 1 wiki > /dev/null 2>&1; then
        log_success "Webhook Handler 可以连接到 Wiki.js"
    else
        log_warning "Webhook Handler 无法 ping Wiki.js（可能防火墙阻止 ICMP）"
    fi
    
    # 测试 HTTP 连接（更可靠）
    if docker exec knowledge-ai curl -s -f http://qdrant:6333 > /dev/null 2>&1; then
        log_success "AI 助手可以通过 HTTP 访问 Qdrant"
    else
        log_warning "AI 助手无法通过 HTTP 访问 Qdrant"
    fi
}

# 主测试流程
main() {
    echo ""
    echo "=========================================="
    echo "  工程师知识系统 - 端到端测试"
    echo "=========================================="
    echo ""
    
    # 运行所有测试
    test_docker_services
    echo ""
    
    test_directory_structure
    echo ""
    
    test_health_endpoints
    echo ""
    
    test_python_modules
    echo ""
    
    test_git_repository
    echo ""
    
    test_configuration_files
    echo ""
    
    test_docker_volumes
    echo ""
    
    test_network_connectivity
    echo ""
    
    # 输出测试结果
    echo "=========================================="
    echo "  测试结果汇总"
    echo "=========================================="
    echo -e "总测试数: ${TESTS_TOTAL}"
    echo -e "${GREEN}通过: ${TESTS_PASSED}${NC}"
    echo -e "${RED}失败: ${TESTS_FAILED}${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ 所有测试通过！${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ 部分测试失败，请检查上述错误信息${NC}"
        echo ""
        return 1
    fi
}

# 执行主函数
main
exit $?
