# 使用示例

本文档提供 MkDocs Index Generator 的详细使用示例，涵盖从基础到高级的各种场景。

## 目录

- [基础使用](#基础使用)
- [配置文件使用](#配置文件使用)
- [模板自定义](#模板自定义)
- [批量操作](#批量操作)
- [CI/CD 集成](#cicd-集成)
- [高级场景](#高级场景)

## 基础使用

### 示例 1: 首次使用 - 完整流程

```bash
# 步骤 1: 扫描目录，查看缺失的 index.md
python mkdocs_index_generator.py scan knowledge/

# 输出示例：
# 扫描目录: knowledge/
# 找到 15 个缺失 index.md 的目录：
#   - knowledge/01-foundations/algorithm/
#   - knowledge/01-foundations/database/
#   - knowledge/02-technologies/embedded/01-hardware-layer/
#   ...

# 步骤 2: 预览将要生成的内容（前 5 个）
python mkdocs_index_generator.py preview knowledge/ --limit 5

# 步骤 3: 确认无误后生成所有文件
python mkdocs_index_generator.py generate knowledge/

# 输出示例：
# 生成报告：
# ✓ 成功: 15
# ⊘ 跳过: 0
# ✗ 失败: 0
```

### 示例 2: 只扫描不生成

```bash
# 查看哪些目录缺失 index.md
python mkdocs_index_generator.py scan knowledge/

# 查看特定类型的目录
python mkdocs_index_generator.py scan knowledge/ --type difficulty
```

### 示例 3: 预览模式（不写入文件）

```bash
# 预览前 5 个目录的生成内容
python mkdocs_index_generator.py preview knowledge/ --limit 5

# 预览所有目录
python mkdocs_index_generator.py preview knowledge/ --limit 0

# 预览特定类型
python mkdocs_index_generator.py preview knowledge/ --type sub_topic
```

### 示例 4: 生成文件（基础）

```bash
# 生成所有缺失的 index.md
python mkdocs_index_generator.py generate knowledge/

# 只生成难度级别目录的 index.md
python mkdocs_index_generator.py generate knowledge/ --type difficulty

# 预览模式（不实际写入）
python mkdocs_index_generator.py generate knowledge/ --dry-run
```

## 配置文件使用

### 示例 5: 使用配置文件

创建配置文件 `my-config.yml`:

```yaml
scan:
  root_dir: "knowledge"
  excluded_dirs:
    - "javascripts"
    - "stylesheets"
    - "_site"
    - "_wiki"
    - "temp"

templates:
  main_layer: "templates/main_layer.md"
  sub_topic: "templates/sub_topic.md"
  difficulty: "templates/difficulty.md"
  content: "templates/content.md"

generation:
  force_overwrite: false
  create_backup: true
  dry_run: false

logging:
  level: "INFO"
  file: "generator.log"
```

使用配置文件：

```bash
python mkdocs_index_generator.py generate knowledge/ --config my-config.yml
```

### 示例 6: 不同环境的配置

开发环境配置 `config-dev.yml`:

```yaml
scan:
  root_dir: "knowledge"
  excluded_dirs:
    - "_site"
    - "_wiki"

generation:
  force_overwrite: true  # 开发时允许覆盖
  create_backup: true
  dry_run: false

logging:
  level: "DEBUG"  # 详细日志
  file: "dev.log"
```

生产环境配置 `config-prod.yml`:

```yaml
scan:
  root_dir: "knowledge"
  excluded_dirs:
    - "_site"
    - "_wiki"
    - "temp"

generation:
  force_overwrite: false  # 生产环境保护已有文件
  create_backup: true
  dry_run: false

logging:
  level: "WARNING"  # 只记录警告和错误
  file: "prod.log"
```

使用：

```bash
# 开发环境
python mkdocs_index_generator.py generate knowledge/ --config config-dev.yml

# 生产环境
python mkdocs_index_generator.py generate knowledge/ --config config-prod.yml
```

### 示例 7: JSON 格式配置

创建 `config.json`:

```json
{
  "scan": {
    "root_dir": "knowledge",
    "excluded_dirs": [
      "javascripts",
      "stylesheets",
      "_site",
      "_wiki"
    ]
  },
  "templates": {
    "main_layer": "templates/main_layer.md",
    "sub_topic": "templates/sub_topic.md",
    "difficulty": "templates/difficulty.md",
    "content": "templates/content.md"
  },
  "generation": {
    "force_overwrite": false,
    "create_backup": true,
    "dry_run": false
  },
  "logging": {
    "level": "INFO",
    "file": "generator.log"
  }
}
```

使用：

```bash
python mkdocs_index_generator.py generate knowledge/ --config config.json
```

## 模板自定义

### 示例 8: 创建自定义模板

创建模板目录和文件：

```bash
mkdir my-templates
```

创建 `my-templates/main_layer.md`:

```markdown
---
title: {{title}}
description: {{description}}
---

# 📚 {{title}}

> {{description}}

## 🎯 学习目标

本章节涵盖以下主题：

{{children}}

## 📖 学习建议

1. 按照子主题顺序学习
2. 完成每个主题的练习
3. 参考相关文档深入理解

## 🔗 相关资源

- [官方文档](https://example.com)
- [视频教程](https://example.com)

---
*最后更新：{{date}}*
```

创建 `my-templates/difficulty.md`:

```markdown
---
title: {{title}} 级别
description: {{description}}
---

# {{title}} 级别内容

## 📝 内容列表

{{children}}

## 💡 学习提示

根据您的基础选择合适的学习内容：

- **Beginner**: 适合初学者，从基础概念开始
- **Intermediate**: 需要一定基础，深入理解原理
- **Advanced**: 高级主题，需要扎实的基础知识

## ⏱️ 预计学习时间

- Beginner: 2-4 周
- Intermediate: 4-8 周
- Advanced: 8-12 周

---
*生成时间：{{date}}*
```

使用自定义模板：

```bash
python mkdocs_index_generator.py generate knowledge/ --template-dir my-templates/
```

### 示例 9: 模板变量使用

所有可用的模板变量：

```markdown
---
title: {{title}}
description: {{description}}
---

# {{title}}

**路径**: {{breadcrumb}}

**层级**: {{level}}

## 内容

{{children}}

---
*生成时间：{{date}}*
```

## 批量操作

### 示例 10: 按类型批量生成

```bash
# 只生成主层级目录
python mkdocs_index_generator.py generate knowledge/ --type main_layer

# 只生成子主题目录
python mkdocs_index_generator.py generate knowledge/ --type sub_topic

# 只生成难度级别目录
python mkdocs_index_generator.py generate knowledge/ --type difficulty

# 只生成内容目录
python mkdocs_index_generator.py generate knowledge/ --type content
```

### 示例 11: 强制重新生成所有文件

```bash
# 会覆盖已存在的文件（但会创建备份）
python mkdocs_index_generator.py generate knowledge/ --force

# 查看备份文件
find knowledge/ -name "*.backup"
```

### 示例 12: 批量处理多个目录

创建脚本 `batch-generate.sh`:

```bash
#!/bin/bash

# 定义要处理的目录列表
DIRS=(
  "knowledge"
  "docs"
  "wiki"
)

# 循环处理每个目录
for dir in "${DIRS[@]}"; do
  echo "=========================================="
  echo "处理目录: $dir"
  echo "=========================================="
  
  if [ -d "$dir" ]; then
    python mkdocs_index_generator.py generate "$dir/" --config config.yml
    
    if [ $? -eq 0 ]; then
      echo "✓ $dir 处理成功"
    else
      echo "✗ $dir 处理失败"
    fi
  else
    echo "⚠ 目录不存在: $dir"
  fi
  
  echo ""
done

echo "批量处理完成！"
```

运行：

```bash
chmod +x batch-generate.sh
./batch-generate.sh
```

## CI/CD 集成

### 示例 13: GitHub Actions 集成

创建 `.github/workflows/generate-index.yml`:

```yaml
name: Generate MkDocs Index

on:
  push:
    branches: [ main ]
    paths:
      - 'knowledge/**'
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd mkdocs-index-generator
        pip install -r requirements.txt
    
    - name: Generate index files
      run: |
        cd mkdocs-index-generator
        python mkdocs_index_generator.py generate ../knowledge/ --config config.yml
    
    - name: Commit changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add knowledge/**/index.md
        git diff --quiet && git diff --staged --quiet || git commit -m "Auto-generate index.md files"
    
    - name: Push changes
      uses: ad-m/github-push-action@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        branch: ${{ github.ref }}
```

### 示例 14: GitLab CI 集成

创建 `.gitlab-ci.yml`:

```yaml
stages:
  - generate

generate-index:
  stage: generate
  image: python:3.9
  
  before_script:
    - cd mkdocs-index-generator
    - pip install -r requirements.txt
  
  script:
    - python mkdocs_index_generator.py generate ../knowledge/ --config config.yml
    - cd ..
    - git config --global user.email "ci@gitlab.com"
    - git config --global user.name "GitLab CI"
    - git add knowledge/**/index.md
    - git diff --quiet && git diff --staged --quiet || git commit -m "Auto-generate index.md files"
    - git push origin HEAD:$CI_COMMIT_REF_NAME
  
  only:
    - main
  
  when: manual
```

### 示例 15: Jenkins 集成

创建 `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r mkdocs-index-generator/requirements.txt'
            }
        }
        
        stage('Generate Index') {
            steps {
                dir('mkdocs-index-generator') {
                    sh 'python mkdocs_index_generator.py generate ../knowledge/ --config config.yml'
                }
            }
        }
        
        stage('Commit Changes') {
            steps {
                sh '''
                    git config user.email "jenkins@example.com"
                    git config user.name "Jenkins"
                    git add knowledge/**/index.md
                    git diff --quiet && git diff --staged --quiet || git commit -m "Auto-generate index.md files"
                    git push origin main
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Index generation completed successfully!'
        }
        failure {
            echo 'Index generation failed!'
        }
    }
}
```

## 高级场景

### 示例 16: 定时自动更新

Linux/Mac Cron 任务：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天凌晨 2 点执行）
0 2 * * * cd /path/to/project/mkdocs-index-generator && python mkdocs_index_generator.py generate ../knowledge/ --config config.yml >> /var/log/mkdocs-gen.log 2>&1

# 每周一凌晨 3 点执行
0 3 * * 1 cd /path/to/project/mkdocs-index-generator && python mkdocs_index_generator.py generate ../knowledge/ --force --config config.yml >> /var/log/mkdocs-gen.log 2>&1
```

Windows 任务计划程序脚本 `schedule-task.bat`:

```batch
@echo off
cd C:\path\to\project\mkdocs-index-generator
python mkdocs_index_generator.py generate ..\knowledge\ --config config.yml >> C:\logs\mkdocs-gen.log 2>&1
```

### 示例 17: 增量更新（只更新新目录）

创建脚本 `incremental-update.sh`:

```bash
#!/bin/bash

# 查找所有没有 index.md 的目录
find knowledge/ -type d | while read dir; do
  if [ ! -f "$dir/index.md" ]; then
    echo "发现新目录: $dir"
    python mkdocs_index_generator.py generate "$dir/" --config config.yml
  fi
done
```

### 示例 18: 验证和修复

```bash
# 步骤 1: 验证现有 index.md 文件
python mkdocs_index_generator.py validate knowledge/

# 步骤 2: 如果发现问题，重新生成
python mkdocs_index_generator.py generate knowledge/ --force

# 步骤 3: 再次验证
python mkdocs_index_generator.py validate knowledge/
```

### 示例 19: 生成报告并发送邮件

创建脚本 `generate-and-notify.sh`:

```bash
#!/bin/bash

# 生成索引并保存报告
python mkdocs_index_generator.py generate knowledge/ --config config.yml > report.txt 2>&1

# 检查是否成功
if [ $? -eq 0 ]; then
  STATUS="成功"
  SUBJECT="MkDocs 索引生成成功"
else
  STATUS="失败"
  SUBJECT="MkDocs 索引生成失败"
fi

# 发送邮件通知
mail -s "$SUBJECT" admin@example.com < report.txt

echo "报告已发送到 admin@example.com"
```

### 示例 20: 与 Git 钩子集成

创建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# 检查是否有 knowledge 目录的更改
if git diff --cached --name-only | grep -q "^knowledge/"; then
  echo "检测到 knowledge 目录更改，生成索引文件..."
  
  cd mkdocs-index-generator
  python mkdocs_index_generator.py generate ../knowledge/ --config config.yml
  
  if [ $? -eq 0 ]; then
    echo "✓ 索引文件生成成功"
    # 将生成的文件添加到暂存区
    git add ../knowledge/**/index.md
  else
    echo "✗ 索引文件生成失败"
    exit 1
  fi
fi
```

设置可执行权限：

```bash
chmod +x .git/hooks/pre-commit
```

### 示例 21: 条件生成（基于文件修改时间）

创建脚本 `conditional-generate.sh`:

```bash
#!/bin/bash

# 查找最近 7 天修改的目录
echo "查找最近 7 天修改的目录..."

find knowledge/ -type d -mtime -7 | while read dir; do
  # 检查该目录是否有 index.md
  if [ ! -f "$dir/index.md" ]; then
    echo "生成: $dir (新目录)"
    python mkdocs_index_generator.py generate "$dir/" --config config.yml
  else
    # 检查 index.md 是否比目录旧
    if [ "$dir/index.md" -ot "$dir" ]; then
      echo "更新: $dir (目录已修改)"
      python mkdocs_index_generator.py generate "$dir/" --force --config config.yml
    fi
  fi
done
```

### 示例 22: 并行处理（加速大型项目）

创建脚本 `parallel-generate.sh`:

```bash
#!/bin/bash

# 获取所有一级子目录
DIRS=$(find knowledge/ -maxdepth 1 -type d | tail -n +2)

# 并行处理（最多 4 个进程）
echo "$DIRS" | xargs -P 4 -I {} bash -c '
  echo "处理: {}"
  python mkdocs_index_generator.py generate {}/ --config config.yml
'

echo "并行处理完成！"
```

### 示例 23: 生成统计和可视化

创建脚本 `generate-stats.py`:

```python
#!/usr/bin/env python3
import subprocess
import json
import re

# 运行生成命令
result = subprocess.run(
    ['python', 'mkdocs_index_generator.py', 'generate', 'knowledge/', '--config', 'config.yml'],
    capture_output=True,
    text=True
)

# 解析输出
output = result.stdout
stats = {
    'total': 0,
    'success': 0,
    'skipped': 0,
    'failed': 0
}

# 提取统计信息（根据实际输出格式调整）
if '成功:' in output:
    stats['success'] = int(re.search(r'成功:\s*(\d+)', output).group(1))
if '跳过:' in output:
    stats['skipped'] = int(re.search(r'跳过:\s*(\d+)', output).group(1))
if '失败:' in output:
    stats['failed'] = int(re.search(r'失败:\s*(\d+)', output).group(1))

stats['total'] = stats['success'] + stats['skipped'] + stats['failed']

# 保存为 JSON
with open('stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

# 打印统计
print(f"总计: {stats['total']}")
print(f"成功: {stats['success']}")
print(f"跳过: {stats['skipped']}")
print(f"失败: {stats['failed']}")
print(f"成功率: {stats['success']/stats['total']*100:.1f}%")
```

## 故障排除示例

### 示例 24: 调试模式

```bash
# 启用详细日志
python mkdocs_index_generator.py generate knowledge/ --config config-debug.yml
```

`config-debug.yml`:

```yaml
logging:
  level: "DEBUG"
  file: "debug.log"
```

查看日志：

```bash
# 实时查看日志
tail -f debug.log

# 搜索错误
grep ERROR debug.log

# 搜索特定目录的日志
grep "01-hardware-layer" debug.log
```

### 示例 25: 测试配置

```bash
# 使用预览模式测试配置
python mkdocs_index_generator.py generate knowledge/ --config test-config.yml --dry-run

# 只处理一个目录测试
python mkdocs_index_generator.py generate knowledge/01-foundations/ --config test-config.yml
```

---

## 总结

这些示例涵盖了从基础到高级的各种使用场景。根据您的需求选择合适的示例，并根据实际情况进行调整。

如需更多帮助，请参考：
- [README.md](README.md) - 完整文档
- [FAQ.md](FAQ.md) - 常见问题解答
- [config.example.yml](config.example.yml) - 配置示例

*最后更新：2024*
