# 知识系统配置指南

## 当前状态
✅ 所有服务已启动
- Gitea: http://localhost:3001
- Wiki.js: http://localhost:3000 (你当前在这里)
- MkDocs: http://localhost:3002
- AI 助手: http://localhost:3003

---

## 第一步：配置 Wiki.js (当前页面)

你现在看到的是 Wiki.js 欢迎页面。

### 操作步骤：

1. **点击 "ADMINISTRATION" 按钮**（右边的蓝色按钮）

2. **在管理员设置页面填写：**
   - Email: 你的邮箱（例如：admin@example.com）
   - Password: 设置一个强密码（自己记住）
   - Confirm Password: 再次输入密码
   - Site URL: 保持默认 `http://localhost:3000`

3. **点击 "Install" 完成安装**

4. **登录后，配置 Git 同步：**
   - 点击右上角头像 → "Administration"
   - 左侧菜单选择 "Storage"
   - 找到 "Git" 并点击
   - 配置如下：
     ```
     Authentication Type: Basic
     Repository URL: http://gitea:3000/admin/knowledge-system.git
     Branch: main
     Username: admin (等会在 Gitea 创建的用户名)
     Password: (等会在 Gitea 设置的密码)
     Local Repository Path: /wiki/data/repo
     Sync Direction: Sync ← Remote (Pull)
     Sync Interval: PT5M (每5分钟同步一次)
     Default Author Email: wiki@example.com
     Default Author Name: Wiki.js
     ```
   - 先不要点击 "Apply"，等 Gitea 配置完成后再回来

---

## 第二步：配置 Gitea

### 操作步骤：

1. **打开新标签页访问：http://localhost:3001**

2. **首次访问会看到 Gitea 安装页面**

3. **数据库设置（已自动配置，不需要修改）：**
   - 数据库类型: PostgreSQL
   - 主机: db:5432
   - 用户名: gitea
   - 密码: (已配置)
   - 数据库名: gitea

4. **一般设置：**
   - 站点名称: 知识系统 Git 仓库
   - 仓库根目录: /data/git/repositories
   - Git LFS 根目录: /data/git/lfs
   - 运行系统用户: git
   - SSH 服务器域名: localhost
   - SSH 端口: 2222
   - HTTP 端口: 3000
   - 应用 URL: http://localhost:3001/
   - 日志路径: /data/gitea/log

5. **可选设置（展开）：**
   - 邮件设置: 可以跳过
   - 服务器和第三方服务设置: 保持默认
   - 管理员账号设置（重要！）：
     ```
     管理员用户名: admin
     密码: 设置一个强密码（记住这个密码！）
     确认密码: 再次输入
     邮箱地址: admin@example.com
     ```

6. **点击 "立即安装"**

7. **安装完成后会自动登录**

---

## 第三步：在 Gitea 中创建知识仓库

1. **登录 Gitea 后，点击右上角 "+" → "新建仓库"**

2. **填写仓库信息：**
   - 仓库名称: `knowledge-system`
   - 可见性: 私有
   - 描述: 工程师知识管理系统
   - 不要勾选 "使用 README 文件初始化仓库"
   - 不要勾选 ".gitignore"
   - 不要勾选 "许可证"

3. **点击 "创建仓库"**

4. **记下仓库 URL（会显示在页面上）：**
   ```
   http://localhost:3001/admin/knowledge-system.git
   ```

---

## 第四步：推送本地代码到 Gitea

在你的项目目录打开终端（PowerShell），执行：

```powershell
# 添加 Gitea 远程仓库
git remote remove origin  # 如果之前有 origin，先删除
git remote add origin http://localhost:3001/admin/knowledge-system.git

# 提交所有文件
git add .
git commit -m "Initial commit: Knowledge system setup"

# 推送到 Gitea
git push -u origin main
```

推送时会要求输入用户名和密码：
- 用户名: `admin`
- 密码: 你在 Gitea 设置的密码

---

## 第五步：配置 Gitea Webhook

1. **在 Gitea 仓库页面，点击 "设置" → "管理 Web 钩子"**

2. **点击 "添加 Web 钩子" → "Gitea"**

3. **配置 Webhook：**
   - 目标 URL: `http://webhook-handler:9000/hooks/knowledge-sync`
   - HTTP 方法: POST
   - POST Content Type: application/json
   - 密钥文本: `RnOO36LJ19hIcbsu5e8oeHilKIXXBRlN` (从 .env 文件中复制)
   - 触发条件: 勾选 "推送事件"
   - 激活: 勾选

4. **点击 "添加 Web 钩子"**

5. **测试 Webhook：**
   - 点击刚创建的 Webhook
   - 点击 "测试推送"
   - 查看是否返回成功

---

## 第六步：回到 Wiki.js 配置 Git 同步

1. **回到 Wiki.js 管理界面**

2. **导航到 "Storage" → "Git"**

3. **填写配置（使用你在 Gitea 设置的密码）：**
   ```
   Repository URL: http://gitea:3000/admin/knowledge-system.git
   Branch: main
   Username: admin
   Password: [你的 Gitea 密码]
   ```

4. **点击 "Apply"**

5. **点击 "Execute Sync" 测试同步**

---

## 第七步：配置 Obsidian（可选）

1. **下载并安装 Obsidian：https://obsidian.md/**

2. **打开 Obsidian，选择 "打开文件夹作为仓库"**

3. **选择项目中的 `knowledge/` 目录**

4. **安装 Obsidian Git 插件：**
   - 打开设置（Ctrl+,）
   - 点击 "社区插件"
   - 关闭 "安全模式"
   - 点击 "浏览"
   - 搜索 "Obsidian Git"
   - 点击 "安装" → "启用"

5. **配置 Obsidian Git：**
   - 打开设置 → Obsidian Git
   - Vault backup interval: 10 (每10分钟自动备份)
   - Auto pull interval: 10 (每10分钟自动拉取)
   - Pull updates on startup: 开启
   - Pull before push: 开启
   - Commit message: `vault backup: {{date}}`

---

## 验证部署

### 测试完整工作流：

1. **在 `knowledge/` 目录创建测试文件：**
   ```bash
   echo "# 测试文档" > knowledge/test.md
   git add knowledge/test.md
   git commit -m "Test: 添加测试文档"
   git push
   ```

2. **检查各服务：**
   - Gitea (http://localhost:3001): 查看是否有新提交
   - Wiki.js (http://localhost:3000): 等待5分钟后查看是否同步
   - MkDocs (http://localhost:3002): 查看文档站点
   - AI 助手健康检查: http://localhost:3003/health

---

## 服务访问地址总览

| 服务 | 地址 | 用途 |
|------|------|------|
| Gitea | http://localhost:3001 | Git 版本控制 |
| Wiki.js | http://localhost:3000 | 团队知识库 |
| MkDocs | http://localhost:3002 | 文档站点 |
| AI 助手 | http://localhost:3003 | 智能问答 |
| Qdrant | http://localhost:6333 | 向量数据库 |
| Webhook | http://localhost:9000 | 自动化处理 |

---

## 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

---

## 下一步

配置完成后，你可以：
1. 在 Obsidian 中创建和编辑笔记
2. 在 Wiki.js 中协作和查看文档
3. 使用 AI 助手进行智能搜索
4. 在 MkDocs 中发布精美的文档站点

开始构建你的知识库吧！🚀
