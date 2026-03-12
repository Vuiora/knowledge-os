# MkDocs 构建服务

MkDocs 构建服务负责从 Gitea 仓库克隆知识内容，构建静态文档站点，并提供 Web 访问。

## 功能特性

- **自动克隆/拉取**: 从 Gitea 仓库自动同步最新内容
- **MkDocs 构建**: 使用 Material 主题构建美观的文档站点
- **静态文件服务**: 提供构建后的静态文件访问
- **Webhook 集成**: 接收 Git push 事件自动触发重新构建
- **构建状态通知**: 构建完成后发送状态通知
- **健康检查**: 提供服务健康状态查询

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `GITEA_URL` | Gitea 服务器 URL | `http://gitea:3000` |
| `GITEA_TOKEN` | Gitea API Token | (必需) |
| `REPO_PATH` | 仓库路径 | `admin/knowledge-system` |
| `BUILD_ON_STARTUP` | 启动时是否构建 | `true` |
| `NOTIFICATION_URL` | 构建通知 URL | (可选) |

## API 端点

### 健康检查

```bash
GET /health
```

返回服务健康状态和构建信息。

**响应示例**:
```json
{
  "status": "ok",
  "service": "mkdocs-builder",
  "building": false,
  "site_exists": true
}
```

### 获取构建状态

```bash
GET /status
```

返回详细的构建状态信息。

**响应示例**:
```json
{
  "last_build_time": "2024-03-11T10:30:00",
  "last_build_status": "success",
  "last_commit_sha": "abc123...",
  "site_exists": true,
  "is_building": false,
  "repo_dir": "/app/repo",
  "site_dir": "/app/site"
}
```

### 触发构建

```bash
POST /build
Content-Type: application/json

{
  "force": false
}
```

触发 MkDocs 构建流程。

**参数**:
- `force` (boolean): 是否强制重新构建，默认 `false`

**响应示例**:
```json
{
  "success": true,
  "message": "MkDocs 构建成功",
  "duration": 12.5,
  "commit_sha": "abc123...",
  "build_time": "2024-03-11T10:30:00"
}
```

### 强制重新构建

```bash
POST /rebuild
```

清理旧的构建并强制重新构建。

### 同步仓库

```bash
GET /sync
```

仅同步 Git 仓库，不执行构建。

**响应示例**:
```json
{
  "success": true,
  "message": "仓库同步成功",
  "commit_sha": "abc123..."
}
```

### Webhook 端点

```bash
POST /webhook
Content-Type: application/json

{
  "event_type": "push",
  "changed_files": ["knowledge/01-foundations/network/tcp.md"]
}
```

接收 webhook 事件并触发构建。

**参数**:
- `event_type` (string): 事件类型
- `changed_files` (array): 变更的文件列表

### 访问文档站点

```bash
GET /docs/
```

访问构建后的静态文档站点。

## 构建流程

1. **接收触发**: 通过 API 或 Webhook 接收构建请求
2. **同步仓库**: 从 Gitea 克隆或拉取最新代码
3. **准备环境**: 复制配置文件和资源文件
4. **执行构建**: 运行 `mkdocs build` 命令
5. **发送通知**: 构建完成后发送状态通知（如果配置）
6. **提供服务**: 通过 `/docs/` 路径提供静态文件访问

## MkDocs 配置

服务使用 `mkdocs.yml.template` 作为配置模板，包含以下特性：

- **Material 主题**: 现代化的文档主题
- **中文支持**: 优化的中文字体和搜索
- **代码高亮**: 支持多种编程语言
- **数学公式**: 支持 MathJax 渲染
- **Mermaid 图表**: 支持流程图和架构图
- **Git 修订日期**: 自动显示文档更新时间
- **搜索功能**: 全文搜索支持

## 目录结构

```
mkdocs-builder/
├── app.py                    # 主应用
├── gitea_client.py          # Gitea 客户端
├── builder.py               # MkDocs 构建器
├── mkdocs.yml.template      # MkDocs 配置模板
├── stylesheets/             # 自定义样式
│   └── extra.css
├── javascripts/             # 自定义脚本
│   └── mathjax.js
├── templates/               # 模板文件
│   └── index.md
├── Dockerfile               # Docker 镜像
├── requirements.txt         # Python 依赖
└── README.md               # 本文档
```

## 使用示例

### 手动触发构建

```bash
curl -X POST http://localhost:8080/build \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

### 查看构建状态

```bash
curl http://localhost:8080/status
```

### 访问文档

在浏览器中打开: `http://localhost:8080/docs/`

## 与其他服务集成

### Webhook Handler 集成

Webhook Handler 会在收到 Git push 事件时自动调用 `/build` 端点触发构建。

### Gitea 集成

服务使用 Gitea API Token 从仓库克隆内容，确保 Token 有读取权限。

## 故障排除

### 构建失败

1. 检查 Gitea 连接: `curl http://gitea:3000`
2. 检查 Token 权限
3. 查看构建日志: `docker logs knowledge-mkdocs`
4. 检查 knowledge 目录是否有有效的 Markdown 文件

### 静态文件无法访问

1. 确认构建成功: `GET /status`
2. 检查 `/app/site` 目录是否有文件
3. 尝试重新构建: `POST /rebuild`

### Git 同步失败

1. 检查网络连接
2. 验证 Gitea URL 和 Token
3. 检查仓库路径是否正确

## 开发

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GITEA_URL=http://localhost:3001
export GITEA_TOKEN=your_token
export REPO_PATH=admin/knowledge-system

# 运行服务
python app.py
```

### Docker 构建

```bash
docker build -t mkdocs-builder .
docker run -p 8080:8080 \
  -e GITEA_URL=http://gitea:3000 \
  -e GITEA_TOKEN=your_token \
  mkdocs-builder
```

## 许可证

本项目是工程师知识系统的一部分。
