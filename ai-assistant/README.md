# AI 知识助手服务

AI 知识助手服务负责文档嵌入生成、向量存储和知识检索。

## 功能概述

### 已实现功能（任务 7）

1. **文档处理模块** (`document_processor.py`)
   - Markdown 文件读取
   - 文档分块（Chunking）支持可配置的块大小和重叠
   - 智能句子边界检测
   - 元数据提取（标题、标签、知识层次、文件统计）

2. **嵌入生成器** (`embedding_generator.py`)
   - Sentence Transformers 集成
   - 批处理支持（可配置批大小）
   - 缓存机制（基于 MD5 哈希）
   - 支持多语言模型（默认：paraphrase-multilingual-MiniLM-L12-v2）

3. **Gitea API 客户端** (`gitea_client.py`)
   - 仓库文件列表获取
   - 文件内容读取（Base64 解码）
   - Webhook 事件解析
   - 知识文件过滤

4. **主应用服务** (`app.py`)
   - FastAPI Web 服务
   - `/api/update-embeddings` - 更新文件嵌入向量
   - `/api/query` - 查询知识库（基础实现）
   - `/api/embeddings/status` - 获取嵌入状态
   - `/health` - 健康检查

### 已实现功能（任务 8）

5. **RAG 查询引擎** (`rag_engine.py`)
   - 问题嵌入生成
   - 向量相似度搜索
   - 智能上下文构建（支持长度限制）
   - LLM 集成（OpenAI API）
   - 源文档引用格式化
   - 完整的 RAG 查询流程

6. **增强的 API 端点**
   - `/api/query` - 完整的 RAG 查询实现
   - `/api/rag/info` - RAG 引擎信息
   - 改进的健康检查（包含 RAG 引擎状态）

## 架构

```
ai-assistant/
├── app.py                      # FastAPI 主应用
├── document_processor.py       # 文档处理模块
├── embedding_generator.py      # 嵌入生成器
├── gitea_client.py            # Gitea API 客户端
├── qdrant_client_wrapper.py   # Qdrant 向量数据库封装
├── rag_engine.py              # RAG 查询引擎
├── requirements.txt           # Python 依赖
├── Dockerfile                 # Docker 镜像定义
├── test_modules.py            # 模块测试
├── test_rag_engine.py         # RAG 引擎测试
└── README.md                  # 本文档
```

## 工作流程

### 嵌入更新流程

1. Webhook Handler 接收 Gitea push 事件
2. 提取变更的知识文件列表
3. 调用 `/api/update-embeddings` 端点
4. AI 助手处理流程：
   - 从 Gitea 获取文件内容
   - 提取元数据（标题、层次、标签等）
   - 将文档分块（512 字符，50 字符重叠）
   - 生成嵌入向量（批处理）
   - 存储到 Qdrant 向量数据库

### RAG 查询流程（完整版）

1. 用户发送查询请求到 `/api/query`
2. RAG 引擎生成查询文本的嵌入向量
3. 在 Qdrant 中搜索相似向量（可配置阈值和数量）
4. 构建上下文（智能长度控制，保留完整文档）
5. 使用 LLM（OpenAI API）基于上下文生成答案
6. 返回答案和源文档引用（包含文件路径、标题、相关度评分）

## API 端点

### POST /api/update-embeddings

更新指定文件的嵌入向量。

**请求体：**
```json
{
  "files": [
    "knowledge/01-foundations/algorithm/sorting.md",
    "knowledge/02-technologies/ai/transformers.md"
  ]
}
```

**响应：**
```json
{
  "status": "completed",
  "message": "Embeddings updated successfully",
  "files_processed": 2,
  "chunks_created": 15,
  "embeddings_stored": 15
}
```

### POST /api/query

查询知识库。

**请求体：**
```json
{
  "question": "什么是快速排序算法？",
  "limit": 5,
  "score_threshold": 0.7
}
```

**响应：**
```json
{
  "answer": "快速排序是一种高效的分治排序算法。它的基本思想是选择一个基准元素，将数组分为两部分：小于基准的元素和大于基准的元素，然后递归地对这两部分进行排序。快速排序的平均时间复杂度为 O(n log n)，但在最坏情况下会退化到 O(n²)。",
  "sources": [
    {
      "file_path": "knowledge/01-foundations/algorithm/sorting.md",
      "title": "排序算法",
      "layer": "01-foundations",
      "score": 0.89,
      "content_preview": "快速排序是一种分治算法，由 C.A.R. Hoare 在 1960 年提出..."
    }
  ]
}
```

### GET /api/embeddings/status

获取嵌入向量和缓存状态。

**响应：**
```json
{
  "status": "ok",
  "collection": {
    "name": 384,
    "vectors_count": 1250,
    "points_count": 1250,
    "status": "green"
  },
  "cache": {
    "enabled": true,
    "cache_dir": "/app/cache",
    "file_count": 856,
    "total_size_mb": 12.5
  },
  "model": {
    "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
    "embedding_dimension": 384,
    "batch_size": 32,
    "cache_enabled": true
  }
}
```

### GET /health

健康检查端点。

**响应：**
```json
{
  "status": "healthy",
  "components": {
    "document_processor": "ok",
    "embedding_generator": {
      "status": "ok",
      "model": "paraphrase-multilingual-MiniLM-L12-v2",
      "dimension": 384
    },
    "gitea": {
      "healthy": true,
      "base_url": "http://gitea:3000",
      "repo_path": "admin/knowledge-system"
    },
    "qdrant": {
      "status": "ok"
    },
    "rag_engine": {
      "status": "ok",
      "model": "gpt-3.5-turbo",
      "openai_configured": true
    }
  }
}
```

### GET /api/rag/info

获取 RAG 引擎配置信息。

**响应：**
```json
{
  "status": "ok",
  "engine": {
    "model": "gpt-3.5-turbo",
    "max_context_length": 3000,
    "temperature": 0.7,
    "openai_configured": true,
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
    "embedding_dimension": 384
  }
}
```

## 配置

通过环境变量配置服务：

```bash
# Qdrant 配置
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Gitea 配置
GITEA_URL=http://gitea:3000
GITEA_TOKEN=your_api_token
REPO_PATH=admin/knowledge-system

# 嵌入模型配置
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# 缓存配置
CACHE_DIR=/app/cache

# OpenAI 配置
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo  # 或 gpt-4
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t knowledge-ai-assistant .

# 运行容器
docker run -d \
  --name ai-assistant \
  -p 8000:8000 \
  -e QDRANT_HOST=qdrant \
  -e GITEA_URL=http://gitea:3000 \
  -e GITEA_TOKEN=your_token \
  -v ./cache:/app/cache \
  knowledge-ai-assistant
```

### Docker Compose

服务已在 `docker-compose.yml` 中定义：

```bash
docker-compose up -d ai-assistant
```

## 测试

运行模块测试：

```bash
# 测试文档处理、嵌入生成等基础模块
python test_modules.py

# 测试 RAG 查询引擎
python test_rag_engine.py
```

测试覆盖：
- 文档处理和分块
- 嵌入向量生成和缓存
- Qdrant 向量存储和检索
- RAG 查询流程（问题嵌入、搜索、上下文构建）
- 源文档引用格式化

## 性能优化

1. **批处理**：嵌入生成使用批处理（默认 32）
2. **缓存**：嵌入向量缓存到本地文件系统
3. **异步处理**：使用 FastAPI 异步端点
4. **智能分块**：在句子边界处分割文档

## 依赖

- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- sentence-transformers >= 2.2.0
- qdrant-client >= 1.6.0
- httpx >= 0.25.0
- pydantic >= 2.0.0

## 日志

服务使用 Python logging 模块，日志级别为 INFO。

查看日志：
```bash
docker logs -f knowledge-ai
```

## 故障排除

### 模型下载失败

首次启动时会下载 Sentence Transformers 模型（约 120MB）。如果下载失败：

1. 检查网络连接
2. 使用镜像源：设置 `HF_ENDPOINT=https://hf-mirror.com`
3. 手动下载模型到 `/app/models` 目录

### Qdrant 连接失败

检查 Qdrant 服务是否运行：
```bash
curl http://localhost:6333/health
```

### Gitea API 认证失败

确保 `GITEA_TOKEN` 环境变量正确设置，并且令牌有仓库读取权限。

## RAG 引擎特性

### 智能上下文构建

- 自动限制上下文长度，避免超出 LLM token 限制
- 优先保留高相关度文档
- 在句子边界处截断，保持内容完整性
- 包含文档元数据（来源、标题、相关度评分）

### 灵活配置

- 可配置搜索结果数量（limit）
- 可配置相似度阈值（score_threshold）
- 可配置 LLM 模型（gpt-3.5-turbo, gpt-4 等）
- 可配置生成温度（temperature）
- 支持按知识层次过滤（filter_conditions）

### 错误处理

- OpenAI API 未配置时提供友好提示
- 无搜索结果时返回明确说明
- 完整的异常捕获和日志记录
- 降级策略（无 LLM 时仍可返回搜索结果）

## 使用示例

### Python 客户端

```python
import httpx

# 查询知识库
response = httpx.post(
    "http://localhost:8000/api/query",
    json={
        "question": "什么是 TCP 滑动窗口机制？",
        "limit": 5,
        "score_threshold": 0.7
    }
)

result = response.json()
print(f"答案: {result['answer']}")
print(f"找到 {len(result['sources'])} 个相关文档")

for source in result['sources']:
    print(f"- {source['title']} ({source['score']:.2f})")
```

### cURL

```bash
# 查询知识库
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是 FreeRTOS 任务调度？",
    "limit": 3,
    "score_threshold": 0.75
  }'

# 获取 RAG 引擎信息
curl http://localhost:8000/api/rag/info

# 健康检查
curl http://localhost:8000/health
```
