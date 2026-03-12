# 知识系统部署步骤

## 前置检查

在开始之前，确保你已安装：
- Docker 和 Docker Compose
- Git

检查版本：
```bash
docker --version
docker compose version
git --version
```

## 第一步：配置环境变量

1. 复制环境变量模板：
```bash
copy .env.example .env
```

2. 编辑 `.env` 文件，设置以下必需的密码（使用强密码）：
```
GITEA_PASSWORD=你的Gitea管理员密码
POSTGRES_PASSWORD=你的PostgreSQL密码
GITEA_DB_PASS=你的Gitea数据库密码
WIKI_DB_PASS=你的Wiki数据库密码
WEBHOOK_SECRET=你的Webhook密钥
OPENAI_API_KEY=你的OpenAI密钥（如果使用AI功能）
```

提示：可以使用在线密码生成器生成强密码

## 第二步：初始化数据库

确保 `scripts/init-db.sql` 文件存在并包含正确的数据库初始化脚本。

## 第三步：启动所有服务

```bash
docker-compose up -d
```

等待所有服务启动（约1-2分钟）。

## 第四步：检查服务状态

```bash
docker-compose ps
```

所有服务应该显示 "Up" 状态。

查看日志（如有问题）：
```bash
docker-compose logs -f
```

## 第五步：初始化 Gitea

1. 访问：http://localhost:3000
2. 首次访问会显示安装向导
3. 数据库配置已自动完成，无需修改
4. 创建管理员账户：
   - 用户名：admin
   - 密码：使用 `.env` 中的 `GITEA_PASSWORD`
   - 邮箱：你的邮箱
5. 点击"安装 Gitea"

## 第六步：创建知识仓库

在 Gitea 中：
1. 点击右上角 "+" → "新建仓库"
2. 仓库名称：`knowledge-system`
3. 可见性：私有
4. 不勾选"初始化仓库"
5. 点击"创建仓库"

## 第七步：推送初始内容

```bash
# 添加远程仓库
git remote add origin http://localhost:3000/admin/knowledge-system.git

# 提交并推送
git add .
git commit -m "Initial commit"
git push -u origin main
```

输入 Gitea 用户名（admin）和密码。

## 第八步：配置 Webhook

在 Gitea 仓库页面：
1. 点击"设置" → "Web 钩子"
2. 点击"添加 Web 钩子" → "Gitea"
3. 配置：
   - 目标 URL: `http://webhook-handler:9000/hooks/knowledge-sync`
   - 密钥文本: 使用 `.env` 中的 `WEBHOOK_SECRET`
   - 触发条件: 勾选"推送事件"
4. 点击"添加 Web 钩子"

## 第九步：初始化 Wiki.js

1. 访问：http://localhost:3001
2. 选择语言：中文（简体）
3. 创建管理员账户
4. 点击"安装"

## 第十步：配置 Wiki.js Git 同步

在 Wiki.js 管理界面：
1. 点击右上角头像 → "管理"
2. 导航到"存储" → "Git"
3. 配置：
   - 仓库 URL: `http://gitea:3000/admin/knowledge-system.git`
   - 分支: `main`
   - 用户名: `admin`
   - 密码: Gitea 密码
   - 同步间隔: `PT5M`（每5分钟）
4. 点击"应用"
5. 点击"执行同步"测试

## 第十一步：配置 Obsidian（可选）

1. 下载安装 Obsidian：https://obsidian.md/
2. 打开 Obsidian，选择"打开文件夹作为仓库"
3. 选择 `knowledge/` 目录
4. 安装 Obsidian Git 插件
5. 配置自动同步（每10分钟）

## 验证部署

测试完整工作流：

1. 在 `knowledge/` 目录创建测试文件：
```bash
echo "# 测试文档" > knowledge/test.md
git add knowledge/test.md
git commit -m "Test"
git push
```

2. 检查各服务：
   - Gitea: http://localhost:3000 - 查看提交
   - Wiki.js: http://localhost:3001 - 等待5分钟后查看同步
   - MkDocs: http://localhost:3002 - 查看文档站点
   - AI 助手: http://localhost:3003/health - 检查健康状态

## 服务端口总览

- Gitea: http://localhost:3000
- Wiki.js: http://localhost:3001
- MkDocs: http://localhost:3002
- AI 助手: http://localhost:3003
- Qdrant: http://localhost:6333

## 常见问题

### 端口冲突
如果端口被占用，修改 `.env` 文件中的端口号，然后重启：
```bash
docker-compose down
docker-compose up -d
```

### 服务无法启动
查看日志找出原因：
```bash
docker-compose logs [服务名]
```

### 忘记密码
重置 Gitea 管理员密码：
```bash
docker exec -it knowledge-gitea gitea admin user change-password --username admin --password 新密码
```

## 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据（警告：会删除所有数据）
docker-compose down -v
```

## 下一步

- 阅读 [用户指南](docs/USER_GUIDE.md) 了解如何使用系统
- 查看 [详细部署文档](docs/DEPLOYMENT.md) 了解高级配置
- 开始在 `knowledge/` 目录组织你的知识

---

部署完成！开始构建你的知识库吧 🚀
