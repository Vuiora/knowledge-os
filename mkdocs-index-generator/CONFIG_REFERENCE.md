# 配置文件参考

本文档详细说明 MkDocs Index Generator 配置文件的所有选项。

## 配置文件格式

支持两种格式：

- **YAML** (推荐): `config.yml`
- **JSON**: `config.json`

## 完整配置示例

```yaml
# 扫描配置
scan:
  # 文档根目录
  root_dir: "knowledge"
  
  # 排除的目录列表
  excluded_dirs:
    - "javascripts"
    - "stylesheets"
    - "_site"
    - "_wiki"
    - "templates"
    - ".git"
    - "__pycache__"
    - "node_modules"

# 模板配置
templates:
  # 主层级目录模板
  main_layer: "templates/main_layer.md"
  
  # 子主题目录模板
  sub_topic: "templates/sub_topic.md"
  
  # 难度级别目录模板
  difficulty: "templates/difficulty.md"
  
  # 内容目录模板
  content: "templates/content.md"

# 生成配置
generation:
  # 是否强制覆盖已存在的文件
  force_overwrite: false
  
  # 覆盖前是否创建备份
  create_backup: true
  
  # 预览模式（不实际写入文件）
  dry_run: false

# 日志配置
logging:
  # 日志级别: DEBUG, INFO, WARNING, ERROR
  level: "INFO"
  
  # 日志文件路径（留空则只输出到控制台）
  file: "mkdocs_generator.log"
```

## 配置项详解

### scan 部分

扫描相关的配置。

#### root_dir

- **类型**: 字符串
- **必需**: 是
- **默认值**: 无
- **说明**: 文档根目录的路径，相对于配置文件或当前工作目录

**示例**:
```yaml
scan:
  root_dir: "knowledge"
```

```yaml
scan:
  root_dir: "/absolute/path/to/knowledge"
```

#### excluded_dirs

- **类型**: 字符串列表
- **必需**: 否
- **默认值**: `[]`
- **说明**: 需要排除的目录名称列表，这些目录及其子目录不会被扫描和生成 index.md

**常见排除目录**:
```yaml
scan:
  excluded_dirs:
    # 前端资源目录
    - "javascripts"
    - "stylesheets"
    - "images"
    - "assets"
    
    # 构建输出目录
    - "_site"
    - "site"
    - "build"
    - "dist"
    
    # 内部目录
    - "_wiki"
    - "_drafts"
    - "templates"
    
    # 版本控制
    - ".git"
    - ".svn"
    
    # 依赖和缓存
    - "node_modules"
    - "__pycache__"
    - ".pytest_cache"
    
    # 临时文件
    - "temp"
    - "tmp"
    - "backup"
```

### templates 部分

模板文件路径配置。

#### main_layer

- **类型**: 字符串
- **必需**: 否
- **默认值**: 内置默认模板
- **说明**: 主层级目录（如 `01-hardware-layer`）的模板文件路径

**示例**:
```yaml
templates:
  main_layer: "templates/main_layer.md"
```

```yaml
templates:
  main_layer: "/absolute/path/to/custom_main_layer.md"
```

#### sub_topic

- **类型**: 字符串
- **必需**: 否
- **默认值**: 内置默认模板
- **说明**: 子主题目录（如 `01-chip-architecture`）的模板文件路径

**示例**:
```yaml
templates:
  sub_topic: "templates/sub_topic.md"
```

#### difficulty

- **类型**: 字符串
- **必需**: 否
- **默认值**: 内置默认模板
- **说明**: 难度级别目录（`beginner`, `intermediate`, `advanced`）的模板文件路径

**示例**:
```yaml
templates:
  difficulty: "templates/difficulty.md"
```

#### content

- **类型**: 字符串
- **必需**: 否
- **默认值**: 内置默认模板
- **说明**: 内容目录（包含 .md 文件的目录）的模板文件路径

**示例**:
```yaml
templates:
  content: "templates/content.md"
```

### generation 部分

文件生成行为配置。

#### force_overwrite

- **类型**: 布尔值
- **必需**: 否
- **默认值**: `false`
- **说明**: 是否强制覆盖已存在的 index.md 文件

**行为**:
- `false`: 跳过已存在的 index.md 文件（默认，安全）
- `true`: 覆盖已存在的 index.md 文件（危险，但会创建备份）

**示例**:
```yaml
generation:
  force_overwrite: false  # 安全模式
```

```yaml
generation:
  force_overwrite: true   # 强制覆盖模式
```

**使用场景**:
- 开发环境: 可以设为 `true` 方便测试
- 生产环境: 应该设为 `false` 保护手动编辑的内容
- CI/CD: 根据需求决定，通常设为 `true`

#### create_backup

- **类型**: 布尔值
- **必需**: 否
- **默认值**: `true`
- **说明**: 覆盖文件前是否创建备份

**行为**:
- `true`: 覆盖前创建 `.backup` 备份文件（推荐）
- `false`: 不创建备份，直接覆盖

**备份文件命名**:
```
原文件: knowledge/01-foundations/index.md
备份文件: knowledge/01-foundations/index.md.backup
```

**示例**:
```yaml
generation:
  create_backup: true   # 推荐
```

**注意**: 只有在 `force_overwrite: true` 时才会触发备份

#### dry_run

- **类型**: 布尔值
- **必需**: 否
- **默认值**: `false`
- **说明**: 预览模式，不实际写入文件

**行为**:
- `false`: 正常模式，会写入文件
- `true`: 预览模式，只显示将要生成的内容，不写入文件

**示例**:
```yaml
generation:
  dry_run: false  # 正常模式
```

```yaml
generation:
  dry_run: true   # 预览模式
```

**使用场景**:
- 测试配置是否正确
- 预览生成内容
- 验证模板效果

### logging 部分

日志记录配置。

#### level

- **类型**: 字符串
- **必需**: 否
- **默认值**: `"INFO"`
- **说明**: 日志级别

**可选值**:
- `"DEBUG"`: 详细调试信息（最详细）
- `"INFO"`: 一般信息（推荐）
- `"WARNING"`: 警告信息
- `"ERROR"`: 错误信息（最简洁）

**示例**:
```yaml
logging:
  level: "INFO"     # 生产环境
```

```yaml
logging:
  level: "DEBUG"    # 开发/调试
```

```yaml
logging:
  level: "WARNING"  # 只记录问题
```

**各级别输出内容**:

- **DEBUG**: 所有操作细节、变量值、函数调用等
- **INFO**: 扫描进度、生成结果、统计信息
- **WARNING**: 配置问题、模板回退、跳过的文件
- **ERROR**: 文件系统错误、权限问题、致命错误

#### file

- **类型**: 字符串
- **必需**: 否
- **默认值**: `""`（空字符串，只输出到控制台）
- **说明**: 日志文件路径

**行为**:
- 空字符串或不设置: 只输出到控制台
- 指定路径: 同时输出到控制台和文件

**示例**:
```yaml
logging:
  file: ""  # 只输出到控制台
```

```yaml
logging:
  file: "mkdocs_generator.log"  # 输出到文件
```

```yaml
logging:
  file: "/var/log/mkdocs-gen.log"  # 绝对路径
```

**日志文件管理**:
- 日志文件会追加内容，不会覆盖
- 建议定期清理或轮转日志文件
- 可以使用不同的日志文件名区分环境

## 配置文件示例

### 最小配置

只包含必需的配置项：

```yaml
scan:
  root_dir: "knowledge"
```

### 开发环境配置

适合开发和测试：

```yaml
scan:
  root_dir: "knowledge"
  excluded_dirs:
    - "_site"
    - "_wiki"

generation:
  force_overwrite: true
  create_backup: true
  dry_run: false

logging:
  level: "DEBUG"
  file: "dev.log"
```

### 生产环境配置

适合正式部署：

```yaml
scan:
  root_dir: "knowledge"
  excluded_dirs:
    - "javascripts"
    - "stylesheets"
    - "_site"
    - "_wiki"
    - "templates"

generation:
  force_overwrite: false
  create_backup: true
  dry_run: false

logging:
  level: "WARNING"
  file: "prod.log"
```

### CI/CD 配置

适合自动化流程：

```yaml
scan:
  root_dir: "knowledge"
  excluded_dirs:
    - "_site"
    - "_wiki"

generation:
  force_overwrite: true
  create_backup: true
  dry_run: false

logging:
  level: "INFO"
  file: "ci.log"
```

## JSON 格式配置

如果使用 JSON 格式，配置结构相同：

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
    "file": "mkdocs_generator.log"
  }
}
```

## 配置验证

### 验证 YAML 配置

```bash
# 使用 Python 验证
python -c "import yaml; yaml.safe_load(open('config.yml'))"

# 如果没有输出，说明格式正确
```

### 验证 JSON 配置

```bash
# 使用 Python 验证
python -c "import json; json.load(open('config.json'))"

# 如果没有输出，说明格式正确
```

### 常见配置错误

#### YAML 格式错误

```yaml
# 错误：缩进使用 Tab
scan:
	root_dir: "knowledge"  # ✗ 使用了 Tab

# 正确：使用空格
scan:
  root_dir: "knowledge"  # ✓ 使用空格
```

```yaml
# 错误：冒号后没有空格
scan:
  root_dir:"knowledge"  # ✗ 冒号后没有空格

# 正确：冒号后有空格
scan:
  root_dir: "knowledge"  # ✓ 冒号后有空格
```

#### JSON 格式错误

```json
// 错误：最后一项有逗号
{
  "scan": {
    "root_dir": "knowledge",  // ✗ 最后一项不应有逗号
  }
}

// 正确：最后一项没有逗号
{
  "scan": {
    "root_dir": "knowledge"  // ✓ 最后一项没有逗号
  }
}
```

## 配置优先级

配置的优先级顺序（从高到低）：

1. 命令行参数（如 `--force`, `--dry-run`）
2. 配置文件（通过 `--config` 指定）
3. 默认配置

**示例**:
```bash
# 配置文件中 force_overwrite: false
# 但命令行使用 --force
python mkdocs_index_generator.py generate knowledge/ --config config.yml --force

# 结果：使用命令行的 --force，会覆盖文件
```

## 环境变量

目前不支持通过环境变量配置，但可以在脚本中实现：

```bash
#!/bin/bash

# 根据环境选择配置文件
if [ "$ENV" = "production" ]; then
  CONFIG="config-prod.yml"
elif [ "$ENV" = "development" ]; then
  CONFIG="config-dev.yml"
else
  CONFIG="config.yml"
fi

python mkdocs_index_generator.py generate knowledge/ --config "$CONFIG"
```

---

*最后更新：2024*
