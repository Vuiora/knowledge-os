# MkDocs Index Generator

自动生成 MkDocs 文档目录的 index.md 文件的 Python 命令行工具。

## 📋 目录

- [功能特性](#功能特性)
- [系统要求](#系统要求)
- [安装](#安装)
- [快速开始](#快速开始)
- [命令行使用](#命令行使用)
- [配置文件](#配置文件)
- [自定义模板](#自定义模板)
- [使用示例](#使用示例)
- [常见问题](#常见问题)
- [开发指南](#开发指南)
- [许可证](#许可证)

## 功能特性

- 🔍 **智能扫描**: 自动递归扫描目录结构，识别缺失的 index.md 文件
- 🎯 **类型识别**: 智能识别目录类型（主层级、子主题、难度级别、内容目录）
- 📝 **模板生成**: 基于可自定义模板生成符合 MkDocs 规范的索引页面
- ⚙️ **灵活配置**: 支持 YAML/JSON 配置文件，可自定义排除目录、模板路径等
- 🔄 **增量更新**: 支持批量生成和增量更新，避免覆盖手动编辑的内容
- 👀 **预览模式**: 生成前预览内容，确保符合预期
- 📊 **详细报告**: 提供详细的执行报告和统计信息
- 🔐 **安全备份**: 覆盖文件前自动创建备份
- 📝 **完整日志**: 支持多级别日志记录，便于调试和审计

## 系统要求

- Python 3.8 或更高版本
- pip 包管理器

## 安装

### 方法 1: 从源码安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/yourusername/mkdocs-index-generator.git
cd mkdocs-index-generator

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装
pip install -e .
```

### 方法 2: 直接使用

```bash
# 安装依赖
pip install -r requirements.txt

# 直接运行脚本
python mkdocs_index_generator.py --help
```

## 快速开始

### 1. 扫描目录

查看哪些目录缺失 index.md 文件：

```bash
python mkdocs_index_generator.py scan knowledge/
```

### 2. 预览生成内容

在实际生成前预览内容：

```bash
python mkdocs_index_generator.py preview knowledge/ --limit 5
```

### 3. 生成 index.md 文件

为所有缺失的目录生成 index.md：

```bash
python mkdocs_index_generator.py generate knowledge/
```

### 4. 使用配置文件

使用自定义配置：

```bash
python mkdocs_index_generator.py generate knowledge/ --config config.yml
```

## 命令行使用

### 命令概览

```bash
python mkdocs_index_generator.py <command> <root_dir> [options]
```

### 可用命令

#### 1. scan - 扫描目录

扫描目录结构，显示缺失 index.md 的目录列表。

```bash
python mkdocs_index_generator.py scan <root_dir> [options]
```

**示例**:
```bash
# 扫描所有目录
python mkdocs_index_generator.py scan knowledge/

# 只扫描难度级别目录
python mkdocs_index_generator.py scan knowledge/ --type difficulty

# 使用配置文件
python mkdocs_index_generator.py scan knowledge/ --config config.yml
```

#### 2. generate - 生成文件

为缺失 index.md 的目录生成索引文件。

```bash
python mkdocs_index_generator.py generate <root_dir> [options]
```

**示例**:
```bash
# 生成所有缺失的 index.md
python mkdocs_index_generator.py generate knowledge/

# 强制覆盖已存在的文件
python mkdocs_index_generator.py generate knowledge/ --force

# 预览模式（不实际写入）
python mkdocs_index_generator.py generate knowledge/ --dry-run

# 只生成特定类型的目录
python mkdocs_index_generator.py generate knowledge/ --type sub_topic

# 使用自定义模板
python mkdocs_index_generator.py generate knowledge/ --template-dir ./my-templates/
```

#### 3. preview - 预览内容

预览将要生成的内容，不实际写入文件。

```bash
python mkdocs_index_generator.py preview <root_dir> [options]
```

**示例**:
```bash
# 预览前 5 个目录
python mkdocs_index_generator.py preview knowledge/ --limit 5

# 预览所有目录
python mkdocs_index_generator.py preview knowledge/ --limit 0

# 预览特定类型
python mkdocs_index_generator.py preview knowledge/ --type difficulty
```

#### 4. validate - 验证文件

验证现有 index.md 文件的格式和内容。

```bash
python mkdocs_index_generator.py validate <root_dir>
```

### 通用选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--config CONFIG` | 配置文件路径 | `--config config.yml` |
| `--force` | 强制覆盖已存在的文件 | `--force` |
| `--dry-run` | 预览模式，不写入文件 | `--dry-run` |
| `--type TYPE` | 过滤目录类型 | `--type difficulty` |
| `--template-dir DIR` | 自定义模板目录 | `--template-dir ./templates/` |
| `--limit N` | 限制预览数量 | `--limit 10` |
| `--help` | 显示帮助信息 | `--help` |

### 目录类型

- `main_layer`: 主层级目录（如 `01-hardware-layer`）
- `sub_topic`: 子主题目录（如 `01-chip-architecture`）
- `difficulty`: 难度级别目录（`beginner`, `intermediate`, `advanced`）
- `content`: 内容目录（包含 .md 文件的目录）

### 退出码

- `0`: 成功执行
- `1`: 发生错误
- `130`: 用户取消（Ctrl+C）

## 配置文件

### 配置文件格式

支持 YAML 和 JSON 格式。推荐使用 YAML 格式，更易读。

### 配置示例

参考 `config.example.yml`:

```yaml
# 扫描配置
scan:
  root_dir: "knowledge"
  excluded_dirs:
    - "javascripts"
    - "stylesheets"
    - "_site"
    - "_wiki"
    - "templates"

# 模板配置
templates:
  main_layer: "templates/main_layer.md"
  sub_topic: "templates/sub_topic.md"
  difficulty: "templates/difficulty.md"
  content: "templates/content.md"

# 生成配置
generation:
  force_overwrite: false
  create_backup: true
  dry_run: false

# 日志配置
logging:
  level: "INFO"
  file: "mkdocs_generator.log"
```

### 配置项说明

#### scan 部分

- `root_dir`: 文档根目录路径
- `excluded_dirs`: 排除的目录列表（不生成 index.md）

#### templates 部分

- `main_layer`: 主层级目录模板路径
- `sub_topic`: 子主题目录模板路径
- `difficulty`: 难度级别目录模板路径
- `content`: 内容目录模板路径

#### generation 部分

- `force_overwrite`: 是否强制覆盖已存在的文件（默认: false）
- `create_backup`: 覆盖前是否创建备份（默认: true）
- `dry_run`: 预览模式，不实际写入（默认: false）

#### logging 部分

- `level`: 日志级别（DEBUG, INFO, WARNING, ERROR）
- `file`: 日志文件路径（留空则只输出到控制台）

## 自定义模板

### 模板变量

模板支持以下变量：

- `{{title}}`: 目录标题（自动从目录名提取）
- `{{description}}`: 目录描述
- `{{children}}`: 子项列表（子目录或文件）
- `{{breadcrumb}}`: 面包屑导航
- `{{level}}`: 目录层级
- `{{date}}`: 生成日期

### 模板示例

#### 主层级模板 (main_layer.md)

```markdown
---
title: {{title}}
description: {{description}}
---

# {{title}}

{{description}}

## 📚 子主题

{{children}}

## 🎯 学习路径

根据难度级别选择合适的学习内容：
- 🟢 beginner - 入门基础
- 🟡 intermediate - 进阶提升  
- 🔴 advanced - 高级实战

---
*最后更新：{{date}}*
```

#### 难度级别模板 (difficulty.md)

```markdown
---
title: {{title}}
description: {{description}}
---

# {{title}}

本部分包含 {{level}} 级别的学习内容。

## 📖 文档列表

{{children}}

## 💡 学习建议

根据您的学习进度，建议按照文档顺序逐步学习。

---
*最后更新：{{date}}*
```

### 创建自定义模板

1. 创建模板目录：
   ```bash
   mkdir my-templates
   ```

2. 创建模板文件（使用上述变量）：
   ```bash
   touch my-templates/main_layer.md
   touch my-templates/sub_topic.md
   touch my-templates/difficulty.md
   touch my-templates/content.md
   ```

3. 在配置文件中指定模板路径，或使用 `--template-dir` 选项：
   ```bash
   python mkdocs_index_generator.py generate knowledge/ --template-dir my-templates/
   ```

## 使用示例

### 示例 1: 首次生成所有 index.md

```bash
# 1. 扫描查看缺失的文件
python mkdocs_index_generator.py scan knowledge/

# 2. 预览生成内容
python mkdocs_index_generator.py preview knowledge/ --limit 5

# 3. 确认无误后生成
python mkdocs_index_generator.py generate knowledge/
```

### 示例 2: 只更新难度级别目录

```bash
python mkdocs_index_generator.py generate knowledge/ --type difficulty
```

### 示例 3: 强制重新生成所有文件

```bash
# 会创建备份文件
python mkdocs_index_generator.py generate knowledge/ --force
```

### 示例 4: 使用自定义配置和模板

```bash
python mkdocs_index_generator.py generate knowledge/ \
  --config my-config.yml \
  --template-dir my-templates/
```

### 示例 5: 预览模式测试

```bash
# 不会实际写入文件
python mkdocs_index_generator.py generate knowledge/ --dry-run
```

## 常见问题

### Q1: 如何避免覆盖手动编辑的 index.md？

**A**: 默认情况下，工具会跳过已存在的 index.md 文件。只有使用 `--force` 选项时才会覆盖。

### Q2: 覆盖文件时会丢失原内容吗？

**A**: 不会。默认配置下，覆盖前会自动创建 `.backup` 备份文件。

### Q3: 如何排除某些目录不生成 index.md？

**A**: 在配置文件的 `scan.excluded_dirs` 中添加目录名：

```yaml
scan:
  excluded_dirs:
    - "my-special-dir"
    - "temp"
```

### Q4: 生成的内容不符合预期怎么办？

**A**: 
1. 使用 `preview` 命令先预览内容
2. 自定义模板文件以满足需求
3. 使用 `--dry-run` 选项测试而不实际写入

### Q5: 如何查看详细的执行日志？

**A**: 在配置文件中设置日志级别为 DEBUG：

```yaml
logging:
  level: "DEBUG"
  file: "debug.log"
```

### Q6: 工具支持哪些 Python 版本？

**A**: Python 3.8 及以上版本。

### Q7: 如何集成到 CI/CD 流程？

**A**: 
```bash
# 在 CI 脚本中使用
python mkdocs_index_generator.py generate knowledge/ --config ci-config.yml

# 检查退出码
if [ $? -eq 0 ]; then
  echo "Index generation successful"
else
  echo "Index generation failed"
  exit 1
fi
```

### Q8: 生成失败时如何调试？

**A**:
1. 查看日志文件（如果配置了）
2. 使用 DEBUG 日志级别
3. 检查目录权限
4. 验证配置文件格式

### Q9: 可以只预览特定目录吗？

**A**: 可以使用 `--type` 选项过滤：

```bash
python mkdocs_index_generator.py preview knowledge/ --type difficulty --limit 10
```

### Q10: 如何贡献代码或报告问题？

**A**: 请访问项目的 GitHub 仓库提交 Issue 或 Pull Request。

## 开发指南

### 项目结构

```
mkdocs-index-generator/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   ├── logger.py          # 日志系统
│   ├── scanner.py         # 目录扫描器
│   ├── analyzer.py        # 内容分析器
│   ├── template_engine.py # 模板引擎
│   ├── file_generator.py  # 文件生成器
│   ├── config_manager.py  # 配置管理器
│   ├── reporter.py        # 报告生成器
│   ├── pipeline.py        # 处理流程
│   └── cli.py            # 命令行接口
├── tests/                 # 测试文件
│   ├── test_logger.py
│   ├── test_models.py
│   └── test_scanner.py
├── config.example.yml     # 配置示例
├── requirements.txt       # 依赖列表
├── setup.py              # 安装配置
└── README.md             # 项目说明
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_scanner.py

# 运行属性测试
pytest -v tests/

# 检查代码覆盖率
pytest --cov=src tests/

# 生成覆盖率报告
pytest --cov=src --cov-report=html tests/
```

### 代码风格

```bash
# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```

### 添加新功能

1. 在 `src/` 目录下创建或修改模块
2. 在 `tests/` 目录下添加测试
3. 更新文档
4. 运行测试确保通过
5. 提交 Pull Request

## 许可证

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
