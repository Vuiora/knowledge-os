# 快速启动指南

本指南将帮助您在 5 分钟内启动工程师知识系统。

## 前置要求

- Docker 和 Docker Compose 已安装
- Git 已安装
- 至少 4GB 可用内存

## 快速部署

### 1. 一键部署

```bash
# 运行部署脚本
bash scripts/deploy.sh
```

部署脚本会自动：
- ✅ 检查 Docker 环境
- ✅ 创建目录结构
- ✅ 构建 Docker 镜像
- ✅ 启动所有服务

### 2. 访问服务

部署完成后，访问以下地址：

| 服务 | 地址 | 用途 |
|------|------|------|
| Gitea | http://localhost:3001 | Git 服务器 |
| Wiki.js | http://localhost:3000 | 团队知识库 |
| AI Assistant | http://localhost:8000 | AI 问答 |
| MkDocs | http://localhost:8080 | 文档站点 |
| Webhook | http://localhost:9000 | 同步服务 |

### 3. 初始配置

#### 3.1 配置 Gitea

1. 访问 http://localhost:3001
2. 首次访问会显示安装页面
3. 保持默认配置（数据库已自动配置）
4. 创建管理员账户：
   - 用户名: `admin`
   - 密码: 使用 `.env` 中的 `GITEA_PASSWORD`
   - 邮箱: `admin@example.com`
5. 点击"安装 Gitea"

#### 3.2 创建知识仓库

1. 登录 Gitea
2. 点击右上角 "+" → "新建仓库"
3. 仓库名称: `knowledge-system`
4. 设置为私有仓库
5. 点击"创建仓库"

#### 3.3 配置 Webhook

1. 进入 `knowledge-system` 仓库
2. 点击"设置" → "Web 钩子"
3. 点击"添加 Web 钩子" → "Gitea"
4. 配置：
   - **目标 URL**: `http://webhook-handler:9000/hooks/knowledge-sync`
   - **密钥文本**: 复制 `.env` 中的 `WEBHOOK_SECRET`
   - **POST 内容类型**: `application/json`
   - **触发条件**: 勾选 "推送事件"
5. 点击"添加 Web 钩子"

#### 3.4 配置 Wiki.js

1. 访问 http://localhost:3000
2. 首次访问会显示安装向导
3. 选择语言: 中文
4. 配置管理员账户：
   - 邮箱: `admin@example.com`
   - 密码: 使用 `.env` 中的 `GITEA_PASSWORD`
5. 完成安装

#### 3.5 配置 Wiki.js Git 同步

1. 登录 Wiki.js
2. 点击右上角头像 → "管理"
3. 左侧菜单 → "存储"
4. 点击 "Git" → "设置"
5. 配置：
   - **认证类型**: Basic
   - **仓库 URL**: `http://gitea:3000/admin/knowledge-system.git`
   - **分支**: `main`
   - **用户名**: `admin`
   - **密码**: 使用 `.env` 中的 `GITEA_PASSWORD`
   - **同步方向**: 双向
   - **同步间隔**: `PT5M` (每 5 分钟)
   - **本地仓库路径**: `/wiki/repo`
6. 点击"应用"

### 4. 配置本地 Git

```bash
# 添加远程仓库
git remote add origin http://localhost:3001/admin/knowledge-system.git

# 提交初始内容
git add .
git commit -m "Initial commit: Knowledge system setup"

# 推送到 Gitea
git push -u origin main
```

首次推送时会要求输入用户名和密码：
- 用户名: `admin`
- 密码: 使用 `.env` 中的 `GITEA_PASSWORD`

### 5. 配置 Obsidian

1. 打开 Obsidian
2. 选择 "打开文件夹作为仓库"
3. 选择 `knowledge-system/knowledge/` 目录
4. 安装推荐插件：
   - Obsidian Git (自动同步)
   - Dataview (数据查询)
   - Templater (模板)

#### 配置 Obsidian Git 插件

1. 设置 → 社区插件 → 浏览
2. 搜索 "Obsidian Git"
3. 安装并启用
4. 配置插件：
   - **自动备份间隔**: 10 分钟
   - **自动拉取间隔**: 10 分钟
   - **启动时自动拉取**: 开启
   - **提交消息**: `vault backup: {{date}}`

## 验证部署

### 测试 Git 同步流程

1. 在 Obsidian 中创建测试文档：
   ```bash
   # 在 knowledge/01-foundations/ 创建文件
   echo "# 测试文档" > knowledge/01-foundations/test.md
   ```

2. 提交并推送：
   ```bash
   git add knowledge/01-foundations/test.md
   git commit -m "测试: 添加测试文档"
   git push origin main
   ```

3. 检查 Webhook 日志：
   ```bash
   docker compose logs webhook-handler
   ```

4. 等待 5 分钟后，在 Wiki.js 中查看是否同步

### 测试 Webhook Handler

```bash
# 健康检查
curl http://localhost:9000/health

# 手动触发 Wiki.js 同步
curl -X POST http://localhost:9000/api/wiki/sync

# 查询同步状态
curl http://localhost:9000/api/wiki/status
```

## 常用命令

### 查看服务状态
```bash
docker compose ps
```

### 查看日志
```bash
# 所有服务
docker compose logs -f

# 特定服务
docker compose logs -f gitea
docker compose logs -f wiki
docker compose logs -f webhook-handler
```

### 重启服务
```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart webhook-handler
```

### 停止服务
```bash
docker compose down
```

### 完全清理（包括数据）
```bash
docker compose down -v
```

## 故障排除

### 服务无法启动

1. 检查端口是否被占用：
   ```bash
   # Windows
   netstat -ano | findstr "3000"
   netstat -ano | findstr "3001"
   
   # Linux/Mac
   lsof -i :3000
   lsof -i :3001
   ```

2. 检查 Docker 日志：
   ```bash
   docker compose logs
   ```

### Webhook 不工作

1. 检查 Webhook Handler 日志：
   ```bash
   docker compose logs webhook-handler
   ```

2. 验证 Webhook 配置：
   - URL 是否正确
   - Secret 是否匹配
   - 事件类型是否选择了 "Push"

3. 测试 Webhook 连接：
   ```bash
   # 从 Gitea 容器内测试
   docker exec knowledge-gitea curl http://webhook-handler:9000/health
   ```

### Wiki.js 同步失败

1. 检查 Git 配置：
   - 仓库 URL 是否正确
   - 用户名密码是否正确
   - 分支名称是否为 `main`

2. 手动触发同步：
   ```bash
   curl -X POST http://localhost:9000/api/wiki/sync
   ```

3. 查看 Wiki.js 日志：
   ```bash
   docker compose logs wiki
   ```

### 数据库连接失败

1. 检查数据库是否运行：
   ```bash
   docker compose ps db
   ```

2. 检查数据库日志：
   ```bash
   docker compose logs db
   ```

3. 验证数据库密码：
   - 检查 `.env` 中的 `POSTGRES_PASSWORD`
   - 确保与 `docker-compose.yml` 中的配置一致

## 下一步

- 📖 阅读 [完整文档](.kiro/specs/engineer-knowledge-system/)
- 🔧 配置 AI 助手（任务 6-8）
- 📝 配置 MkDocs 构建（任务 10）
- 🎨 自定义 Obsidian 主题和插件
- 📚 开始创建知识内容

## 获取帮助

- 查看 [CHECKPOINT-5-REPORT.md](CHECKPOINT-5-REPORT.md) 了解详细验证信息
- 运行验证脚本: `bash scripts/verify-git-sync.sh`
- 查看设计文档: `.kiro/specs/engineer-knowledge-system/design.md`

---

**祝您使用愉快！** 🚀
