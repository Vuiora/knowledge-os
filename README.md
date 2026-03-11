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
   - MkDocs: http://localhost:8080
   - AI 助手: http://localhost:8000

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

