#!/bin/bash

# 工程师知识系统 - 初始化脚本
# 创建所有必需的目录结构

set -e

echo "初始化工程师知识系统目录结构..."

# 创建主目录结构
mkdir -p knowledge/01-foundations/{operating-system,network,algorithm,database}
mkdir -p knowledge/02-technologies/embedded/{mcu,rtos,driver,protocol}
mkdir -p knowledge/02-technologies/{ai,cloud}
mkdir -p knowledge/03-architecture/{embedded-system,distributed-system,platform}
mkdir -p knowledge/04-projects/{smart-ring,anti-snore-pillow}
mkdir -p knowledge/05-insights/{engineering,career,technology-trend}

# 创建 Wiki 专用内容目录（可选）
mkdir -p knowledge/_wiki/{company,product,development}

# 创建 MkDocs 配置目录
mkdir -p knowledge/_site

# 创建 Obsidian 配置目录
mkdir -p .obsidian

# 创建 Gitea Webhooks 配置目录
mkdir -p .gitea/workflows

# 创建脚本目录（如果不存在）
mkdir -p scripts

# 创建 Docker 相关目录
mkdir -p webhook-handler
mkdir -p ai-assistant
mkdir -p mkdocs-builder

echo "✓ 目录结构创建完成"

# 初始化 Git 仓库（如果尚未初始化）
if [ ! -d .git ]; then
    echo "初始化 Git 仓库..."
    git init
    echo "✓ Git 仓库初始化完成"
else
    echo "✓ Git 仓库已存在"
fi

# 创建 .gitignore 文件
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# 环境变量
.env

# Docker 数据
*.tar.gz
*.bundle

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Node.js
node_modules/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# MkDocs
site/

# Obsidian workspace (个人配置)
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# 日志
*.log
EOF
    echo "✓ .gitignore 创建完成"
else
    echo "✓ .gitignore 已存在"
fi

# 创建 README.md
if [ ! -f README.md ]; then
    cat > README.md << 'EOF'
# 工程师知识系统

一个集成化的个人知识管理平台，通过统一的 Git 仓库连接多个专业工具。

## 特性

- **五层知识层次结构**：从基础理论到个人洞察
- **Obsidian 知识图谱**：双向链接和可视化
- **Wiki.js 团队协作**：Web 编辑和权限管理
- **MkDocs 文档站点**：静态网站生成
- **AI 知识助手**：基于 RAG 的智能问答

## 快速开始

1. 初始化项目结构：
   ```bash
   bash scripts/init.sh
   ```

2. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置密码和 API 密钥
   ```

3. 启动所有服务：
   ```bash
   docker-compose up -d
   ```

4. 访问服务：
   - Gitea: http://localhost:3001
   - Wiki.js: http://localhost:3000
   - MkDocs: http://localhost:3002
   - AI 助手: http://localhost:3003

## 目录结构

```
knowledge-system/
├── knowledge/              # 统一的知识内容目录
│   ├── 01-foundations/    # 基础层
│   ├── 02-technologies/   # 技术层
│   ├── 03-architecture/   # 架构层
│   ├── 04-projects/       # 项目层
│   └── 05-insights/       # 洞察层
├── .obsidian/             # Obsidian 配置
├── scripts/               # 自动化脚本
├── docker-compose.yml     # Docker 编排
└── .env                   # 环境变量配置
```

## 文档

详细文档请参考 `.kiro/specs/engineer-knowledge-system/` 目录。

EOF
    echo "✓ README.md 创建完成"
else
    echo "✓ README.md 已存在"
fi

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cp .env.example .env
    echo "✓ .env 文件创建完成"
    echo ""
    echo "⚠ 重要：请编辑 .env 文件设置安全的密码和 API 密钥"
    echo "  可以运行 'bash scripts/generate-secrets.sh' 生成安全密钥"
else
    echo "✓ .env 文件已存在"
fi

echo ""
echo "=========================================="
echo "初始化完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件设置密码和 API 密钥"
echo "   提示：运行 'bash scripts/generate-secrets.sh' 生成安全密钥"
echo "2. 启动 Docker 服务: bash scripts/deploy.sh"
echo "3. 在 Obsidian 中打开 knowledge/ 目录"
echo ""
