# 脚本文档

本目录包含工程师知识系统的管理和维护脚本。

## 脚本列表

### 1. init.sh - 初始化脚本

**用途**: 创建项目目录结构、初始化 Git 仓库、生成配置文件

**使用方法**:
```bash
bash scripts/init.sh
```

**功能**:
- 创建五层知识层次目录结构
- 创建 Wiki、MkDocs、Obsidian 配置目录
- 初始化 Git 仓库
- 生成 .gitignore 文件
- 生成 README.md 文件
- 创建 .env 文件（从 .env.example）

**何时使用**: 首次设置项目时

---

### 2. deploy.sh - 部署脚本

**用途**: 部署和启动所有 Docker 服务，包含健康检查和配置向导

**使用方法**:
```bash
bash scripts/deploy.sh
```

**功能**:
- 检查 Docker 和 Docker Compose 安装
- 验证配置文件存在
- 构建 Docker 镜像
- 启动所有服务
- 执行健康检查
- 显示初始配置向导

**何时使用**: 
- 首次部署系统
- 更新服务配置后重新部署
- 系统维护后重启服务

---

### 3. backup.sh - 备份脚本

**用途**: 备份 Git 仓库和 Docker 卷数据

**使用方法**:
```bash
# 基本备份
bash scripts/backup.sh

# 指定备份目录
BACKUP_DIR=/path/to/backups bash scripts/backup.sh

# 设置备份保留天数（自动清理旧备份）
BACKUP_RETENTION_DAYS=30 bash scripts/backup.sh
```

**功能**:
- 创建 Git bundle 备份
- 备份所有 Docker 卷（Gitea、Wiki.js、数据库、Qdrant、AI 缓存、MkDocs）
- 备份配置文件（.env、docker-compose.yml、.obsidian、scripts）
- 生成备份清单
- 自动清理过期备份（可选）

**备份文件命名**:
- Git: `knowledge-system-backup-YYYYMMDD_HHMMSS.bundle`
- 卷: `knowledge-system-backup-YYYYMMDD_HHMMSS-<volume_name>.tar.gz`
- 配置: `knowledge-system-backup-YYYYMMDD_HHMMSS-config.tar.gz`
- 清单: `knowledge-system-backup-YYYYMMDD_HHMMSS-manifest.txt`

**何时使用**:
- 定期备份（建议每天）
- 重大更改前
- 系统升级前

---

### 4. restore.sh - 恢复脚本

**用途**: 从备份恢复 Git 仓库和 Docker 卷数据

**使用方法**:
```bash
# 交互式恢复
bash scripts/restore.sh

# 指定备份目录
BACKUP_DIR=/path/to/backups bash scripts/restore.sh
```

**功能**:
- 列出可用的备份
- 交互式选择要恢复的备份
- 恢复 Git 仓库
- 恢复 Docker 卷
- 恢复配置文件
- 自动重启服务

**注意事项**:
- ⚠️ 恢复操作会覆盖现有数据
- 现有 Git 仓库会备份到 `.git.backup`
- 现有 .env 会备份到 `.env.backup`
- 服务会自动停止并重启

**何时使用**:
- 数据丢失或损坏
- 迁移到新服务器
- 回滚到之前的状态

---

### 5. setup-backup-cron.sh - 设置自动备份

**用途**: 配置 cron 定时任务自动执行备份

**使用方法**:
```bash
bash scripts/setup-backup-cron.sh
```

**功能**:
- 交互式选择备份频率
- 设置备份保留天数
- 自动配置 cron 任务
- 创建备份日志

**备份频率选项**:
1. 每天凌晨 2:00
2. 每天凌晨 3:00
3. 每周日凌晨 2:00
4. 每 12 小时
5. 自定义 cron 表达式

**何时使用**: 设置自动备份策略时

**Windows 用户**: 
Windows 不支持 cron，请使用任务计划程序 (Task Scheduler) 手动设置定时任务。

---

### 6. generate-secrets.sh - 生成安全密钥

**用途**: 生成安全的随机密码和密钥

**使用方法**:
```bash
bash scripts/generate-secrets.sh
```

**功能**:
- 生成 Gitea 密码
- 生成数据库密码
- 生成 Webhook 密钥
- 生成 PostgreSQL 密码

**输出**: 显示生成的密钥，需要手动复制到 .env 文件

**何时使用**: 
- 首次配置 .env 文件
- 更新密码和密钥

---

### 7. verify-git-sync.sh - 验证 Git 同步

**用途**: 验证 Git 同步流程的完整性

**使用方法**:
```bash
bash scripts/verify-git-sync.sh
```

**功能**:
- 检查目录结构
- 验证 Docker Compose 配置
- 检查环境变量
- 验证 Webhook Handler 实现
- 检查数据库初始化脚本
- 检查 Docker 服务状态
- 验证 Git 仓库配置

**何时使用**:
- 完成初始部署后
- 排查同步问题
- 系统健康检查

---

### 8. init-db.sql - 数据库初始化

**用途**: PostgreSQL 数据库初始化脚本

**功能**:
- 创建 Gitea 数据库和用户
- 创建 Wiki.js 数据库和用户
- 设置权限

**使用**: 由 Docker Compose 自动执行，无需手动运行

---

## 常见使用场景

### 场景 1: 首次部署

```bash
# 1. 初始化项目
bash scripts/init.sh

# 2. 生成安全密钥
bash scripts/generate-secrets.sh

# 3. 编辑 .env 文件，填入生成的密钥
nano .env

# 4. 部署服务
bash scripts/deploy.sh

# 5. 按照部署脚本的向导完成配置

# 6. 验证同步流程
bash scripts/verify-git-sync.sh

# 7. 设置自动备份
bash scripts/setup-backup-cron.sh
```

### 场景 2: 定期维护

```bash
# 手动备份
bash scripts/backup.sh

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart
```

### 场景 3: 灾难恢复

```bash
# 1. 恢复数据
bash scripts/restore.sh

# 2. 验证恢复
bash scripts/verify-git-sync.sh

# 3. 检查服务
docker compose ps
docker compose logs -f
```

### 场景 4: 迁移到新服务器

```bash
# 在旧服务器上
bash scripts/backup.sh
# 复制 backups/ 目录到新服务器

# 在新服务器上
# 1. 克隆项目或创建新目录
git clone <repo> knowledge-system
cd knowledge-system

# 2. 复制备份文件到 backups/ 目录

# 3. 恢复数据
bash scripts/restore.sh

# 4. 验证
bash scripts/verify-git-sync.sh
```

## 环境变量

所有脚本支持以下环境变量：

- `BACKUP_DIR`: 备份目录路径（默认: ./backups）
- `BACKUP_RETENTION_DAYS`: 备份保留天数（默认: 不自动清理）

## 日志

- 部署日志: `docker compose logs`
- 备份日志: `backups/backup.log`（如果使用 cron）
- 服务日志: `docker compose logs <service_name>`

## 故障排除

### 问题: 脚本权限错误

```bash
# Linux/Mac
chmod +x scripts/*.sh

# Windows (Git Bash)
# 脚本应该已经有执行权限
```

### 问题: Docker 服务启动失败

```bash
# 查看详细日志
docker compose logs <service_name>

# 检查端口占用
netstat -ano | findstr :3001
netstat -ano | findstr :3000

# 重新构建镜像
docker compose build --no-cache
docker compose up -d
```

### 问题: 备份失败

```bash
# 检查磁盘空间
df -h

# 检查 Docker 卷
docker volume ls
docker volume inspect <volume_name>

# 手动备份单个卷
docker run --rm -v <volume_name>:/data -v $(pwd)/backups:/backup alpine tar -czf /backup/manual-backup.tar.gz -C /data .
```

### 问题: 恢复失败

```bash
# 验证备份文件完整性
tar -tzf backups/<backup_file>.tar.gz

# 验证 Git bundle
git bundle verify backups/<backup_file>.bundle

# 手动恢复
git clone backups/<backup_file>.bundle restored-repo
```

## 最佳实践

1. **定期备份**: 设置每日自动备份
2. **异地备份**: 将备份文件复制到其他位置
3. **测试恢复**: 定期测试恢复流程
4. **监控日志**: 定期检查备份日志
5. **版本控制**: 保留多个备份版本
6. **文档更新**: 记录重要的配置更改

## 安全建议

1. **保护 .env 文件**: 不要提交到 Git
2. **使用强密码**: 使用 generate-secrets.sh 生成
3. **限制访问**: 设置适当的文件权限
4. **加密备份**: 考虑加密敏感备份
5. **定期更新**: 更新密码和 API 密钥

## 支持

如有问题，请参考：
- 项目文档: `.kiro/specs/engineer-knowledge-system/`
- Docker 日志: `docker compose logs -f`
- 验证脚本: `bash scripts/verify-git-sync.sh`
