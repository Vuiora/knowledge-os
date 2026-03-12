# 工程师知识系统 (Engineer Knowledge System)

> 一个集成化的个人知识管理平台，连接 Obsidian、Wiki.js、MkDocs 和 AI 助手，基于统一的 Git 知识仓库

## 📋 系统概述

工程师知识系统是一个综合性的知识管理解决方案，专为工程师设计，帮助系统化地捕获、组织、连接和检索技术知识。系统采用五层知识层次结构（基础、技术、架构、项目、洞察），支持从个人笔记到团队协作再到公开发布的渐进式工作流。

### 核心特性

- **📝 统一的 Git 仓库**：所有工具共享同一个数据源，确保一致性
- **🔗 知识图谱**：通过 Obsidian 双向链接构建概念网络
- **👥 团队协作**：Wiki.js 提供 Web 界面和权限管理
- **📚 文档发布**：MkDocs 生成精美的静态文档站点
- **🤖 AI 助手**：基于 RAG 的智能问答和语义搜索
- **🔄 自动同步**：Webhook 驱动的自动化工作流
- **🐳 容器化部署**：Docker Compose 一键启动所有服务

### 五层知识结构

```
knowledge/
├── 01-foundations/      # 基础层：操作系统、网络、算法、数据库
├── 02-technologies/     # 技术层：嵌入式、AI、云计算
├── 03-architecture/     # 架构层：系统设计、分布式架构
├── 04-projects/         # 项目层：实际项目经验和案例
└── 05-insights/         # 洞察层：工程思考、职业发展
```

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- Git
- Obsidian Desktop（可选，用于本地编辑）

### 安装步骤

1. **克隆仓库**

```bash
git clone <your-repo-url> knowledge-system
cd knowledge-system
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的密码和 API 密钥
```

3. **初始化目录结构**

```bash
bash scripts/init.sh
```

4. **启动所有服务**

```bash
docker-compose up -d
```

5. **访问服务**

- **Gitea**：http://localhost:3001 - Git 服务器
- **Wiki.js**：http://localhost:3000 - 团队知识库
- **MkDocs**：http://localhost:3002 - 文档站点
- **AI 助手**：http://localhost:3003 - API 端点

### 首次配置

#### 1. 初始化 Gitea

访问 http://localhost:3001 完成初始设置：
- 创建管理员账户
- 创建仓库：`knowledge-system`
- 配置 SSH 密钥（可选）

#### 2. 推送初始内容

```bash
git remote add origin http://localhost:3001/<username>/knowledge-system.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

#### 3. 配置 Gitea Webhook

在 Gitea 仓库设置中添加 Webhook：
- URL: `http://webhook-handler:9000/hooks/knowledge-sync`
- Secret: 与 `.env` 中的 `WEBHOOK_SECRET` 一致
- 触发事件：Push events

#### 4. 初始化 Wiki.js

访问 http://localhost:3000 完成设置：
- 配置 Git Storage 指向 Gitea 仓库
- 设置同步间隔（推荐 5 分钟）

#### 5. 配置 Obsidian

- 打开 Obsidian
- 选择 "Open folder as vault"
- 选择 `knowledge-system/knowledge/` 目录
- 安装 Obsidian Git 插件
- 配置自动同步（推荐 10 分钟间隔）

## 🏗️ 架构说明

### 系统架构图

```
┌─────────────┐
│   Obsidian  │ ──┐
└─────────────┘   │
                  │
┌─────────────┐   │    ┌──────────────┐
│   Wiki.js   │ ──┼───▶│ Git 知识仓库 │
└─────────────┘   │    └──────────────┘
                  │           │
┌─────────────┐   │           │
│   MkDocs    │ ──┘           │
└─────────────┘               │
                              ▼
                    ┌──────────────────┐
                    │  Webhook Handler │
                    └──────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐    ┌─────────────┐
            │ 嵌入生成器    │───▶│ Qdrant 向量 │
            └──────────────┘    │   数据库    │
                                └─────────────┘
                                        │
                                        ▼
                                ┌──────────────┐
                                │  AI 知识助手 │
                                └──────────────┘
```

### 核心组件

| 组件 | 技术栈 | 职责 |
|------|--------|------|
| **Git 仓库** | Gitea | 中央数据源和版本控制 |
| **知识图谱** | Obsidian | 个人笔记和双向链接 |
| **团队知识库** | Wiki.js + PostgreSQL | Web 协作和权限管理 |
| **文档站点** | MkDocs + Material | 静态站点生成和发布 |
| **向量数据库** | Qdrant | 语义搜索和嵌入存储 |
| **AI 助手** | Python + FastAPI | RAG 问答和知识检索 |
| **Webhook 处理** | Python + Flask | 自动化工作流触发 |

### 数据流

1. **内容创建**：用户在 Obsidian 中创建/编辑 Markdown 文档
2. **版本控制**：Obsidian Git 插件自动提交并推送到 Gitea
3. **触发同步**：Gitea Webhook 通知 Webhook Handler
4. **多路同步**：
   - Wiki.js 从 Git 拉取更新
   - MkDocs 重新构建静态站点
   - AI 助手更新嵌入向量
5. **智能检索**：用户通过 AI 助手进行语义搜索

## 📖 使用指南

### 日常工作流

1. **在 Obsidian 中创建笔记**
   - 选择合适的知识层（01-05）
   - 使用 `[[双向链接]]` 连接相关概念
   - 添加标签和元数据

2. **自动同步**
   - Obsidian Git 插件每 10 分钟自动提交
   - 或手动触发：`Ctrl+P` → `Obsidian Git: Commit and push`

3. **团队协作**
   - 在 Wiki.js 中查看和编辑文档
   - 使用 Web 界面进行协作

4. **发布文档**
   - 将成熟内容移至 `_site/` 目录
   - MkDocs 自动构建并发布

5. **AI 问答**
   - 使用 AI 助手快速检索知识
   - 获取带源文档引用的答案

### AI 助手使用示例

```bash
# 查询示例
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "STM32 DMA 的工作原理是什么？"}'

# 响应示例
{
  "answer": "STM32 DMA（直接内存访问）允许外设直接访问内存...",
  "sources": [
    {
      "file_path": "knowledge/02-technologies/embedded/mcu/stm32-dma.md",
      "score": 0.89
    }
  ]
}
```

## 🔧 配置说明

### 环境变量

关键环境变量说明（`.env` 文件）：

```bash
# Gitea 配置
GITEA_PORT=3001              # Gitea Web 端口
GITEA_SSH_PORT=2222          # Gitea SSH 端口
GITEA_USER=admin             # 管理员用户名
GITEA_PASSWORD=***           # 管理员密码
GITEA_TOKEN=***              # API 访问令牌

# Wiki.js 配置
WIKI_PORT=3000               # Wiki.js 端口
WIKI_TOKEN=***               # API 访问令牌

# AI 助手配置
OPENAI_API_KEY=***           # OpenAI API 密钥
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Webhook 配置
WEBHOOK_SECRET=***           # Webhook 签名密钥
```

### 自定义配置

#### MkDocs 主题

编辑 `knowledge/_site/mkdocs.yml` 自定义文档站点：

```yaml
theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.tabs
    - search.suggest
```

#### Obsidian 插件

推荐插件：
- **Obsidian Git**：自动 Git 同步
- **Dataview**：数据查询和展示
- **Templater**：模板自动化
- **Calendar**：日记和时间线

## 🛠️ 维护和管理

### 健康检查

```bash
# 检查所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 检查特定服务
docker-compose logs -f ai-assistant
```

### 备份

```bash
# 备份 Git 仓库（最重要）
bash scripts/backup.sh

# 手动备份
git bundle create knowledge-backup-$(date +%Y%m%d).bundle --all
```

### 恢复

```bash
# 从备份恢复
bash scripts/restore.sh knowledge-backup-20260310.bundle
```

### 更新服务

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

## 📊 监控

### 服务端点

- **Gitea Health**: http://localhost:3001/api/healthz
- **Wiki.js Health**: http://localhost:3000/healthz
- **Qdrant Health**: http://localhost:6333/health
- **AI Assistant Health**: http://localhost:3003/health

### 同步状态

```bash
# 检查 Wiki.js 同步状态
curl http://localhost:3000/api/sync/status

# 检查 AI 嵌入状态
curl http://localhost:3003/api/embeddings/status
```

## 🐛 故障排除

### 常见问题

**问题：Gitea Webhook 未触发**
- 检查 Webhook URL 是否正确
- 验证 Secret 是否匹配
- 查看 Gitea 日志：`docker-compose logs gitea`

**问题：Wiki.js 未同步**
- 检查 Git Storage 配置
- 验证 Git 凭据
- 手动触发同步：`curl -X POST http://localhost:3000/api/sync`

**问题：AI 助手无响应**
- 检查 Qdrant 是否运行
- 验证 OpenAI API 密钥
- 查看日志：`docker-compose logs ai-assistant`

**问题：Obsidian Git 同步失败**
- 检查 Git 远程仓库配置
- 验证认证凭据
- 尝试手动 push：`git push origin main`

### 重置服务

```bash
# 停止所有服务
docker-compose down

# 清理数据卷（警告：会删除所有数据）
docker-compose down -v

# 重新启动
docker-compose up -d
```

## 📚 更多文档

- [详细部署文档](docs/DEPLOYMENT.md)
- [用户指南](docs/USER_GUIDE.md)
- [API 文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

MIT License

## 🙏 致谢

本项目使用了以下优秀的开源项目：
- [Obsidian](https://obsidian.md/)
- [Wiki.js](https://js.wiki/)
- [MkDocs](https://www.mkdocs.org/)
- [Gitea](https://gitea.io/)
- [Qdrant](https://qdrant.tech/)
- [Sentence Transformers](https://www.sbert.net/)

---

**开始构建你的知识帝国！** 🚀
