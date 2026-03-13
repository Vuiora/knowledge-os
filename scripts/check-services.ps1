# 服务健康检查脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "知识系统服务健康检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 容器状态
Write-Host "1. Docker 容器状态:" -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# 检查各服务端口
Write-Host "2. 服务端口检查:" -ForegroundColor Yellow

$services = @(
    @{Name="Gitea"; Port=8001; Path="/api/healthz"},
    @{Name="Wiki.js"; Port=8000; Path="/healthz"},
    @{Name="MkDocs"; Port=8002; Path="/"},
    @{Name="AI 助手"; Port=8003; Path="/health"},
    @{Name="Qdrant"; Port=6333; Path="/health"},
    @{Name="Webhook"; Port=9000; Path="/health"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)$($service.Path)" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ $($service.Name) (端口 $($service.Port)): " -NoNewline -ForegroundColor Green
            Write-Host "正常运行" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ $($service.Name) (端口 $($service.Port)): " -NoNewline -ForegroundColor Red
        Write-Host "无法访问 - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "3. 服务访问地址:" -ForegroundColor Yellow
Write-Host "  - Gitea:      http://localhost:8001" -ForegroundColor Cyan
Write-Host "  - Wiki.js:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - MkDocs:     http://localhost:8002" -ForegroundColor Cyan
Write-Host "  - AI 助手:    http://localhost:8003" -ForegroundColor Cyan
Write-Host "  - Qdrant:     http://localhost:6333" -ForegroundColor Cyan
Write-Host "  - Webhook:    http://localhost:9000" -ForegroundColor Cyan
Write-Host ""

Write-Host "4. 最近的日志 (最后 5 行):" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Gitea:" -ForegroundColor Magenta
docker-compose logs gitea --tail 5 2>&1 | Select-Object -Last 5
Write-Host ""
Write-Host "  Wiki.js:" -ForegroundColor Magenta
docker-compose logs wiki --tail 5 2>&1 | Select-Object -Last 5
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "检查完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
