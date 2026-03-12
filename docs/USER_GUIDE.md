# 用户指南 (User Guide)

## 目录

- [Obsidian 使用指南](#obsidian-使用指南)
- [Wiki.js 使用指南](#wikijs-使用指南)
- [AI 助手使用指南](#ai-助手使用指南)
- [日常工作流](#日常工作流)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## Obsidian 使用指南

### 简介

Obsidian 是你的个人知识图谱工具，用于创建、编辑和连接知识笔记。它是整个知识系统的核心入口。

### 基础操作

#### 1. 打开 Vault

1. 启动 Obsidian
2. 选择"打开文件夹作为仓库"
3. 导航到 `knowledge-system/knowledge/` 目录
4. 点击"打开"

#### 2. 创建新笔记

**方法一：通过文件浏览器**
1. 在左侧文件浏览器中，右键点击目标文件夹
2. 选择"新建笔记"
3. 输入文件名（无需 .md 扩展名）

**方法二：通过快捷键**
1. 按 `Ctrl+N`（Windows/Linux）或 `Cmd+N`（Mac）
2. 输入笔记标题
3. 笔记会创建在当前选中的文件夹中

**方法三：通过双向链接**
1. 在任何笔记中输入 `[[新笔记名称]]`
2. 点击链接
3. Obsidian 会自动创建新笔记

#### 3. 编辑笔记

Obsidian 使用 Markdown 语法：

```markdown
# 一级标题
## 二级标题
### 三级标题

**粗体文本**
*斜体文本*
~~删除线~~

- 无序列表项 1
- 无序列表项 2

1. 有序列表项 1
2. 有序列表项 2

[链接文本](https://example.com)
![图片](image.png)

`行内代码`

```python
# 代码块
def hello():
    print("Hello, World!")
```

> 引用文本

---

表格：
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
```

### 双向链接

双向链接是 Obsidian 的核心功能，用于构建知识图谱。

#### 创建链接

```markdown
# 基本链接
[[目标笔记名称]]

# 带显示文本的链接
[[目标笔记名称|显示文本]]

# 链接到标题
[[目标笔记名称#标题]]

# 链接到块
[[目标笔记名称#^block-id]]
```

#### 示例

```markdown
# STM32 DMA 原理

DMA（Direct Memory Access）是一种数据传输方式，允许外设直接访问内存。

相关概念：
- [[DMA 控制器]]
- [[内存映射]]
- [[中断处理]]

在 [[STM32F4]] 系列中，DMA 有以下特点：
- 支持 [[循环模式]]
- 支持 [[双缓冲模式]]

参考项目：[[智能手环项目#DMA配置]]
```

### 知识图谱

#### 查看图谱

1. 点击右侧面板的"图谱视图"图标
2. 或按 `Ctrl+G`

#### 图谱操作

- **缩放**：鼠标滚轮
- **平移**：拖动背景
- **聚焦节点**：点击节点
- **查看连接**：悬停在节点上

#### 图谱过滤

在图谱视图中，可以过滤显示的笔记：

- **按标签过滤**：在搜索框输入 `tag:#标签名`
- **按路径过滤**：输入文件夹路径
- **按深度过滤**：调整"深度"滑块

### 标签系统

#### 添加标签

```markdown
# 在笔记中添加标签
#嵌入式 #STM32 #DMA

# 或在 YAML 前置元数据中
---
tags:
  - 嵌入式
  - STM32
  - DMA
---
```

#### 查找标签

1. 点击左侧的"标签"面板
2. 查看所有标签及其使用次数
3. 点击标签查看所有相关笔记

### 模板

#### 创建模板

1. 在 `knowledge/` 目录下创建 `_templates/` 文件夹
2. 创建模板文件，例如 `技术笔记模板.md`：

```markdown
---
tags: []
created: {{date}}
updated: {{date}}
---

# {{title}}

## 概述

## 核心概念

## 示例

## 相关资源

- [[]]

## 参考文献
```

#### 使用模板

1. 安装 Templater 插件
2. 配置模板文件夹路径
3. 创建新笔记时，按 `Alt+E` 插入模板

### Git 同步

#### 安装 Obsidian Git 插件

1. 打开设置 → 社区插件
2. 关闭安全模式
3. 浏览社区插件
4. 搜索 "Obsidian Git"
5. 安装并启用

#### 配置自动同步

1. 打开设置 → Obsidian Git
2. 配置：
   - **自动备份间隔**：10 分钟
   - **自动拉取间隔**：10 分钟
   - **启动时自动拉取**：开启
   - **推送前拉取**：开启
   - **提交消息**：`vault backup: {{date}}`
   - **禁用推送**：关闭

#### 手动同步

- **提交并推送**：`Ctrl+P` → "Obsidian Git: Commit and push"
- **仅拉取**：`Ctrl+P` → "Obsidian Git: Pull"
- **查看更改**：`Ctrl+P` → "Obsidian Git: Open source control view"

### 推荐插件

#### 1. Dataview

用于查询和展示笔记数据。

**安装**：社区插件 → 搜索 "Dataview"

**示例**：

```markdown
# 列出所有嵌入式相关笔记
```dataview
LIST
FROM #嵌入式
SORT file.mtime DESC
```

# 表格视图
```dataview
TABLE tags, created, updated
FROM "02-technologies/embedded"
SORT created DESC
```
```

#### 2. Calendar

日记和时间线管理。

**安装**：社区插件 → 搜索 "Calendar"

**使用**：
- 点击日历上的日期创建日记
- 查看笔记创建时间线

#### 3. Excalidraw

绘制图表和示意图。

**安装**：社区插件 → 搜索 "Excalidraw"

**使用**：
- 创建 `.excalidraw` 文件
- 绘制架构图、流程图等
- 嵌入到笔记中

#### 4. Mind Map

思维导图视图。

**安装**：社区插件 → 搜索 "Mind Map"

**使用**：
- 打开任何笔记
- 点击"思维导图"图标
- 查看笔记的思维导图结构

### 快捷键

| 功能 | Windows/Linux | Mac |
|------|---------------|-----|
| 新建笔记 | `Ctrl+N` | `Cmd+N` |
| 快速切换 | `Ctrl+O` | `Cmd+O` |
| 搜索 | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| 命令面板 | `Ctrl+P` | `Cmd+P` |
| 图谱视图 | `Ctrl+G` | `Cmd+G` |
| 切换编辑/预览 | `Ctrl+E` | `Cmd+E` |
| 返回 | `Ctrl+Alt+←` | `Cmd+Opt+←` |
| 前进 | `Ctrl+Alt+→` | `Cmd+Opt+→` |

### 最佳实践

#### 1. 文件组织

遵循五层知识结构：

```
knowledge/
├── 01-foundations/      # 基础理论
├── 02-technologies/     # 具体技术
├── 03-architecture/     # 架构设计
├── 04-projects/         # 项目经验
└── 05-insights/         # 个人洞察
```

#### 2. 命名规范

- 使用描述性名称：`STM32-DMA原理.md` 而非 `笔记1.md`
- 使用连字符或下划线分隔单词
- 避免特殊字符：`/ \ : * ? " < > |`

#### 3. 链接策略

- 创建笔记时就添加相关链接
- 定期回顾并补充链接
- 使用"未链接提及"功能发现潜在连接

#### 4. 标签使用

- 使用层次化标签：`#技术/嵌入式/STM32`
- 保持标签一致性
- 不要过度使用标签（3-5 个为宜）

## Wiki.js 使用指南

### 简介

Wiki.js 是团队协作知识库，提供 Web 界面用于查看、编辑和管理文档。它自动同步 Git 仓库中的内容。

### 访问 Wiki.js

1. 打开浏览器
2. 访问 http://localhost:3000（或配置的域名）
3. 使用管理员账户登录

### 浏览文档

#### 主页

- 显示最近更新的页面
- 快速搜索框
- 导航菜单

#### 导航

- **侧边栏**：显示文档树结构
- **面包屑**：显示当前位置
- **搜索**：全文搜索功能

#### 搜索

1. 点击顶部搜索框
2. 输入关键词
3. 查看搜索结果
4. 支持高级搜索语法：
   - `"精确匹配"`
   - `tag:标签名`
   - `path:路径`

### 编辑文档

#### 创建新页面

1. 点击右上角 "+" 按钮
2. 选择"新建页面"
3. 填写：
   - **路径**：页面 URL 路径
   - **标题**：页面标题
   - **描述**：页面描述（可选）
   - **标签**：添加标签
4. 选择编辑器类型：
   - **Markdown**：推荐，与 Obsidian 兼容
   - **可视化编辑器**：所见即所得
   - **代码编辑器**：HTML/CSS
5. 编写内容
6. 点击"创建"

#### 编辑现有页面

1. 打开要编辑的页面
2. 点击右上角"编辑"按钮
3. 修改内容
4. 点击"保存"
5. 填写提交消息（可选）

#### Markdown 编辑器

Wiki.js 的 Markdown 编辑器支持：

- 实时预览
- 语法高亮
- 表情符号 `:smile:`
- 数学公式（LaTeX）
- 图表（Mermaid）
- 任务列表

**示例**：

```markdown
# 标题

## 代码块

```python
def hello():
    print("Hello")
```

## 数学公式

行内公式：$E = mc^2$

块级公式：
$$
\int_{a}^{b} f(x) dx
$$

## 流程图

```mermaid
graph LR
    A[开始] --> B[处理]
    B --> C[结束]
```

## 任务列表

- [x] 已完成任务
- [ ] 待完成任务
```

### 文件管理

#### 上传文件

1. 编辑页面时，点击工具栏的"插入资源"
2. 选择"上传文件"
3. 拖放文件或点击选择
4. 文件会自动上传并插入链接

#### 管理资源

1. 点击右上角头像 → "管理"
2. 导航到"资源"
3. 查看、编辑、删除上传的文件

### 权限管理

#### 用户管理

1. 管理 → 用户
2. 查看所有用户
3. 添加新用户：
   - 邮箱
   - 姓名
   - 密码
   - 用户组

#### 用户组

1. 管理 → 用户组
2. 创建用户组：
   - **管理员**：完全控制
   - **编辑者**：可编辑所有页面
   - **查看者**：只读访问
3. 配置权限：
   - 读取
   - 写入
   - 管理
   - 删除

#### 页面权限

1. 编辑页面
2. 点击"权限"标签
3. 设置：
   - 继承父页面权限
   - 或自定义权限规则

### Git 同步

#### 查看同步状态

1. 管理 → 存储
2. 查看 Git 存储状态
3. 显示：
   - 最后同步时间
   - 同步状态
   - 错误信息（如有）

#### 手动同步

1. 管理 → 存储 → Git
2. 点击"执行同步"
3. 等待同步完成

#### 同步配置

1. 管理 → 存储 → Git → 配置
2. 设置：
   - **同步间隔**：`PT5M`（5 分钟）
   - **同步方向**：
     - `Sync ← Remote`：仅拉取
     - `Sync → Remote`：仅推送
     - `Sync ↔ Remote`：双向同步
   - **默认作者**：提交时的作者信息

### 搜索引擎

#### 配置搜索

1. 管理 → 搜索引擎
2. 选择搜索引擎：
   - **数据库**：基本搜索
   - **Elasticsearch**：高级搜索
   - **Algolia**：云搜索
3. 重建索引

#### 搜索技巧

- **精确匹配**：`"STM32 DMA"`
- **排除词**：`STM32 -F1`
- **标签搜索**：`tag:嵌入式`
- **路径搜索**：`path:02-technologies`

### 主题和外观

#### 更改主题

1. 管理 → 主题
2. 选择主题：
   - Default（默认）
   - Dark（深色）
   - 自定义主题
3. 应用

#### 自定义 CSS

1. 管理 → 主题 → 自定义 CSS
2. 添加自定义样式
3. 保存

### 导出和备份

#### 导出页面

1. 打开页面
2. 点击右上角"..."菜单
3. 选择"导出"
4. 选择格式：
   - Markdown
   - HTML
   - PDF

#### 备份整个 Wiki

Wiki.js 的内容存储在 Git 仓库中，备份 Git 仓库即可：

```bash
cd knowledge-system
git bundle create wiki-backup.bundle --all
```

### API 使用

Wiki.js 提供 GraphQL API 用于程序化访问。

#### 获取 API 密钥

1. 管理 → API 访问
2. 创建新密钥
3. 设置权限范围
4. 保存密钥（只显示一次）

#### API 示例

```bash
# 查询页面列表
curl -X POST http://localhost:3000/graphql \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ pages { list { id path title } } }"
  }'

# 创建页面
curl -X POST http://localhost:3000/graphql \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { pages { create(content: \"# Test\", path: \"test\", title: \"Test\") { responseResult { succeeded } } } }"
  }'
```

## AI 助手使用指南

### 简介

AI 助手基于 RAG（检索增强生成）技术，能够根据你的知识库内容回答问题，提供智能搜索和知识检索。

### 访问 AI 助手

AI 助手提供 REST API 接口：

- **基础 URL**：http://localhost:8000
- **健康检查**：http://localhost:8000/health
- **API 文档**：http://localhost:8000/docs

### 基本查询

#### 使用 curl

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "STM32 DMA 的工作原理是什么？"
  }'
```

#### 响应格式

```json
{
  "answer": "STM32 DMA（直接内存访问）是一种数据传输方式...",
  "sources": [
    {
      "file_path": "knowledge/02-technologies/embedded/mcu/stm32-dma.md",
      "content": "DMA 控制器可以在不占用 CPU 的情况下...",
      "score": 0.89
    },
    {
      "file_path": "knowledge/04-projects/smart-ring/dma-config.md",
      "content": "在智能手环项目中，我们使用 DMA 传输传感器数据...",
      "score": 0.76
    }
  ],
  "metadata": {
    "query_time": 0.234,
    "model": "gpt-3.5-turbo",
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
  }
}
```

### 高级查询

#### 指定搜索范围

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "FreeRTOS 任务调度",
    "filter": {
      "layer": "02-technologies",
      "tags": ["嵌入式", "RTOS"]
    },
    "limit": 5
  }'
```

#### 调整相关度阈值

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "BLE 协议栈",
    "score_threshold": 0.8,
    "limit": 3
  }'
```

### 语义搜索

纯语义搜索，不生成答案：

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "低功耗设计",
    "limit": 10
  }'
```

响应：

```json
{
  "results": [
    {
      "file_path": "knowledge/02-technologies/embedded/low-power.md",
      "content": "低功耗设计的核心原则...",
      "score": 0.92
    },
    ...
  ]
}
```

### 更新嵌入

当添加新文档或修改现有文档后，需要更新嵌入向量：

```bash
# 自动更新（通过 Webhook 触发）
# 无需手动操作

# 手动触发更新
curl -X POST http://localhost:8000/api/update-embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      "knowledge/02-technologies/embedded/new-doc.md"
    ]
  }'

# 全量重建索引
curl -X POST http://localhost:8000/api/rebuild-index
```

### 查看索引状态

```bash
curl http://localhost:8000/api/embeddings/status
```

响应：

```json
{
  "total_documents": 1234,
  "total_chunks": 5678,
  "last_update": "2026-03-10T14:30:00Z",
  "index_size_mb": 45.6,
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
}
```

### 使用 Python 客户端

创建简单的 Python 客户端：

```python
import requests

class KnowledgeAssistant:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def query(self, question, **kwargs):
        """查询知识库"""
        response = requests.post(
            f"{self.base_url}/api/query",
            json={"question": question, **kwargs}
        )
        return response.json()
    
    def search(self, query, limit=10):
        """语义搜索"""
        response = requests.post(
            f"{self.base_url}/api/search",
            json={"query": query, "limit": limit}
        )
        return response.json()

# 使用示例
assistant = KnowledgeAssistant()

# 查询
result = assistant.query("STM32 DMA 原理")
print(result["answer"])

# 搜索
results = assistant.search("低功耗设计", limit=5)
for r in results["results"]:
    print(f"{r['file_path']}: {r['score']:.2f}")
```

### 集成到应用

#### Web 应用集成

```javascript
// JavaScript 示例
async function queryKnowledge(question) {
    const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question })
    });
    
    const data = await response.json();
    return data;
}

// 使用
queryKnowledge("FreeRTOS 任务优先级")
    .then(result => {
        console.log("答案:", result.answer);
        console.log("来源:", result.sources);
    });
```

#### 命令行工具

创建 `scripts/ask.sh`：

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "用法: ./ask.sh '你的问题'"
    exit 1
fi

curl -s -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"$1\"}" | \
  jq -r '.answer'
```

使用：

```bash
chmod +x scripts/ask.sh
./scripts/ask.sh "STM32 DMA 原理"
```

### 优化查询效果

#### 1. 提问技巧

**好的问题**：
- ✅ "STM32 DMA 的工作原理和配置步骤是什么？"
- ✅ "FreeRTOS 中如何实现任务间通信？"
- ✅ "BLE 协议栈的层次结构是怎样的？"

**不好的问题**：
- ❌ "DMA"（太简短）
- ❌ "告诉我所有关于 STM32 的信息"（太宽泛）
- ❌ "这个怎么做？"（缺乏上下文）

#### 2. 使用过滤器

```bash
# 只搜索嵌入式相关内容
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "低功耗设计",
    "filter": {
      "layer": "02-technologies/embedded"
    }
  }'
```

#### 3. 调整参数

- **limit**：返回的源文档数量（默认 5）
- **score_threshold**：相关度阈值（0-1，默认 0.7）
- **temperature**：生成答案的随机性（0-1，默认 0.7）

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "RTOS 调度算法",
    "limit": 10,
    "score_threshold": 0.75,
    "temperature": 0.5
  }'
```

### 监控和调试

#### 查看日志

```bash
# 查看 AI 助手日志
docker-compose logs -f ai-assistant

# 查看最近 100 行
docker-compose logs --tail=100 ai-assistant
```

#### 性能监控

```bash
# 查询统计
curl http://localhost:8000/api/stats

# 响应示例
{
  "total_queries": 1234,
  "avg_query_time": 0.234,
  "cache_hit_rate": 0.67,
  "uptime_seconds": 86400
}
```

## 日常工作流

### 场景 1：学习新技术

1. **在 Obsidian 中创建笔记**
   - 选择合适的层次（通常是 `02-technologies/`）
   - 创建新笔记，例如 `LoRa通信协议.md`

2. **记录学习内容**
   ```markdown
   # LoRa 通信协议
   
   ## 概述
   LoRa（Long Range）是一种低功耗广域网通信技术...
   
   ## 核心特性
   - 长距离通信（10+ km）
   - 低功耗
   - 抗干扰能力强
   
   ## 相关技术
   - [[LoRaWAN]]
   - [[Sub-GHz 无线通信]]
   - [[物联网协议栈]]
   
   ## 参考资源
   - [LoRa Alliance](https://lora-alliance.org/)
   ```

3. **添加双向链接**
   - 链接到相关概念
   - 链接到项目应用

4. **自动同步**
   - Obsidian Git 自动提交
   - Webhook 触发更新
   - AI 助手自动索引

5. **验证**
   - 在 Wiki.js 中查看
   - 使用 AI 助手查询

### 场景 2：项目文档

1. **创建项目目录**
   ```
   knowledge/04-projects/智能手环/
   ├── README.md
   ├── 需求分析.md
   ├── 架构设计.md
   ├── 硬件设计.md
   ├── 软件设计.md
   └── 测试报告.md
   ```

2. **记录项目信息**
   - 需求、设计、实现、测试
   - 链接到相关技术笔记
   - 添加图表和代码

3. **团队协作**
   - 推送到 Git
   - 团队成员在 Wiki.js 中查看
   - 通过 Git 进行协作编辑

4. **知识沉淀**
   - 提取通用知识到技术层
   - 总结经验到洞察层

### 场景 3：问题解决

1. **遇到问题**
   - 例如：STM32 DMA 传输出错

2. **查询 AI 助手**
   ```bash
   ./scripts/ask.sh "STM32 DMA 传输常见错误和解决方法"
   ```

3. **获取答案和源文档**
   - AI 助手返回答案
   - 提供相关文档链接

4. **深入学习**
   - 在 Obsidian 中打开源文档
   - 查看知识图谱中的相关概念

5. **记录解决方案**
   - 创建新笔记记录问题和解决方案
   - 链接到相关技术文档

### 场景 4：知识分享

1. **整理内容**
   - 在 Obsidian 中整理要分享的内容
   - 确保链接和格式正确

2. **发布到 Wiki**
   - 内容自动同步到 Wiki.js
   - 团队成员可以查看

3. **生成文档站点**
   - 将内容移至 `_site/` 目录
   - MkDocs 自动构建
   - 生成精美的静态网站

4. **对外发布**
   - 部署 MkDocs 站点到服务器
   - 或导出为 PDF 分享

## 最佳实践

### 1. 内容组织

#### 遵循五层结构

- **01-foundations/**：基础理论，不常变化
- **02-technologies/**：具体技术，持续更新
- **03-architecture/**：架构设计，经验总结
- **04-projects/**：项目实践，案例记录
- **05-insights/**：个人洞察，思考沉淀

#### 文件命名

- 使用描述性名称
- 保持一致性
- 避免特殊字符

#### 目录结构

```
02-technologies/embedded/
├── mcu/
│   ├── STM32/
│   │   ├── STM32-DMA.md
│   │   ├── STM32-GPIO.md
│   │   └── STM32-时钟系统.md
│   └── ESP32/
├── rtos/
│   ├── FreeRTOS/
│   └── Zephyr/
└── protocol/
    ├── I2C.md
    ├── SPI.md
    └── UART.md
```

### 2. 链接策略

#### 创建有意义的链接

```markdown
# 好的链接
[[STM32-DMA]] 提供了高效的数据传输方式

# 不好的链接
参考 [[这里]]
```

#### 使用层次化链接

```markdown
# 从具体到抽象
[[STM32F4]] → [[STM32系列]] → [[ARM Cortex-M]] → [[嵌入式处理器]]

# 从理论到实践
[[DMA原理]] → [[STM32-DMA配置]] → [[智能手环项目#DMA应用]]
```

#### 定期维护链接

- 使用"未链接提及"功能
- 修复断开的链接
- 补充缺失的链接

### 3. 标签使用

#### 标签层次

```markdown
# 使用层次化标签
#技术/嵌入式/MCU/STM32
#项目/智能手环/硬件
#洞察/工程实践/调试技巧
```

#### 标签一致性

维护标签列表：

```markdown
# 常用标签
- #嵌入式
- #STM32
- #FreeRTOS
- #低功耗
- #通信协议
- #项目经验
- #调试技巧
```

### 4. 版本控制

#### 提交消息规范

```bash
# 好的提交消息
git commit -m "添加：STM32 DMA 配置详解"
git commit -m "更新：FreeRTOS 任务调度章节"
git commit -m "修复：I2C 通信示例代码错误"

# 不好的提交消息
git commit -m "更新"
git commit -m "修改文件"
```

#### 分支策略

```bash
# 主分支
main - 稳定版本

# 功能分支（可选）
feature/new-topic - 新主题开发
fix/typo - 错误修复
```

### 5. 定期维护

#### 每周

- 回顾本周新增笔记
- 补充链接和标签
- 整理零散笔记

#### 每月

- 查看知识图谱
- 识别知识盲点
- 规划学习方向

#### 每季度

- 重构目录结构
- 归档过时内容
- 总结经验洞察

### 6. 备份策略

#### 自动备份

```bash
# 设置定时任务
crontab -e

# 每天凌晨 2 点备份
0 2 * * * /path/to/knowledge-system/scripts/backup.sh
```

#### 多地备份

- 本地备份
- 云端备份（GitHub/GitLab）
- 外部硬盘备份

## 常见问题

### Q1: Obsidian 同步失败怎么办？

**A**: 检查以下几点：
1. Git 远程仓库配置是否正确
2. 网络连接是否正常
3. 认证凭据是否有效
4. 查看 Obsidian Git 插件日志

手动测试：
```bash
cd knowledge-system
git pull
git push
```

### Q2: Wiki.js 未显示最新内容？

**A**: 
1. 检查 Git 同步状态：管理 → 存储 → Git
2. 手动触发同步
3. 查看同步日志
4. 验证 Git 仓库中有最新提交

### Q3: AI 助手返回不相关的结果？

**A**: 
1. 优化问题描述，提供更多上下文
2. 使用过滤器限制搜索范围
3. 调整相关度阈值
4. 检查文档是否已被索引

### Q4: 如何处理大文件？

**A**: 
1. 使用 Git LFS 存储大文件
2. 将大文件放在单独的目录
3. 在 `.gitignore` 中排除不必要的大文件
4. 考虑使用外部存储（如对象存储）

### Q5: 如何迁移现有笔记？

**A**: 
1. 将现有笔记复制到 `knowledge/` 目录
2. 按五层结构组织
3. 转换为 Markdown 格式（如需要）
4. 添加双向链接
5. 提交到 Git

### Q6: 多人协作时如何避免冲突？

**A**: 
1. 使用 Git 分支
2. 定期拉取最新更改
3. 避免同时编辑同一文件
4. 使用 Wiki.js 的锁定功能
5. 建立协作规范

### Q7: 如何优化搜索性能？

**A**: 
1. 定期重建索引
2. 清理无用文档
3. 优化文档大小（拆分大文件）
4. 增加服务器资源
5. 使用缓存

### Q8: 如何导出所有内容？

**A**: 
```bash
# 导出 Git 仓库
git bundle create knowledge-export.bundle --all

# 导出为 ZIP
zip -r knowledge-export.zip knowledge/

# 使用 MkDocs 生成 HTML
cd knowledge/_site
mkdocs build
```

### Q9: 如何自定义 AI 助手的回答风格？

**A**: 
编辑 AI 助手配置，修改系统提示词：

```python
# ai-assistant/config.py
SYSTEM_PROMPT = """
你是一个专业的技术助手，专注于嵌入式系统和软件工程。
回答时请：
1. 提供准确的技术信息
2. 引用具体的源文档
3. 使用清晰的技术术语
4. 提供实用的示例
"""
```

### Q10: 如何备份和恢复？

**A**: 
```bash
# 备份
bash scripts/backup.sh

# 恢复
bash scripts/restore.sh backups/knowledge-backup-20260310.tar.gz

# 验证
git log
docker-compose ps
```

## 获取帮助

- **文档**：查看 [README.md](../README.md) 和 [DEPLOYMENT.md](DEPLOYMENT.md)
- **日志**：`docker-compose logs -f`
- **社区**：GitHub Issues
- **支持**：联系技术支持

---

**祝你构建强大的知识系统！** 📚✨
