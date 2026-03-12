# 测试文档

本文档描述了工程师知识系统的测试策略、测试类型和测试执行方法。

## 测试概述

系统采用多层次测试策略，确保各个组件和整体系统的正确性：

1. **单元测试**：测试单个模块和函数
2. **集成测试**：测试组件间的交互
3. **端到端测试**：测试完整的用户工作流
4. **健康检查**：验证服务运行状态

## 测试类型

### 1. 单元测试

#### AI 助手模块测试

位置：`ai-assistant/test_modules.py`

测试内容：
- 模块导入验证
- 文档处理器功能
- 嵌入生成器结构
- Gitea 客户端结构

运行方法：
```bash
# 在容器内运行
docker exec knowledge-ai python test_modules.py

# 或在本地运行（需要安装依赖）
cd ai-assistant
python test_modules.py
```

#### Qdrant 客户端测试

位置：`ai-assistant/test_qdrant_client.py`

测试内容：
- Qdrant 连接
- Collection 创建
- 向量插入和检索
- 元数据过滤

运行方法：
```bash
# 确保 Qdrant 服务运行
docker-compose up -d qdrant

# 运行测试
docker exec knowledge-ai python test_qdrant_client.py
```

#### RAG 引擎测试

位置：`ai-assistant/test_rag_engine.py`

测试内容：
- RAG 引擎初始化
- 问题嵌入生成
- 文档搜索
- 上下文构建
- 查询处理

运行方法：
```bash
docker exec knowledge-ai python test_rag_engine.py
```

### 2. 集成测试

#### Docker Compose 集成测试

测试所有服务是否能正确启动和协同工作。

运行方法：
```bash
# 启动所有服务
docker-compose up -d

# 等待服务启动
sleep 30

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs
```

#### 服务间通信测试

测试容器间的网络连接：

```bash
# AI 助手 -> Qdrant
docker exec knowledge-ai ping -c 3 qdrant

# Webhook Handler -> Wiki.js
docker exec knowledge-webhook ping -c 3 wiki

# AI 助手 -> Gitea
docker exec knowledge-ai ping -c 3 gitea
```

### 3. 端到端测试

#### 自动化端到端测试

位置：`scripts/test-e2e.sh`

这是一个综合测试脚本，验证整个系统的核心功能。

测试内容：
1. Docker 服务状态检查
2. 目录结构完整性验证
3. 服务健康端点测试
4. Python 模块测试
5. Git 仓库状态检查
6. 配置文件验证
7. Docker 卷检查
8. 网络连接测试

运行方法：
```bash
# 赋予执行权限
chmod +x scripts/test-e2e.sh

# 运行测试
bash scripts/test-e2e.sh
```

预期输出：
```
==========================================
  工程师知识系统 - 端到端测试
==========================================

[INFO] 测试 1: 检查 Docker 服务状态...
[✓] 服务 knowledge-gitea 正在运行
[✓] 服务 knowledge-wiki 正在运行
[✓] 服务 knowledge-db 正在运行
...

==========================================
  测试结果汇总
==========================================
总测试数: 45
通过: 43
失败: 2

✓ 所有测试通过！
```

#### 手动端到端测试

完整的用户工作流测试：

**步骤 1：创建测试文档**

在 Obsidian 或直接创建文件：
```bash
mkdir -p knowledge/01-foundations/test
cat > knowledge/01-foundations/test/e2e-test.md << 'EOF'
# 端到端测试文档

这是一个用于测试系统功能的文档。

## 测试内容

- Git 版本控制
- Wiki.js 同步
- MkDocs 构建
- AI 嵌入生成

## 技术标签

#test #e2e #verification
EOF
```

**步骤 2：提交到 Git**

```bash
git add knowledge/01-foundations/test/e2e-test.md
git commit -m "Add E2E test document"
git push origin main
```

**步骤 3：验证 Gitea**

访问 http://localhost:3001，确认提交已推送。

**步骤 4：验证 Wiki.js 同步**

等待 5 分钟（同步间隔），然后访问 http://localhost:3000，检查文档是否出现。

或手动触发同步：
```bash
curl -X POST http://localhost:3000/api/sync \
  -H "Authorization: Bearer ${WIKI_TOKEN}"
```

**步骤 5：验证 MkDocs 构建**

访问 http://localhost:3002，检查文档站点是否更新。

**步骤 6：验证 AI 嵌入**

查询 AI 助手：
```bash
curl -X POST http://localhost:3003/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "端到端测试"}'
```

预期响应应包含新创建的文档。

**步骤 7：清理测试数据**

```bash
git rm knowledge/01-foundations/test/e2e-test.md
git commit -m "Remove E2E test document"
git push origin main
```

### 4. 健康检查测试

#### 服务健康端点

测试所有服务的健康状态：

```bash
# Qdrant
curl http://localhost:6333/health

# AI 助手
curl http://localhost:3003/health

# Gitea
curl http://localhost:3001/api/healthz

# Wiki.js
curl http://localhost:3000/healthz

# MkDocs Builder
curl http://localhost:3002/health
```

#### 数据库连接测试

```bash
# 测试 PostgreSQL 连接
docker exec knowledge-db psql -U postgres -c "SELECT version();"

# 检查数据库列表
docker exec knowledge-db psql -U postgres -c "\l"
```

## 测试最佳实践

### 测试前准备

1. **确保所有服务运行**
   ```bash
   docker-compose up -d
   docker-compose ps
   ```

2. **检查日志无错误**
   ```bash
   docker-compose logs --tail=50
   ```

3. **验证环境变量**
   ```bash
   # 检查 .env 文件是否存在
   test -f .env && echo "✓ .env exists" || echo "✗ .env missing"
   ```

### 测试执行顺序

推荐按以下顺序执行测试：

1. 单元测试（快速，无依赖）
2. 集成测试（需要服务运行）
3. 端到端测试（完整工作流）
4. 健康检查（验证稳定性）

### 测试失败处理

#### 常见失败原因

1. **服务未启动**
   ```bash
   docker-compose up -d
   ```

2. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tuln | grep -E '3000|3001|3002|3003|6333|9000'
   
   # 修改 .env 中的端口配置
   ```

3. **网络问题**
   ```bash
   # 重建网络
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

4. **数据卷问题**
   ```bash
   # 检查卷状态
   docker volume ls
   
   # 如需重置（警告：会删除数据）
   docker-compose down -v
   docker-compose up -d
   ```

#### 调试步骤

1. **查看服务日志**
   ```bash
   docker-compose logs -f [service-name]
   ```

2. **进入容器调试**
   ```bash
   docker exec -it knowledge-ai bash
   ```

3. **检查网络连接**
   ```bash
   docker network inspect knowledge-network
   ```

4. **验证配置**
   ```bash
   docker exec knowledge-ai env | grep -E 'QDRANT|GITEA|OPENAI'
   ```

## 持续集成

### GitHub Actions 示例

创建 `.github/workflows/test.yml`：

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up environment
      run: |
        cp .env.example .env
        # 设置测试环境变量
    
    - name: Start services
      run: |
        docker-compose up -d
        sleep 30
    
    - name: Run E2E tests
      run: |
        bash scripts/test-e2e.sh
    
    - name: Run Python tests
      run: |
        docker exec knowledge-ai python test_modules.py
    
    - name: Cleanup
      if: always()
      run: |
        docker-compose down -v
```

## 性能测试

### 负载测试

测试系统在高负载下的表现：

```bash
# 使用 Apache Bench 测试 AI 助手
ab -n 100 -c 10 -p query.json -T application/json \
  http://localhost:3003/api/query

# query.json 内容
echo '{"question": "测试问题"}' > query.json
```

### 大规模文档测试

测试系统处理大量文档的能力：

```bash
# 生成 1000 个测试文档
for i in {1..1000}; do
  mkdir -p knowledge/test
  echo "# Test Document $i" > knowledge/test/doc-$i.md
  echo "This is test document number $i" >> knowledge/test/doc-$i.md
done

# 提交并推送
git add knowledge/test
git commit -m "Add 1000 test documents"
git push origin main

# 监控 AI 助手处理进度
docker logs -f knowledge-ai
```

## 测试报告

### 生成测试报告

运行测试并生成报告：

```bash
# 运行测试并保存输出
bash scripts/test-e2e.sh > test-report.txt 2>&1

# 查看报告
cat test-report.txt
```

### 测试覆盖率

对于 Python 代码，使用 pytest-cov：

```bash
# 在 AI 助手容器中安装 pytest-cov
docker exec knowledge-ai pip install pytest pytest-cov

# 运行测试并生成覆盖率报告
docker exec knowledge-ai pytest --cov=. --cov-report=html

# 查看报告
docker cp knowledge-ai:/app/htmlcov ./coverage-report
```

## 故障排除

### 测试环境重置

如果测试环境出现问题，完全重置：

```bash
# 停止所有服务
docker-compose down

# 删除所有卷（警告：会删除所有数据）
docker-compose down -v

# 清理网络
docker network prune -f

# 重新初始化
bash scripts/init.sh
docker-compose up -d

# 等待服务启动
sleep 30

# 重新运行测试
bash scripts/test-e2e.sh
```

### 常见问题

**Q: 测试超时怎么办？**

A: 增加等待时间或检查服务是否正常启动：
```bash
docker-compose ps
docker-compose logs
```

**Q: Qdrant 连接失败？**

A: 检查 Qdrant 是否运行并可访问：
```bash
curl http://localhost:6333/health
docker logs knowledge-qdrant
```

**Q: AI 助手无法生成嵌入？**

A: 检查模型是否下载和 API 密钥配置：
```bash
docker exec knowledge-ai ls -la /app/models
docker exec knowledge-ai env | grep OPENAI_API_KEY
```

## 总结

完整的测试流程确保系统的可靠性和稳定性。建议：

1. **开发时**：频繁运行单元测试
2. **提交前**：运行集成测试
3. **部署前**：运行完整的端到端测试
4. **生产环境**：定期运行健康检查

遵循这些测试实践，可以及早发现问题并保持系统质量。
