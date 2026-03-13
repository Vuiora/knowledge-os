# 服务状态报告

## 所有服务已成功启动！

### 服务访问地址

| 服务 | 地址 | 状态 | 说明 |
|------|------|------|------|
| **Gitea** | http://localhost:8001 | ✅ 运行中 | Git 版本控制服务器 |
| **Wiki.js** | http://localhost:8000 | ✅ 运行中 | 团队知识库 |
| **MkDocs** | http://localhost:8002 | ✅ 运行中 | 文档站点 |
| **AI 助手** | http://localhost:8003 | ✅ 运行中 | 智能问答 API |
| **Qdrant** | http://localhost:6333 | ✅ 运行中 | 向量数据库 |
| **Webhook** | http://localhost:9000 | ✅ 运行中 | 自动化处理器 |
| **PostgreSQL** | localhost:5432 | ✅ 运行中 | 数据库（内部） |

### 端口变更说明

由于 Windows 系统保留端口范围（2981-3080, 3081-3180），原计划的端口被占用，已调整为：

- Gitea: 3001 → **8001**
- Wiki.js: 3000 → **8000**
- MkDocs: 3002 → **8002**
- AI 助手: 3003 → **8003**

### 已修复的问题

1. ✅ **Gitea Webhook 权限问题**
   - 添加了 `GITEA__webhook__ALLOWED_HOST_LIST=*` 配置
   - 现在可以调用内部服务

2. ✅ **端口冲突问题**
   - 避开了 Windows 保留端口范围
   - 使用 8000+ 端口段

3. ✅ **Wiki.js Git 同步配置**
   - 已配置 Git Storage
   - 需要在管理界面设置 Source Directory

### 下一步操作

#### 1. 配置 Wiki.js 显示 knowledge 目录

访问 http://localhost:8000 并登录后：

1. 点击右上角头像 → Administration
2. 左侧菜单 → Storage → Git
3. 配置如下：
   ```
   Authentication Type: Basic
   Repository URL: http://gitea:3000/admin/knowledge-system.git
   Branch: main
   Username: admin
   Password: [你的 Gitea 密码]
   Source Directory: knowledge    ← 关键配置！
   Sync Direction: Sync ← Remote (Pull)
   Sync Interval: PT5M
   ```
4. 点击 Apply
5. 点击 Execute Sync

#### 2. 配置 Gitea Webhook

在 Gitea (http://localhost:8001) 中：

1. 进入仓库 → 设置 → Webhooks
2. 添加 Webhook：
   - URL: `http://webhook-handler:9000/hooks/knowledge-sync`
   - Secret: `RnOO36LJ19hIcbsu5e8oeHilKIXXBRlN`
   - 触发事件: Push events
3. 测试 Webhook

#### 3. 推送代码到 Gitea

```bash
git remote set-url origin http://localhost:8001/admin/knowledge-system.git
git push
```

### 验证服务

#### 检查 Gitea
```bash
curl http://localhost:8001/api/healthz
```

#### 检查 Wiki.js
访问 http://localhost:8000

#### 检查 MkDocs
访问 http://localhost:8002

#### 检查 AI 助手
```bash
curl http://localhost:8003/health
```

#### 检查 Qdrant
```bash
curl http://localhost:6333/health
```

### 常用命令

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service-name]

# 重启服务
docker-compose restart [service-name]

# 停止所有服务
docker-compose down

# 启动所有服务
docker-compose up -d
```

### 故障排除

#### 如果服务无法访问

1. 检查容器状态：`docker-compose ps`
2. 查看日志：`docker-compose logs [service-name]`
3. 重启服务：`docker-compose restart [service-name]`

#### 如果 Wiki.js 看不到文档

1. 确认已配置 Source Directory 为 `knowledge`
2. 手动触发同步：Administration → Storage → Git → Execute Sync
3. 查看同步日志：`docker-compose logs wiki`

#### 如果 Webhook 不工作

1. 检查 Gitea Webhook 配置
2. 测试 Webhook：在 Gitea 中点击 "测试推送"
3. 查看 webhook-handler 日志：`docker-compose logs webhook-handler`

---

**系统已就绪！** 🎉

现在你可以：
- 在 Obsidian 中编辑 knowledge 目录
- 在 Wiki.js 中查看和协作
- 在 MkDocs 中发布文档
- 使用 AI 助手进行智能搜索

