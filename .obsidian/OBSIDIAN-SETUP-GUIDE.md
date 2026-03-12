# Obsidian 配置指南

本指南将帮助您配置 Obsidian 以与工程师知识系统集成，实现自动 Git 同步。

## 前置要求

- 已安装 Obsidian Desktop（下载地址：https://obsidian.md/）
- 已完成 Gitea 服务器部署和仓库创建
- 已在本地克隆了 knowledge-system 仓库

## 第一步：打开 Vault

1. 启动 Obsidian
2. 点击左下角的 "Open another vault"（打开其他仓库）
3. 选择 "Open folder as vault"（将文件夹作为仓库打开）
4. 导航到您的 `knowledge-system/knowledge/` 目录
5. 点击 "Open"（打开）

**重要提示**：请确保打开的是 `knowledge/` 目录，而不是整个 `knowledge-system/` 目录。这样可以确保 Obsidian 只管理知识内容，而不会干扰其他配置文件。

## 第二步：启用社区插件

1. 打开 Obsidian 设置（点击左下角齿轮图标，或按 `Ctrl/Cmd + ,`）
2. 在左侧菜单中选择 "Community plugins"（社区插件）
3. 如果看到 "Restricted mode"（限制模式）提示，点击 "Turn off restricted mode"（关闭限制模式）
4. 点击 "Browse"（浏览）按钮

## 第三步：安装 Obsidian Git 插件

### 方法一：通过社区插件市场安装（推荐）

1. 在插件浏览器中搜索 "Obsidian Git"
2. 找到由 Denis Olehov 开发的 "Obsidian Git" 插件
3. 点击 "Install"（安装）
4. 安装完成后，点击 "Enable"（启用）

### 方法二：手动安装

如果无法访问社区插件市场，可以手动安装：

1. 访问 https://github.com/denolehov/obsidian-git/releases
2. 下载最新版本的 `main.js`、`manifest.json` 和 `styles.css`
3. 将这些文件复制到 `.obsidian/plugins/obsidian-git/` 目录
4. 重启 Obsidian
5. 在设置中启用 Obsidian Git 插件

## 第四步：配置 Git 远程仓库

### 4.1 配置 Git 用户信息（如果尚未配置）

打开终端，在 `knowledge-system/` 目录下执行：

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 4.2 添加 Gitea 远程仓库

如果尚未添加远程仓库：

```bash
# 替换为您的 Gitea 服务器地址和用户名
git remote add origin http://localhost:3001/admin/knowledge-system.git

# 或使用 SSH（推荐）
git remote add origin git@localhost:2222/admin/knowledge-system.git
```

### 4.3 配置 Git 凭据（HTTP 方式）

如果使用 HTTP 协议，可以配置凭据存储以避免每次输入密码：

**Windows:**
```bash
git config --global credential.helper wincred
```

**macOS:**
```bash
git config --global credential.helper osxkeychain
```

**Linux:**
```bash
git config --global credential.helper store
```

### 4.4 配置 SSH 密钥（SSH 方式，推荐）

1. 生成 SSH 密钥（如果尚未生成）：
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

2. 将公钥添加到 Gitea：
   - 复制公钥内容：`cat ~/.ssh/id_ed25519.pub`
   - 登录 Gitea Web 界面
   - 进入 Settings → SSH / GPG Keys
   - 点击 "Add Key"，粘贴公钥

3. 测试连接：
```bash
ssh -T git@localhost -p 2222
```

## 第五步：配置 Obsidian Git 插件

1. 打开 Obsidian 设置
2. 在左侧菜单中选择 "Community plugins"
3. 找到 "Obsidian Git" 并点击齿轮图标进入设置

### 推荐配置：

#### 基本设置

- **Commit message**（提交消息）：`vault backup: {{date}}`
  - 这将自动生成带时间戳的提交消息

- **Commit date format**（提交日期格式）：`YYYY-MM-DD HH:mm:ss`
  - 使用标准的日期时间格式

#### 自动备份设置

- **Vault backup interval (minutes)**（自动备份间隔）：`10`
  - 每 10 分钟自动提交更改
  - 可根据个人习惯调整（建议 5-30 分钟）

- **Auto pull interval (minutes)**（自动拉取间隔）：`10`
  - 每 10 分钟自动从远程仓库拉取更新
  - 确保与团队成员保持同步

- **Auto pull on boot**（启动时自动拉取）：`启用`
  - Obsidian 启动时自动拉取最新更改

- **Disable push**（禁用推送）：`禁用`
  - 确保更改会被推送到远程仓库

- **Pull updates on startup**（启动时拉取更新）：`启用`
  - 确保始终使用最新版本

#### 高级设置

- **Pull before push**（推送前先拉取）：`启用`
  - 避免推送冲突

- **Sync method**（同步方法）：`merge`
  - 使用合并策略处理冲突

- **Show status bar**（显示状态栏）：`启用`
  - 在底部状态栏显示 Git 状态

## 第六步：测试自动同步

### 6.1 创建测试文档

1. 在 Obsidian 中创建一个新的 Markdown 文件
2. 输入一些测试内容
3. 保存文件（`Ctrl/Cmd + S`）

### 6.2 手动触发同步

使用快捷键或命令面板：

- **提交更改**：`Ctrl/Cmd + Shift + K`
- **推送到远程**：`Ctrl/Cmd + Shift + P`
- **从远程拉取**：`Ctrl/Cmd + Shift + L`

或者打开命令面板（`Ctrl/Cmd + P`）并搜索：
- "Obsidian Git: Commit all changes"
- "Obsidian Git: Push"
- "Obsidian Git: Pull"

### 6.3 验证同步

1. 检查 Obsidian 底部状态栏，应该显示 Git 状态
2. 访问 Gitea Web 界面，确认新提交已出现
3. 检查 Wiki.js，确认文档已同步（可能需要等待几分钟）

## 第七步：配置其他推荐插件（可选）

### Dataview 插件

用于创建动态查询和数据视图：

1. 在社区插件中搜索 "Dataview"
2. 安装并启用
3. 可以创建如下查询：

\`\`\`dataview
LIST
FROM "02-technologies"
WHERE contains(file.tags, "#embedded")
SORT file.mtime DESC
\`\`\`

### Templater 插件

用于创建和使用模板：

1. 在社区插件中搜索 "Templater"
2. 安装并启用
3. 在设置中配置模板文件夹路径

### Calendar 插件

用于日记和时间线管理：

1. 在社区插件中搜索 "Calendar"
2. 安装并启用
3. 会在右侧边栏显示日历视图

## 常见问题解决

### 问题 1：无法推送到远程仓库

**错误信息**：`Authentication failed` 或 `Permission denied`

**解决方案**：
1. 检查 Git 凭据是否正确配置
2. 如果使用 SSH，确保 SSH 密钥已添加到 Gitea
3. 尝试在终端手动执行 `git push` 以诊断问题

### 问题 2：出现合并冲突

**错误信息**：`Merge conflict`

**解决方案**：
1. 打开终端，导航到 `knowledge-system/` 目录
2. 执行 `git status` 查看冲突文件
3. 手动编辑冲突文件，解决冲突标记（`<<<<<<<`, `=======`, `>>>>>>>`）
4. 执行 `git add .` 和 `git commit -m "Resolve merge conflict"`
5. 在 Obsidian 中使用 "Obsidian Git: Push" 推送更改

### 问题 3：自动同步不工作

**解决方案**：
1. 检查 Obsidian Git 插件是否已启用
2. 检查自动备份间隔设置是否正确
3. 查看 Obsidian 开发者控制台（`Ctrl/Cmd + Shift + I`）是否有错误信息
4. 尝试手动触发同步以测试连接

### 问题 4：.obsidian 配置文件冲突

**解决方案**：
1. `.obsidian/` 目录包含个人配置，通常不应同步
2. 如果需要同步配置，确保团队成员使用相同的插件版本
3. 可以在 `.gitignore` 中排除某些个人配置文件：
   ```
   .obsidian/workspace.json
   .obsidian/workspace-mobile.json
   ```

## 工作流建议

### 日常使用流程

1. **早上开始工作**：
   - 打开 Obsidian（自动拉取最新更改）
   - 检查状态栏确认同步成功

2. **创建和编辑内容**：
   - 在适当的知识层次目录下创建文档
   - 使用 `[[双向链接]]` 连接相关概念
   - 添加标签以便分类和搜索

3. **定期保存**：
   - Obsidian Git 会每 10 分钟自动提交和推送
   - 也可以手动触发同步（`Ctrl/Cmd + Shift + K` 然后 `Ctrl/Cmd + Shift + P`）

4. **结束工作**：
   - 确保所有更改已提交（检查状态栏）
   - 关闭 Obsidian

### 知识组织最佳实践

1. **使用五层结构**：
   - `01-foundations/`：基础理论知识
   - `02-technologies/`：具体技术和工具
   - `03-architecture/`：架构设计和模式
   - `04-projects/`：项目经验和案例
   - `05-insights/`：个人洞察和总结

2. **创建索引文件**：
   - 在每个目录下创建 `README.md` 或 `index.md`
   - 列出该目录下的主要内容和链接

3. **使用双向链接**：
   - 连接相关概念：`[[TCP协议]]` 和 `[[网络编程]]`
   - 创建知识图谱，便于发现关联

4. **添加元数据**：
   ```markdown
   ---
   tags: [embedded, stm32, driver]
   created: 2024-03-10
   updated: 2024-03-11
   ---
   ```

5. **定期回顾**：
   - 使用图谱视图（`Ctrl/Cmd + Shift + G`）查看知识网络
   - 识别孤立节点，添加更多链接

## 与其他工具的集成

### Wiki.js 同步

- Obsidian 中的更改会通过 Git 自动同步到 Wiki.js
- 同步延迟通常为 5-10 分钟（取决于 Wiki.js 配置）
- 可以在 Wiki.js 中查看和编辑相同的内容

### MkDocs 文档站点

- 选择性地将成熟的内容发布到 `_site/` 目录
- MkDocs 会自动构建并生成静态网站
- 适合公开分享的技术文档

### AI 知识助手

- 所有在 Obsidian 中创建的内容都会被 AI 助手索引
- 可以通过 AI 助手 API 查询知识库
- 支持语义搜索和智能问答

## 快捷键参考

### Obsidian 内置快捷键

- `Ctrl/Cmd + N`：新建笔记
- `Ctrl/Cmd + O`：快速切换笔记
- `Ctrl/Cmd + P`：命令面板
- `Ctrl/Cmd + Shift + F`：全局搜索
- `Ctrl/Cmd + Shift + G`：打开图谱视图
- `Ctrl/Cmd + E`：切换编辑/预览模式
- `Ctrl/Cmd + ,`：打开设置

### Obsidian Git 快捷键

- `Ctrl/Cmd + Shift + K`：提交所有更改
- `Ctrl/Cmd + Shift + P`：推送到远程
- `Ctrl/Cmd + Shift + L`：从远程拉取

## 进一步学习

- Obsidian 官方文档：https://help.obsidian.md/
- Obsidian Git 插件文档：https://github.com/denolehov/obsidian-git
- Obsidian 社区论坛：https://forum.obsidian.md/
- Obsidian 中文社区：https://forum-zh.obsidian.md/

## 支持

如果遇到问题，请：
1. 查看本指南的"常见问题解决"部分
2. 检查 Obsidian 开发者控制台的错误信息
3. 查看 Git 日志：`git log --oneline -10`
4. 联系系统管理员或查阅项目文档

---

**祝您使用愉快！开始构建您的知识图谱吧！** 🚀
