# 工程师知识系统 - Windows 重新部署脚本
# 用于在修改 docker-compose.yml 后重新部署系统

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  工程师知识系统 - 重新部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 NAS 挂载路径
Write-Host "[INFO] 步骤 1: 检查 NAS 挂载路径..." -ForegroundColor Blue

$nasBase = "/mnt/nas_share/appdata/knowledge"

# 注意：在 Windows 上，Docker Desktop 使用 WSL2，路径是 Linux 风格
Write-Host "[!] 注意：此脚本假设你在 WSL2 环境中运行 Docker" -ForegroundColor Yellow
Write-Host "[!] 如果使用 Windows 路径，请修改 docker-compose.yml 中的路径" -ForegroundColor Yellow
Write-Host ""

# 2. 停止现有服务
Write-Host "[INFO] 步骤 2: 停止现有服务..." -ForegroundColor Blue

$runningContainers = docker-compose ps -q
if ($runningContainers) {
    docker-compose down
    Write-Host "[✓] 服务已停止" -ForegroundColor Green
} else {
    Write-Host "[INFO] 没有运行中的服务" -ForegroundColor Blue
}

# 3. 备份提示
Write-Host ""
Write-Host "[!] 重要提示：" -ForegroundColor Yellow
Write-Host "    如果你有重要数据，建议先运行备份脚本：" -ForegroundColor Yellow
Write-Host "    bash scripts/backup.sh" -ForegroundColor Yellow
Write-Host ""

$backup = Read-Host "是否继续重新部署？(y/n)"
if ($backup -ne "y" -and $backup -ne "Y") {
    Write-Host "[INFO] 已取消部署" -ForegroundColor Blue
    exit 0
}

# 4. 创建 NAS 目录（在 WSL2 中）
Write-Host ""
Write-Host "[INFO] 步骤 3: 创建 NAS 目录结构..." -ForegroundColor Blue

$directories = @(
    "$nasBase/gitea",
    "$nasBase/wiki-data",
    "$nasBase/wiki-repo",
    "$nasBase/postgres",
    "$nasBase/qdrant",
    "$nasBase/ai-cache",
    "$nasBase/mkdocs-site"
)

Write-Host "[INFO] 在 WSL2 中创建目录..." -ForegroundColor Blue
foreach ($dir in $directories) {
    wsl bash -c "mkdir -p $dir && chmod 755 $dir"
}
Write-Host "[✓] 目录创建完成" -ForegroundColor Green

# 5. 迁移现有数据
Write-Host ""
Write-Host "[INFO] 步骤 4: 迁移现有数据..." -ForegroundColor Blue

$volumes = @{
    "knowledge-os_gitea-data" = "$nasBase/gitea"
    "knowledge-os_wiki-data" = "$nasBase/wiki-data"
    "knowledge-os_db-data" = "$nasBase/postgres"
    "knowledge-os_qdrant-data" = "$nasBase/qdrant"
    "knowledge-os_ai-cache" = "$nasBase/ai-cache"
    "knowledge-os_mkdocs-site" = "$nasBase/mkdocs-site"
}

foreach ($volume in $volumes.Keys) {
    $existingVolume = docker volume ls --format "{{.Name}}" | Select-String -Pattern "^$volume$"
    if ($existingVolume) {
        Write-Host "[INFO] 迁移卷: $volume -> $($volumes[$volume])" -ForegroundColor Blue
        
        docker run --rm `
            -v ${volume}:/source `
            -v $($volumes[$volume]):/target `
            alpine sh -c "cp -a /source/. /target/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] 数据迁移成功: $volume" -ForegroundColor Green
        } else {
            Write-Host "[✗] 数据迁移失败: $volume" -ForegroundColor Red
        }
    }
}

# 6. 删除旧卷（可选）
Write-Host ""
$removeOld = Read-Host "是否删除旧的 Docker 卷以释放空间？(y/n)"
if ($removeOld -eq "y" -or $removeOld -eq "Y") {
    Write-Host "[INFO] 删除旧卷..." -ForegroundColor Blue
    foreach ($volume in $volumes.Keys) {
        docker volume rm $volume 2>$null
    }
    Write-Host "[✓] 旧卷已删除" -ForegroundColor Green
}

# 7. 启动服务
Write-Host ""
Write-Host "[INFO] 步骤 5: 启动服务..." -ForegroundColor Blue

docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] 服务启动成功" -ForegroundColor Green
} else {
    Write-Host "[✗] 服务启动失败" -ForegroundColor Red
    exit 1
}

# 8. 等待服务就绪
Write-Host ""
Write-Host "[INFO] 步骤 6: 等待服务就绪..." -ForegroundColor Blue
Start-Sleep -Seconds 15

# 9. 验证服务状态
Write-Host ""
Write-Host "[INFO] 步骤 7: 验证服务状态..." -ForegroundColor Blue

$services = @(
    "knowledge-gitea",
    "knowledge-wiki",
    "knowledge-db",
    "knowledge-qdrant",
    "knowledge-webhook",
    "knowledge-ai",
    "knowledge-mkdocs"
)

$allRunning = $true
foreach ($service in $services) {
    $container = docker ps --format "{{.Names}}" | Select-String -Pattern "^$service$"
    if ($container) {
        $running = docker inspect -f "{{.State.Running}}" $service
        if ($running -eq "true") {
            Write-Host "[✓] 服务运行中: $service" -ForegroundColor Green
        } else {
            Write-Host "[✗] 服务已停止: $service" -ForegroundColor Red
            $allRunning = $false
        }
    } else {
        Write-Host "[✗] 服务不存在: $service" -ForegroundColor Red
        $allRunning = $false
    }
}

# 10. 完成
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  重新部署完成" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($allRunning) {
    Write-Host "[✓] 所有服务运行正常" -ForegroundColor Green
    Write-Host ""
    Write-Host "服务访问地址：" -ForegroundColor Cyan
    Write-Host "  - Gitea:        http://localhost:3001"
    Write-Host "  - Wiki.js:      http://localhost:3000"
    Write-Host "  - MkDocs:       http://localhost:3002"
    Write-Host "  - AI 助手:      http://localhost:3003"
    Write-Host ""
    Write-Host "数据存储位置：" -ForegroundColor Cyan
    Write-Host "  - NAS 路径:     $nasBase"
    Write-Host ""
    Write-Host "[INFO] 建议运行端到端测试验证系统：" -ForegroundColor Blue
    Write-Host "  bash scripts/test-e2e.sh"
    Write-Host ""
} else {
    Write-Host "[✗] 部分服务启动失败，请检查日志：" -ForegroundColor Red
    Write-Host "  docker-compose logs"
    exit 1
}
