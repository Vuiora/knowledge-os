# 部署文档 (Deployment Guide)

## 目录

- [系统要求](#系统要求)
- [安装前准备](#安装前准备)
- [详细部署步骤](#详细部署步骤)
- [配置说明](#配置说明)
- [服务配置](#服务配置)
- [安全配置](#安全配置)
- [性能优化](#性能优化)
- [故障排除](#故障排除)

## 系统要求

### 硬件要求

**最低配置**：
- CPU: 2 核心
- 内存: 4GB RAM
- 存储: 20GB 可用空间
- 网络: 稳定的互联网连接

**推荐配置**：
- CPU: 4 核心或更多
- 内存: 8GB RAM 或更多
- 存储: 50GB SSD
- 网络: 高速互联网连接

### 软件要求

- **操作系统**：
  - Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
  - macOS 11+
  - Windows 10/11 with WSL2

- **必需软件**：
  - Docker 20.10+
  - Docker Compose 2.0+
  - Git 2.30+

- **可选软件**：
  - Obsidian Desktop (用于本地编辑)
  - VS Code (用于配置编辑)

## 安装前准备

### 1. 安装 Docker

#### Linux (Ubuntu/Debian)

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 验证安装
sudo docker --version
sudo docker compose version

# 将当前用户添加到 docker 组（可选）
sudo usermod -aG docker $USER
newgrp docker
```

#### macOS

```bash
# 下载并安装 Docker Desktop for Mac
# https://www.docker.com/products/docker-desktop

# 或使用 Homebrew
brew install --cask docker
```

#### Windows

1. 启用 WSL2
2. 下载并安装 Docker Desktop for Windows
3. 在 Docker Desktop 设置中启用 WSL2 集成

### 2. 安装 Git

```bash
# Linux
sudo apt-get install git

# macOS
brew install git

# Windows (使用 Git for Windows)
# https://git-scm.com/download/win
```

### 3. 生成 SSH 密钥（可选）

```bash
# 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "your_email@example.com"

# 启动 ssh-agent
eval "$(ssh-agent -s)"

# 添加私钥
ssh-add ~/.ssh/id_ed25519
```

## 详细部署步骤

### 步骤 1：克隆或创建项目

```bash
# 如果从现有仓库克隆
git clone <your-repo-url> knowledge-system
cd knowledge-system

# 或创建新项目
mkdir knowledge-system
cd knowledge-system
git init
```

### 步骤 2：创建目录结构

```bash
# 运行初始化脚本
bash scripts/init.sh

# 或手动创建
mkdir -p knowledge/{01-foundations/{operating-system,network,algorithm,database},02-technologies/{embedded/{mcu,rtos,driver,protocol},ai,cloud},03-architecture/{embedded-system,distributed-system,platform},04-projects,05-insights/{engineering,career,technology-trend}}
mkdir -p knowledge/_wiki/{company,product,development}
mkdir -p knowledge/_site
mkdir -p .obsidian
mkdir -p scripts
mkdir -p ai-assistant
mkdir -p webhook-handler
mkdir -p mkdocs-builder
```

### 步骤 3：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

**必须配置的变量**：

```bash
# Gitea 管理员密码（必须）
GITEA_PASSWORD=your_secure_password_here

# PostgreSQL 密码（必须）
POSTGRES_PASSWORD=your_postgres_password_here

# Gitea 数据库密码（必须）
GITEA_DB_PASS=your_gitea_db_password_here

# Wiki.js 数据库密码（必须）
WIKI_DB_PASS=your_wiki_db_password_here

# Webhook 密钥（必须）
WEBHOOK_SECRET=your_webhook_secret_here

# OpenAI API 密钥（如果使用 OpenAI）
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**可选配置**：

```bash
# 端口配置
GITEA_PORT=3001
GITEA_SSH_PORT=2222
WIKI_PORT=3000
AI_PORT=8000
QDRANT_PORT=6333
MKDOCS_PORT=8080

# 域名配置（生产环境）
GITEA_DOMAIN=git.yourdomain.com
WIKI_DOMAIN=wiki.yourdomain.com
DOCS_DOMAIN=docs.yourdomain.com
```

### 步骤 4：生成安全密钥

```bash
# 使用脚本生成随机密钥
bash scripts/generate-secrets.sh

# 或手动生成
openssl rand -hex 32  # 生成 Webhook Secret
openssl rand -hex 32  # 生成数据库密码
```

### 步骤 5：启动服务

```bash
# 拉取 Docker 镜像
docker-compose pull

# 启动所有服务（后台运行）
docker-compose up -d

# 查看启动日志
docker-compose logs -f

# 等待所有服务启动（约 1-2 分钟）
```

### 步骤 6：验证服务状态

```bash
# 检查所有服务是否运行
docker-compose ps

# 应该看到所有服务状态为 "Up"
# NAME                    STATUS
# knowledge-gitea         Up
# knowledge-wiki          Up
# knowledge-db            Up
# knowledge-qdrant        Up
# knowledge-webhook       Up
# knowledge-ai            Up
# knowledge-mkdocs        Up
```

### 步骤 7：初始化 Gitea

1. 访问 http://localhost:3001
2. 首次访问会显示安装向导
3. 配置数据库（已自动配置，无需修改）
4. 创建管理员账户：
   - 用户名：admin（或自定义）
   - 密码：使用 `.env` 中的 `GITEA_PASSWORD`
   - 邮箱：your_email@example.com
5. 点击"安装 Gitea"

### 步骤 8：创建 Git 仓库

在 Gitea 中创建新仓库：
1. 点击右上角 "+" → "新建仓库"
2. 仓库名称：`knowledge-system`
3. 可见性：私有
4. 初始化：不勾选（我们已有本地内容）
5. 点击"创建仓库"

### 步骤 9：推送初始内容

```bash
# 添加 Gitea 作为远程仓库
git remote add origin http://localhost:3001/admin/knowledge-system.git

# 提交初始内容
git add .
git commit -m "Initial commit: Knowledge system setup"

# 推送到 Gitea
git push -u origin main

# 如果需要认证，使用 Gitea 用户名和密码
```

### 步骤 10：配置 Gitea Webhook

1. 在 Gitea 仓库页面，点击"设置" → "Web 钩子"
2. 点击"添加 Web 钩子" → "Gitea"
3. 配置：
   - 目标 URL: `http://webhook-handler:9000/hooks/knowledge-sync`
   - HTTP 方法: POST
   - POST Content Type: application/json
   - 密钥文本: 使用 `.env` 中的 `WEBHOOK_SECRET`
   - 触发条件: 勾选 "推送事件"
   - 激活: 勾选
4. 点击"添加 Web 钩子"

### 步骤 11：测试 Webhook

```bash
# 创建测试文件
echo "# Test" > knowledge/test.md
git add knowledge/test.md
git commit -m "Test webhook"
git push

# 检查 Webhook 日志
docker-compose logs webhook-handler

# 应该看到 Webhook 被触发的日志
```

### 步骤 12：初始化 Wiki.js

1. 访问 http://localhost:3000
2. 首次访问会显示设置向导
3. 选择语言：中文（简体）
4. 配置管理员账户：
   - 邮箱地址：admin@example.com
   - 密码：设置强密码
   - 确认密码
5. 点击"安装"
6. 等待安装完成

### 步骤 13：配置 Wiki.js Git 同步

1. 登录 Wiki.js
2. 点击右上角头像 → "管理"
3. 导航到"存储" → "Git"
4. 点击"配置"
5. 填写配置：
   - 认证类型: Basic
   - 仓库 URL: `http://gitea:3000/admin/knowledge-system.git`
   - 分支: `main`
   - 用户名: `admin`（Gitea 用户名）
   - 密码: Gitea 密码
   - 本地仓库路径: `/wiki/data/repo`
   - 同步方向: Sync ← Remote (Pull)
   - 同步间隔: `PT5M`（每 5 分钟）
   - 默认作者邮箱: `wiki@example.com`
   - 默认作者名称: `Wiki.js`
6. 点击"应用"
7. 点击"执行同步"测试

### 步骤 14：配置 Obsidian

1. 下载并安装 Obsidian：https://obsidian.md/
2. 打开 Obsidian
3. 选择"打开文件夹作为仓库"
4. 选择 `knowledge-system/knowledge/` 目录
5. 安装 Obsidian Git 插件：
   - 打开设置 → 社区插件
   - 关闭安全模式
   - 浏览社区插件
   - 搜索 "Obsidian Git"
   - 安装并启用
6. 配置 Obsidian Git：
   - 打开设置 → Obsidian Git
   - 自动备份间隔: 10（分钟）
   - 自动拉取间隔: 10（分钟）
   - 启动时自动拉取: 开启
   - 推送前拉取: 开启
   - 提交消息: `vault backup: {{date}}`

### 步骤 15：验证完整工作流

1. 在 Obsidian 中创建测试文档：
   ```markdown
   # 测试文档
   
   这是一个测试文档，用于验证自动同步。
   
   [[相关概念]]
   ```

2. 等待 Obsidian Git 自动提交（或手动触发：Ctrl+P → "Obsidian Git: Commit and push"）

3. 检查 Gitea 是否收到提交：
   - 访问 http://localhost:3001/admin/knowledge-system
   - 查看最新提交

4. 等待 5 分钟，检查 Wiki.js 是否同步：
   - 访问 http://localhost:3000
   - 查找测试文档

5. 检查 AI 助手是否索引：
   ```bash
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{"question": "测试文档"}'
   ```

## 配置说明

### Docker Compose 配置

`docker-compose.yml` 文件定义了所有服务。关键配置：

#### 服务端口映射

```yaml
services:
  gitea:
    ports:
      - "${GITEA_PORT:-3001}:3000"      # Web 界面
      - "${GITEA_SSH_PORT:-2222}:22"    # SSH Git
  
  wiki:
    ports:
      - "${WIKI_PORT:-3000}:3000"       # Web 界面
  
  qdrant:
    ports:
      - "${QDRANT_PORT:-6333}:6333"     # HTTP API
      - "6334:6334"                      # gRPC API
  
  ai-assistant:
    ports:
      - "${AI_PORT:-8000}:8000"         # FastAPI
  
  mkdocs-builder:
    ports:
      - "${MKDOCS_PORT:-8080}:8080"     # 文档站点
```

#### 数据持久化

所有重要数据都存储在 Docker 卷中：

```yaml
volumes:
  gitea-data:      # Gitea 数据（仓库、配置）
  wiki-data:       # Wiki.js 数据
  db-data:         # PostgreSQL 数据库
  qdrant-data:     # Qdrant 向量数据
  ai-cache:        # AI 模型缓存
  mkdocs-site:     # MkDocs 构建输出
```

#### 网络配置

所有服务在同一个 Docker 网络中：

```yaml
networks:
  default:
    name: knowledge-network
```

服务间可以通过服务名访问，例如：
- `http://gitea:3000`
- `http://wiki:3000`
- `http://qdrant:6333`

### 数据库初始化

`scripts/init-db.sql` 创建必要的数据库：

```sql
-- 创建 Gitea 数据库
CREATE DATABASE gitea;
CREATE USER gitea WITH PASSWORD 'giteapass';
GRANT ALL PRIVILEGES ON DATABASE gitea TO gitea;

-- 创建 Wiki.js 数据库
CREATE DATABASE wiki;
CREATE USER wikijs WITH PASSWORD 'wikijspass';
GRANT ALL PRIVILEGES ON DATABASE wiki TO wikijs;
```

### AI 助手配置

AI 助手支持多种配置选项：

```bash
# 使用 OpenAI API
OPENAI_API_KEY=sk-your-key-here
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# 或使用本地 LLM（需要额外配置）
USE_LOCAL_LLM=true
LOCAL_LLM_MODEL=llama2
LOCAL_LLM_URL=http://ollama:11434
```

## 服务配置

### Gitea 高级配置

编辑 Gitea 配置文件（在容器内）：

```bash
# 进入 Gitea 容器
docker exec -it knowledge-gitea bash

# 编辑配置
vi /data/gitea/conf/app.ini
```

常用配置：

```ini
[server]
DOMAIN = git.yourdomain.com
ROOT_URL = https://git.yourdomain.com/
HTTP_PORT = 3000

[repository]
DEFAULT_BRANCH = main
ENABLE_PUSH_CREATE_USER = true

[security]
INSTALL_LOCK = true
SECRET_KEY = your-secret-key

[service]
DISABLE_REGISTRATION = true
REQUIRE_SIGNIN_VIEW = false
```

### Wiki.js 高级配置

Wiki.js 配置通过 Web 界面管理，但也可以通过环境变量：

```yaml
environment:
  # 数据库配置
  DB_TYPE: postgres
  DB_HOST: db
  DB_PORT: 5432
  
  # 日志级别
  LOG_LEVEL: info
  
  # 上传限制
  UPLOAD_MAX_FILE_SIZE: 5242880  # 5MB
  UPLOAD_MAX_FILES: 10
```

### Qdrant 配置

Qdrant 配置文件（可选）：

```yaml
# qdrant-config.yaml
service:
  max_request_size_mb: 32
  
storage:
  storage_path: /qdrant/storage
  
log_level: INFO
```

挂载配置：

```yaml
qdrant:
  volumes:
    - ./qdrant-config.yaml:/qdrant/config/config.yaml
    - qdrant-data:/qdrant/storage
```

## 安全配置

### 1. 使用 HTTPS

#### 使用 Nginx 反向代理

安装 Nginx：

```bash
sudo apt-get install nginx certbot python3-certbot-nginx
```

配置 Nginx（`/etc/nginx/sites-available/knowledge-system`）：

```nginx
# Gitea
server {
    listen 80;
    server_name git.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Wiki.js
server {
    listen 80;
    server_name wiki.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# MkDocs
server {
    listen 80;
    server_name docs.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
    }
}
```

启用 HTTPS：

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/knowledge-system /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 获取 SSL 证书
sudo certbot --nginx -d git.yourdomain.com -d wiki.yourdomain.com -d docs.yourdomain.com
```

### 2. 防火墙配置

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable

# 如果直接暴露服务端口
sudo ufw allow 3001/tcp    # Gitea
sudo ufw allow 3000/tcp    # Wiki.js
```

### 3. 密钥管理

**不要将密钥提交到 Git**：

```bash
# .gitignore 应包含
.env
*.key
*.pem
secrets/
```

**使用密钥管理工具**（生产环境）：
- Docker Secrets
- HashiCorp Vault
- AWS Secrets Manager

### 4. 访问控制

**Gitea**：
- 禁用公开注册
- 启用双因素认证
- 使用 SSH 密钥而非密码

**Wiki.js**：
- 配置用户组和权限
- 启用 LDAP/OAuth 集成
- 限制匿名访问

## 性能优化

### 1. 资源限制

为服务设置资源限制：

```yaml
services:
  qdrant:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
  
  ai-assistant:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 2. 数据库优化

PostgreSQL 配置优化：

```yaml
db:
  environment:
    POSTGRES_INITDB_ARGS: "-E UTF8 --locale=C"
  command: >
    postgres
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
    -c work_mem=4MB
    -c min_wal_size=1GB
    -c max_wal_size=4GB
```

### 3. Qdrant 优化

```yaml
qdrant:
  environment:
    QDRANT__SERVICE__MAX_REQUEST_SIZE_MB: 32
    QDRANT__STORAGE__PERFORMANCE__MAX_SEARCH_THREADS: 4
```

### 4. 缓存配置

AI 助手缓存：

```yaml
ai-assistant:
  environment:
    CACHE_ENABLED: "true"
    CACHE_TTL: 3600
    CACHE_MAX_SIZE: 1000
```

### 5. 日志管理

限制日志大小：

```yaml
services:
  gitea:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 故障排除

### 问题 1：服务无法启动

**症状**：`docker-compose up` 失败

**诊断**：
```bash
# 查看详细日志
docker-compose logs

# 检查特定服务
docker-compose logs gitea
docker-compose logs db
```

**常见原因**：
1. 端口冲突
   ```bash
   # 检查端口占用
   sudo netstat -tulpn | grep :3001
   
   # 修改 .env 中的端口
   GITEA_PORT=3002
   ```

2. 数据库连接失败
   ```bash
   # 检查数据库是否运行
   docker-compose ps db
   
   # 重启数据库
   docker-compose restart db
   ```

3. 权限问题
   ```bash
   # 修复卷权限
   sudo chown -R 1000:1000 ./data
   ```

### 问题 2：Gitea Webhook 不工作

**症状**：推送代码后其他服务未更新

**诊断**：
```bash
# 检查 Webhook Handler 日志
docker-compose logs webhook-handler

# 测试 Webhook 端点
curl -X POST http://localhost:9000/hooks/knowledge-sync \
  -H "Content-Type: application/json" \
  -H "X-Gitea-Signature: test" \
  -d '{"repository":{"name":"test"}}'
```

**解决方案**：
1. 验证 Webhook URL 正确
2. 检查 Secret 是否匹配
3. 确认 Webhook Handler 服务运行中
4. 查看 Gitea 中的 Webhook 交付历史

### 问题 3：Wiki.js 同步失败

**症状**：Wiki.js 未显示最新内容

**诊断**：
```bash
# 检查 Wiki.js 日志
docker-compose logs wiki

# 手动触发同步
curl -X POST http://localhost:3000/api/sync \
  -H "Authorization: Bearer YOUR_WIKI_TOKEN"
```

**解决方案**：
1. 验证 Git 凭据正确
2. 检查仓库 URL 可访问
3. 确认分支名称正确（main vs master）
4. 手动进入容器测试 Git 连接：
   ```bash
   docker exec -it knowledge-wiki bash
   git clone http://gitea:3000/admin/knowledge-system.git /tmp/test
   ```

### 问题 4：AI 助手无响应

**症状**：查询 AI 助手超时或返回错误

**诊断**：
```bash
# 检查 AI 助手日志
docker-compose logs ai-assistant

# 检查 Qdrant 状态
curl http://localhost:6333/health

# 测试嵌入生成
curl -X POST http://localhost:8000/api/test-embedding \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文本"}'
```

**解决方案**：
1. 验证 OpenAI API 密钥有效
2. 检查 Qdrant 是否运行
3. 确认模型已下载：
   ```bash
   docker exec -it knowledge-ai ls /app/models
   ```
4. 重启 AI 助手：
   ```bash
   docker-compose restart ai-assistant
   ```

### 问题 5：Obsidian Git 同步失败

**症状**：Obsidian 无法推送或拉取

**诊断**：
1. 检查 Git 配置：
   ```bash
   cd knowledge-system
   git remote -v
   git status
   ```

2. 测试手动推送：
   ```bash
   git push origin main
   ```

**解决方案**：
1. 验证 Git 远程 URL 正确
2. 检查认证凭据（用户名/密码或 SSH 密钥）
3. 配置 Git 凭据缓存：
   ```bash
   git config credential.helper store
   ```
4. 使用 SSH 而非 HTTPS：
   ```bash
   git remote set-url origin git@localhost:admin/knowledge-system.git
   ```

### 问题 6：Docker 卷空间不足

**症状**：服务崩溃，日志显示磁盘空间不足

**诊断**：
```bash
# 检查 Docker 磁盘使用
docker system df

# 检查卷大小
docker volume ls
docker volume inspect knowledge-system_gitea-data
```

**解决方案**：
```bash
# 清理未使用的资源
docker system prune -a

# 清理未使用的卷
docker volume prune

# 如果需要，迁移到更大的磁盘
# 1. 停止服务
docker-compose down

# 2. 备份卷
docker run --rm -v knowledge-system_gitea-data:/data -v $(pwd):/backup \
  alpine tar -czf /backup/gitea-backup.tar.gz /data

# 3. 在新位置恢复
```

### 问题 7：性能问题

**症状**：服务响应缓慢

**诊断**：
```bash
# 检查容器资源使用
docker stats

# 检查系统资源
htop
df -h
free -m
```

**解决方案**：
1. 增加资源限制（见性能优化部分）
2. 优化数据库查询
3. 启用缓存
4. 考虑水平扩展

## 备份和恢复

### 自动备份

设置定时备份：

```bash
# 编辑 crontab
crontab -e

# 添加每日备份任务（凌晨 2 点）
0 2 * * * /path/to/knowledge-system/scripts/backup.sh
```

### 手动备份

```bash
# 运行备份脚本
bash scripts/backup.sh

# 备份文件位置
ls -lh backups/
```

### 恢复

```bash
# 从备份恢复
bash scripts/restore.sh backups/knowledge-backup-20260310.tar.gz
```

## 升级

### 升级 Docker 镜像

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d

# 检查日志
docker-compose logs -f
```

### 升级特定服务

```bash
# 只升级 Gitea
docker-compose pull gitea
docker-compose up -d gitea
```

## 监控

### 健康检查脚本

创建 `scripts/health-check.sh`：

```bash
#!/bin/bash

services=("gitea:3001" "wiki:3000" "qdrant:6333" "ai-assistant:8000")

for service in "${services[@]}"; do
    name="${service%%:*}"
    port="${service##*:}"
    
    if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✓ $name is healthy"
    else
        echo "✗ $name is unhealthy"
    fi
done
```

### 日志聚合

使用 Loki + Grafana（可选）：

```yaml
# docker-compose.monitoring.yml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3200:3000"
```

## 生产环境建议

1. **使用 HTTPS**：配置 SSL/TLS 证书
2. **定期备份**：自动化备份策略
3. **监控告警**：设置服务监控和告警
4. **资源限制**：为每个服务设置合理的资源限制
5. **日志管理**：配置日志轮转和归档
6. **安全加固**：定期更新、最小权限原则
7. **灾难恢复**：测试恢复流程
8. **文档更新**：保持部署文档最新

## 支持

如遇到问题：
1. 查看本文档的故障排除部分
2. 检查服务日志：`docker-compose logs`
3. 查看 GitHub Issues
4. 联系技术支持

---

**祝部署顺利！** 🚀
