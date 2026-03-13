# Wiki.js 配置指南

## 问题：Wiki.js 看不到 knowledge 目录下的文档

### 原因
Wiki.js 默认同步整个 Git 仓库的根目录，而我们的知识库内容在 `knowledge/` 子目录下。

### 解决方案

#### 步骤 1：访问 Wiki.js 管理界面

1. 打开浏览器访问：http://localhost:3000
2. 使用管理员账号登录
3. 点击右上角头像 → "Administration"

#### 步骤 2：配置 Git Storage

1. 在左侧菜单中选择 "Storage"
2. 找到 "Git" 存储类型并点击
3. 填写以下配置：

```yaml
Authentication Type: Basic
Repository URL: http://gitea:3000/admin/knowledge-system.git
Branch: main
Username: admin
Password: [你在 Gitea 设置的密码]

# 关键配置
Local Repository Path: /wiki/data/repo
Source Directory: knowledge          # ← 重要！指定 knowledge 目录
Sync Direction: Sync ← Remote (Pull)
Sync Interval: PT5M                  # 每5分钟同步一次

# 作者信息
Default Author Email: wiki@example.com
Default Author Name: Wiki.js
```

#### 步骤 3：应用并测试

1. 点击页面底部的 "Apply" 按钮
2. 等待配置保存成功
3. 点击 "Execute Sync" 按钮立即执行同步
4. 等待同步完成（可能需要几秒钟）

#### 步骤 4：验证

1. 返回 Wiki.js 首页
2. 你应该能看到以下目录结构：
   - 01-foundations/
   - 02-technologies/
   - 03-architecture/
   - 04-projects/
   - 05-insights/
   - index.md (首页)

## 配置说明

### Source Directory 字段的作用

- **不填写**：同步整个仓库根目录（包括 docker-compose.yml、README.md 等）
- **填写 knowledge**：只同步 knowledge/ 目录下的内容
- **填写 knowledge/02-technologies**：只同步特定子目录

### Sync Direction 选项

- **Sync ← Remote (Pull)**：从 Git 拉取到 Wiki.js（推荐）
- **Sync → Remote (Push)**：从 Wiki.js 推送到 Git
- **Bi-directional**：双向同步（可能导致冲突）

### Sync Interval 格式

使用 ISO 8601 Duration 格式：
- `PT5M` = 5分钟
- `PT1H` = 1小时
- `PT30S` = 30秒

## 常见问题

### Q1: 同步后还是看不到文档？

**检查项：**
1. 确认 Source Directory 填写为 `knowledge`（不要加斜杠）
2. 检查 Git 仓库中确实有 knowledge 目录
3. 查看 Wiki.js 日志：`docker logs knowledge-wiki --tail 50`

### Q2: 同步失败，显示认证错误？

**解决方法：**
1. 确认 Gitea 用户名和密码正确
2. 确认 Repository URL 正确：`http://gitea:3000/admin/knowledge-system.git`
3. 在 Gitea 中检查仓库是否存在

### Q3: 文档显示但格式不对？

**可能原因：**
1. Markdown 语法问题
2. Wiki.js 不支持某些 Markdown 扩展
3. 图片路径问题

### Q4: 如何手动触发同步？

**方法：**
1. 进入 Administration → Storage
2. 点击 Git 存储
3. 点击 "Execute Sync" 按钮

或使用 API：
```bash
curl -X POST http://localhost:3000/api/storage/execute \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"targetKey": "git"}'
```

## 高级配置

### 配置多个 Git 存储

如果你想同时同步多个目录：

1. 添加第二个 Git Storage
2. 使用不同的 Source Directory
3. 例如：
   - Git Storage 1: Source Directory = `knowledge`
   - Git Storage 2: Source Directory = `docs`

### 配置 SSH 认证

如果使用 SSH 而不是 HTTP：

```yaml
Authentication Type: SSH
Repository URL: git@gitea:admin/knowledge-system.git
SSH Private Key: [粘贴私钥内容]
```

### 配置 Webhook 自动同步

在 Gitea 中配置 Webhook，推送时自动触发 Wiki.js 同步：

```
URL: http://wiki:3000/api/storage/execute
Method: POST
Content Type: application/json
Secret: [设置一个密钥]
Body:
{
  "targetKey": "git"
}
```

## 验证配置

### 检查同步状态

```bash
# 查看 Wiki.js 日志
docker logs knowledge-wiki --tail 100 | grep STORAGE

# 检查 repo 目录
docker exec knowledge-wiki ls -la /wiki/data/repo

# 应该看到 knowledge 目录下的文件
docker exec knowledge-wiki ls -la /wiki/data/repo/01-foundations
```

### 测试完整流程

1. 在本地修改 `knowledge/index.md`
2. 提交并推送到 Gitea
3. 等待 5 分钟（或手动触发同步）
4. 在 Wiki.js 中查看更新

## 故障排除

### 查看详细日志

```bash
# 实时查看日志
docker logs -f knowledge-wiki

# 查看最近的错误
docker logs knowledge-wiki 2>&1 | grep -i error
```

### 重置 Git Storage

如果配置出错，可以重置：

1. 在 Wiki.js 管理界面删除 Git Storage 配置
2. 清空 repo 目录：
   ```bash
   docker exec knowledge-wiki rm -rf /wiki/data/repo/*
   ```
3. 重新配置 Git Storage

### 手动克隆仓库测试

```bash
# 进入容器
docker exec -it knowledge-wiki sh

# 手动克隆测试
cd /tmp
git clone http://admin:PASSWORD@gitea:3000/admin/knowledge-system.git
ls -la knowledge-system/knowledge/
```

## 参考资源

- [Wiki.js 官方文档](https://docs.requarks.io/)
- [Git Storage 配置](https://docs.requarks.io/storage/git)
- [API 文档](https://docs.requarks.io/dev/api)

---

配置完成后，你的 Wiki.js 应该能正确显示 knowledge 目录下的所有文档了！
