# Obsidian 配置目录

本目录包含 Obsidian 知识图谱的配置文件和插件设置。

## 目录结构

```
.obsidian/
├── app.json                    # Obsidian 应用程序设置
├── workspace.json              # 工作区布局配置
├── core-plugins.json           # 启用的核心插件列表
├── community-plugins.json      # 启用的社区插件列表
├── hotkeys.json               # 自定义快捷键配置
├── plugins/                   # 社区插件目录
│   └── obsidian-git/         # Obsidian Git 插件
│       ├── data.json         # 插件配置
│       ├── main.js           # 插件主文件
│       └── manifest.json     # 插件清单
├── OBSIDIAN-SETUP-GUIDE.md   # 详细配置指南（中文）
├── QUICK-START.md            # 快速开始指南（英文）
└── README.md                 # 本文件
```

## 配置文件说明

### app.json
包含 Obsidian 的全局应用设置，如：
- 编辑器行为（行号、换行等）
- 链接格式（相对路径、Markdown 链接）
- 主题和外观设置

### workspace.json
定义 Obsidian 的工作区布局，包括：
- 左侧边栏（文件浏览器、搜索）
- 右侧边栏（反向链接、标签、大纲）
- 编辑器面板布局

### core-plugins.json
列出启用的 Obsidian 核心插件：
- file-explorer（文件浏览器）
- global-search（全局搜索）
- graph（知识图谱）
- backlink（反向链接）
- 等等

### community-plugins.json
列出启用的社区插件：
- obsidian-git（Git 自动同步）
- dataview（数据查询）
- templater-obsidian（模板引擎）
- calendar（日历视图）

### hotkeys.json
自定义快捷键配置：
- `Ctrl/Cmd + Shift + K`：Git 提交
- `Ctrl/Cmd + Shift + P`：Git 推送
- `Ctrl/Cmd + Shift + L`：Git 拉取
- `Ctrl/Cmd + Shift + G`：打开图谱视图

### plugins/obsidian-git/data.json
Obsidian Git 插件的详细配置：
- 自动备份间隔：10 分钟
- 自动拉取间隔：10 分钟
- 提交消息格式：`vault backup: {{date}}`
- 同步策略：合并（merge）

## 使用说明

### 首次使用

1. 阅读 `OBSIDIAN-SETUP-GUIDE.md` 获取详细的配置步骤
2. 或查看 `QUICK-START.md` 快速开始

### 配置文件管理

**重要提示**：
- `.obsidian/workspace.json` 包含个人工作区布局，通常不应同步到 Git
- 其他配置文件可以在团队间共享
- 如果需要个性化配置，可以在 `.gitignore` 中排除特定文件

### 插件安装

社区插件需要通过 Obsidian 的插件市场安装：
1. 打开 Obsidian 设置
2. 进入 Community plugins
3. 搜索并安装所需插件
4. 插件文件会自动下载到 `plugins/` 目录

### 配置同步

如果在多台设备上使用 Obsidian：
1. 通过 Git 同步配置文件
2. 在新设备上打开 vault 后，Obsidian 会自动读取配置
3. 需要重新安装社区插件（配置会保留）

## 推荐工作流

### 日常使用
1. 打开 Obsidian（自动拉取最新更改）
2. 创建和编辑笔记
3. 使用双向链接连接概念
4. 每 10 分钟自动提交和推送

### 知识组织
1. 使用五层目录结构组织内容
2. 在每个目录创建索引文件
3. 使用标签和元数据增强可搜索性
4. 定期查看知识图谱，发现关联

### 团队协作
1. 通过 Git 共享知识内容
2. 使用 Wiki.js 进行团队协作编辑
3. 通过 MkDocs 发布公开文档
4. 使用 AI 助手进行智能检索

## 故障排除

### 配置文件损坏
如果配置文件损坏导致 Obsidian 无法启动：
1. 备份当前 `.obsidian/` 目录
2. 从 Git 历史恢复配置文件
3. 或删除 `.obsidian/` 目录，让 Obsidian 重新创建

### 插件冲突
如果插件导致问题：
1. 在安全模式下启动 Obsidian（禁用所有插件）
2. 逐个启用插件，找出问题插件
3. 更新或卸载问题插件

### Git 同步问题
参见 `OBSIDIAN-SETUP-GUIDE.md` 的"常见问题解决"部分

## 进一步定制

### 自定义主题
1. 在 Obsidian 设置中选择主题
2. 或安装社区主题
3. 主题设置会保存在 `app.json` 中

### 自定义 CSS
1. 创建 `snippets/` 目录
2. 添加 `.css` 文件
3. 在设置中启用 CSS 片段

### 自定义模板
1. 创建模板文件夹（如 `templates/`）
2. 在 Templater 插件中配置模板路径
3. 创建模板文件供重复使用

## 相关资源

- [Obsidian 官方文档](https://help.obsidian.md/)
- [Obsidian Git 插件](https://github.com/denolehov/obsidian-git)
- [Obsidian 社区论坛](https://forum.obsidian.md/)
- [工程师知识系统设计文档](../.kiro/specs/engineer-knowledge-system/design.md)

## 版本信息

- Obsidian 最低版本：0.12.12
- Obsidian Git 插件版本：2.23.0
- 配置创建日期：2024-03-11

---

**注意**：本配置是工程师知识系统的一部分，与 Gitea、Wiki.js、MkDocs 和 AI 助手集成。
