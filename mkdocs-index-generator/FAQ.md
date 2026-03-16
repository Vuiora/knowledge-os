# 常见问题解答 (FAQ)

## 目录

- [安装和配置](#安装和配置)
- [使用问题](#使用问题)
- [模板和自定义](#模板和自定义)
- [错误处理](#错误处理)
- [高级用法](#高级用法)

## 安装和配置

### Q1: 支持哪些 Python 版本？

**A**: MkDocs Index Generator 需要 Python 3.8 或更高版本。

验证 Python 版本：
```bash
python --version
```

### Q2: 如何安装依赖？

**A**: 使用 pip 安装 requirements.txt 中的所有依赖：

```bash
pip install -r requirements.txt
```

如果遇到权限问题，可以使用：
```bash
pip install --user -r requirements.txt
```

### Q3: 配置文件必须存在吗？

**A**: 不是必须的。如果不提供配置文件，工具会使用内置的默认配置。但建议创建配置文件以便自定义行为。

### Q4: 配置文件支持哪些格式？

**A**: 支持 YAML 和 JSON 两种格式。推荐使用 YAML，因为更易读和编辑。

示例：
```bash
# 使用 YAML 配置
python mkdocs_index_generator.py generate knowledge/ --config config.yml

# 使用 JSON 配置
python mkdocs_index_generator.py generate knowledge/ --config config.json
```

### Q5: 如何生成示例配置文件？

**A**: 项目中已包含 `config.example.yml`，可以复制并修改：

```bash
cp config.example.yml config.yml
# 然后编辑 config.yml
```

## 使用问题

### Q6: 如何避免覆盖手动编辑的 index.md？

**A**: 默认情况下，工具会跳过已存在的 index.md 文件。只有明确使用 `--force` 选项时才会覆盖：

```bash
# 安全：跳过已存在的文件
python mkdocs_index_generator.py generate knowledge/

# 危险：会覆盖已存在的文件（但会创建备份）
python mkdocs_index_generator.py generate knowledge/ --force
```

### Q7: 覆盖文件时会丢失原内容吗？

**A**: 不会。默认配置下，覆盖前会自动创建 `.backup` 备份文件：

```
knowledge/01-foundations/index.md          # 新文件
knowledge/01-foundations/index.md.backup   # 原文件备份
```

可以在配置文件中控制备份行为：
```yaml
generation:
  create_backup: true  # 设为 false 则不创建备份
```

### Q8: 如何只处理特定类型的目录？

**A**: 使用 `--type` 选项过滤目录类型：

```bash
# 只处理难度级别目录
python mkdocs_index_generator.py generate knowledge/ --type difficulty

# 只处理主层级目录
python mkdocs_index_generator.py generate knowledge/ --type main_layer

# 只处理子主题目录
python mkdocs_index_generator.py generate knowledge/ --type sub_topic

# 只处理内容目录
python mkdocs_index_generator.py generate knowledge/ --type content
```

### Q9: 如何排除某些目录不生成 index.md？

**A**: 在配置文件的 `scan.excluded_dirs` 中添加目录名：

```yaml
scan:
  excluded_dirs:
    - "javascripts"
    - "stylesheets"
    - "_site"
    - "_wiki"
    - "templates"
    - "my-special-dir"  # 添加自定义排除目录
```

### Q10: 如何在生成前预览内容？

**A**: 使用 `preview` 命令或 `--dry-run` 选项：

```bash
# 方法 1: 使用 preview 命令
python mkdocs_index_generator.py preview knowledge/ --limit 5

# 方法 2: 使用 --dry-run 选项
python mkdocs_index_generator.py generate knowledge/ --dry-run
```

### Q11: 预览时如何查看更多目录？

**A**: 使用 `--limit` 选项控制预览数量：

```bash
# 预览前 10 个目录
python mkdocs_index_generator.py preview knowledge/ --limit 10

# 预览所有目录（设为 0）
python mkdocs_index_generator.py preview knowledge/ --limit 0
```

### Q12: 如何查看哪些目录缺失 index.md？

**A**: 使用 `scan` 命令：

```bash
python mkdocs_index_generator.py scan knowledge/
```

输出示例：
```
扫描目录: knowledge/
找到 15 个缺失 index.md 的目录：
  - knowledge/01-foundations/algorithm/
  - knowledge/01-foundations/database/
  - knowledge/02-technologies/embedded/01-hardware-layer/
  ...
```

## 模板和自定义

### Q13: 如何自定义生成的内容？

**A**: 创建自定义模板文件：

1. 创建模板目录：
   ```bash
   mkdir my-templates
   ```

2. 创建模板文件（参考默认模板）：
   ```bash
   touch my-templates/main_layer.md
   touch my-templates/sub_topic.md
   touch my-templates/difficulty.md
   touch my-templates/content.md
   ```

3. 使用自定义模板：
   ```bash
   python mkdocs_index_generator.py generate knowledge/ --template-dir my-templates/
   ```

### Q14: 模板中可以使用哪些变量？

**A**: 支持以下模板变量：

- `{{title}}`: 目录标题（自动从目录名提取）
- `{{description}}`: 目录描述
- `{{children}}`: 子项列表（子目录或文件）
- `{{breadcrumb}}`: 面包屑导航
- `{{level}}`: 目录层级
- `{{date}}`: 生成日期

示例：
```markdown
---
title: {{title}}
description: {{description}}
---

# {{title}}

{{description}}

## 内容

{{children}}

---
*生成时间：{{date}}*
```

### Q15: 如何修改标题提取规则？

**A**: 标题提取规则在 `src/analyzer.py` 中的 `extract_title` 方法。可以修改该方法来自定义标题提取逻辑。

当前规则：
- 去除数字前缀（如 `01-`, `02-`）
- 将连字符替换为空格
- 首字母大写

### Q16: 模板文件找不到会怎样？

**A**: 如果自定义模板文件不存在，工具会：
1. 记录警告日志
2. 自动回退到内置的默认模板
3. 继续正常执行

这确保了即使模板配置错误，工具也能正常工作。

## 错误处理

### Q17: 遇到权限错误怎么办？

**A**: 权限错误通常是因为：

1. **目录不可写**：
   ```bash
   # 检查目录权限
   ls -la knowledge/
   
   # 修改权限（Linux/Mac）
   chmod -R u+w knowledge/
   ```

2. **文件被锁定**：
   - 关闭正在编辑该文件的程序
   - 检查是否有其他进程占用

3. **需要管理员权限**：
   ```bash
   # Linux/Mac
   sudo python mkdocs_index_generator.py generate knowledge/
   
   # Windows（以管理员身份运行命令提示符）
   python mkdocs_index_generator.py generate knowledge/
   ```

### Q18: 生成失败时如何调试？

**A**: 按以下步骤调试：

1. **启用详细日志**：
   ```yaml
   # config.yml
   logging:
     level: "DEBUG"
     file: "debug.log"
   ```

2. **查看日志文件**：
   ```bash
   cat debug.log
   # 或
   tail -f debug.log  # 实时查看
   ```

3. **使用预览模式测试**：
   ```bash
   python mkdocs_index_generator.py generate knowledge/ --dry-run
   ```

4. **检查配置文件**：
   ```bash
   # 验证 YAML 语法
   python -c "import yaml; yaml.safe_load(open('config.yml'))"
   ```

### Q19: 配置文件格式错误怎么办？

**A**: 

1. **YAML 格式错误**：
   - 检查缩进（使用空格，不要用 Tab）
   - 检查冒号后是否有空格
   - 使用在线 YAML 验证器

2. **JSON 格式错误**：
   - 检查括号和逗号
   - 使用 JSON 验证器

3. **验证配置**：
   ```bash
   # Python 验证 YAML
   python -c "import yaml; print(yaml.safe_load(open('config.yml')))"
   
   # Python 验证 JSON
   python -c "import json; print(json.load(open('config.json')))"
   ```

### Q20: 磁盘空间不足怎么办？

**A**: 

1. **检查磁盘空间**：
   ```bash
   df -h  # Linux/Mac
   ```

2. **清理不需要的文件**：
   - 删除备份文件（*.backup）
   - 清理日志文件
   - 清理临时文件

3. **使用预览模式**（不占用空间）：
   ```bash
   python mkdocs_index_generator.py generate knowledge/ --dry-run
   ```

### Q21: 如何处理特殊字符的目录名？

**A**: 工具会自动处理大多数特殊字符。如果遇到问题：

1. **避免使用的字符**：
   - 控制字符
   - 路径分隔符（`/`, `\`）
   - 通配符（`*`, `?`）

2. **支持的字符**：
   - 中文字符 ✓
   - 连字符 `-` ✓
   - 下划线 `_` ✓
   - 数字 ✓

## 高级用法

### Q22: 如何集成到 CI/CD 流程？

**A**: 示例 CI 脚本：

```bash
#!/bin/bash
# ci-generate-index.sh

set -e  # 遇到错误立即退出

echo "生成 MkDocs 索引文件..."

python mkdocs_index_generator.py generate knowledge/ \
  --config ci-config.yml \
  --force

# 检查退出码
if [ $? -eq 0 ]; then
  echo "✓ 索引生成成功"
  
  # 提交更改（如果需要）
  git add knowledge/**/index.md
  git commit -m "Auto-generate index.md files" || true
  
  exit 0
else
  echo "✗ 索引生成失败"
  exit 1
fi
```

### Q23: 如何批量处理多个文档目录？

**A**: 使用脚本循环处理：

```bash
#!/bin/bash
# batch-generate.sh

DIRS=("knowledge" "docs" "wiki")

for dir in "${DIRS[@]}"; do
  echo "处理目录: $dir"
  python mkdocs_index_generator.py generate "$dir/" --config config.yml
done
```

### Q24: 如何定期自动更新索引？

**A**: 使用 cron 定时任务（Linux/Mac）：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天凌晨 2 点执行）
0 2 * * * cd /path/to/project && python mkdocs_index_generator.py generate knowledge/ --config config.yml >> /var/log/mkdocs-gen.log 2>&1
```

Windows 任务计划程序：
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天、每周等）
4. 操作：启动程序
5. 程序：`python`
6. 参数：`mkdocs_index_generator.py generate knowledge/`

### Q25: 如何生成统计报告？

**A**: 工具会自动生成执行报告。可以将报告保存到文件：

```bash
python mkdocs_index_generator.py generate knowledge/ > report.txt 2>&1
```

报告包含：
- 扫描的目录总数
- 缺失 index.md 的数量
- 生成成功的数量
- 失败的数量和原因
- 跳过的数量

### Q26: 如何只更新最近修改的目录？

**A**: 结合 `find` 命令和脚本：

```bash
#!/bin/bash
# update-recent.sh

# 查找最近 7 天修改的目录
find knowledge/ -type d -mtime -7 | while read dir; do
  if [ ! -f "$dir/index.md" ]; then
    echo "生成: $dir"
    python mkdocs_index_generator.py generate "$dir/" --config config.yml
  fi
done
```

### Q27: 如何验证生成的 Markdown 语法？

**A**: 使用 `validate` 命令：

```bash
python mkdocs_index_generator.py validate knowledge/
```

或使用第三方工具：
```bash
# 安装 markdownlint
npm install -g markdownlint-cli

# 验证 Markdown 文件
markdownlint knowledge/**/index.md
```

### Q28: 如何自定义日志格式？

**A**: 修改 `src/logger.py` 中的日志格式配置：

```python
# 当前格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 自定义格式
formatter = logging.Formatter(
    '[%(levelname)s] %(asctime)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### Q29: 如何扩展工具添加新功能？

**A**: 

1. **添加新的目录类型**：
   - 修改 `src/models.py` 中的 `DirectoryType` 枚举
   - 更新 `src/analyzer.py` 中的 `detect_type` 方法
   - 添加对应的模板

2. **添加新的模板变量**：
   - 在 `src/analyzer.py` 中提取新的元数据
   - 在 `src/template_engine.py` 中添加变量替换逻辑

3. **添加新的命令**：
   - 在 `src/cli.py` 中添加新的子命令
   - 实现对应的处理逻辑

### Q30: 如何贡献代码？

**A**: 

1. Fork 项目仓库
2. 创建功能分支：`git checkout -b feature/my-feature`
3. 编写代码和测试
4. 运行测试确保通过：`pytest`
5. 提交更改：`git commit -am 'Add my feature'`
6. 推送分支：`git push origin feature/my-feature`
7. 创建 Pull Request

## 获取帮助

如果以上 FAQ 没有解决您的问题：

1. **查看文档**：阅读 README.md 和设计文档
2. **查看日志**：启用 DEBUG 级别日志查看详细信息
3. **提交 Issue**：在 GitHub 上提交问题报告
4. **联系维护者**：通过邮件或项目讨论区联系

---

*最后更新：2024*
