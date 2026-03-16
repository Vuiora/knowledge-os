# Requirements Document

## Introduction

本文档定义了 MkDocs Index 自动生成工具的需求。该系统旨在自动扫描 knowledge 目录结构，识别缺失的 index.md 文件，并根据目录类型和内容智能生成符合 MkDocs 规范的索引页面。

## Glossary

- **System**: MkDocs Index Generator - 自动生成 index.md 文件的工具系统
- **Knowledge_Directory**: knowledge/ 目录 - MkDocs 文档的根目录
- **Index_File**: index.md 文件 - MkDocs 目录的索引页面
- **Directory_Scanner**: 目录扫描器 - 扫描并分析目录结构的组件
- **Template_Engine**: 模板引擎 - 根据模板生成 index.md 内容的组件
- **Content_Analyzer**: 内容分析器 - 分析目录内容和类型的组件
- **Excluded_Directory**: 排除目录 - 不需要生成 index.md 的特殊目录（如 javascripts, stylesheets, _site, _wiki 等）

## Requirements

### Requirement 1: 目录扫描与分析

**User Story:** 作为系统管理员，我希望系统能够自动扫描 knowledge 目录，识别所有缺失 index.md 的目录，以便了解需要生成的文件数量和位置。

#### Acceptance Criteria

1. WHEN System 启动扫描时，THE Directory_Scanner SHALL 递归遍历 Knowledge_Directory 下的所有子目录
2. WHEN Directory_Scanner 检查每个目录时，THE Directory_Scanner SHALL 判断该目录是否存在 index.md 文件
3. WHEN 目录属于 Excluded_Directory 列表时，THE Directory_Scanner SHALL 跳过该目录不进行处理
4. WHEN 扫描完成时，THE System SHALL 返回缺失 index.md 的目录列表，包含完整路径和目录层级信息
5. THE System SHALL 将目录分类为：主层级目录、子主题目录、难度级别目录、内容目录

### Requirement 2: 目录类型识别

**User Story:** 作为内容管理员，我希望系统能够识别不同类型的目录，以便为不同类型生成合适的索引内容。

#### Acceptance Criteria

1. WHEN Content_Analyzer 分析目录名称包含 "beginner"、"intermediate" 或 "advanced" 时，THE Content_Analyzer SHALL 将其标记为难度级别目录
2. WHEN 目录路径匹配 "XX-layer" 或 "XX-concerns" 模式时，THE Content_Analyzer SHALL 将其标记为主层级目录
3. WHEN 目录包含数字前缀（如 "01-"、"02-"）且不是难度级别目录时，THE Content_Analyzer SHALL 将其标记为子主题目录
4. WHEN 目录包含 .md 文件（除 index.md 外）时，THE Content_Analyzer SHALL 将其标记为内容目录
5. THE Content_Analyzer SHALL 为每个目录类型返回相应的元数据（标题、描述、子项列表）

### Requirement 3: 内容智能生成

**User Story:** 作为文档维护者，我希望生成的 index.md 文件包含有意义的内容和导航链接，以便用户能够快速了解该目录的内容结构。

#### Acceptance Criteria

1. WHEN Template_Engine 为主层级目录生成内容时，THE Template_Engine SHALL 包含目录标题、概述描述和子主题列表
2. WHEN Template_Engine 为子主题目录生成内容时，THE Template_Engine SHALL 包含主题介绍、难度级别导航和相关文档链接
3. WHEN Template_Engine 为难度级别目录生成内容时，THE Template_Engine SHALL 包含难度说明、学习路径和文档列表
4. WHEN Template_Engine 为内容目录生成内容时，THE Template_Engine SHALL 列出该目录下所有 .md 文件的链接和简要描述
5. THE Template_Engine SHALL 从目录名称和路径自动提取中文标题（去除数字前缀和连字符）
6. THE Template_Engine SHALL 为每个生成的 index.md 添加标准的 YAML front matter（包含 title 和 description）

### Requirement 4: 模板系统

**User Story:** 作为开发者，我希望系统使用可配置的模板来生成内容，以便根据需要调整生成的格式和样式。

#### Acceptance Criteria

1. THE System SHALL 支持至少 4 种模板类型：主层级模板、子主题模板、难度级别模板、内容目录模板
2. WHEN 用户提供自定义模板文件时，THE Template_Engine SHALL 使用自定义模板替代默认模板
3. THE Template_Engine SHALL 支持模板变量替换（如 {{title}}、{{description}}、{{children}}）
4. WHEN 模板文件不存在或格式错误时，THE System SHALL 使用内置的默认模板并记录警告
5. THE System SHALL 支持模板继承和复用机制

### Requirement 5: 批量文件生成

**User Story:** 作为系统管理员，我希望能够一次性生成所有缺失的 index.md 文件，以便快速完成文档结构的补全。

#### Acceptance Criteria

1. WHEN 用户执行批量生成命令时，THE System SHALL 为所有缺失 index.md 的目录生成文件
2. WHEN 生成文件时，THE System SHALL 确保目标目录存在且可写
3. WHEN 文件生成成功时，THE System SHALL 记录生成的文件路径和状态
4. WHEN 文件生成失败时，THE System SHALL 记录错误信息并继续处理其他文件
5. WHEN 批量生成完成时，THE System SHALL 输出统计报告（成功数量、失败数量、跳过数量）

### Requirement 6: 预览与验证

**User Story:** 作为内容审核者，我希望在实际生成文件前能够预览生成的内容，以便确认内容的正确性。

#### Acceptance Criteria

1. WHEN 用户执行预览命令时，THE System SHALL 显示将要生成的 index.md 内容而不实际写入文件
2. WHEN 预览模式启用时，THE System SHALL 为每个目录显示：目录路径、目录类型、生成的内容预览
3. THE System SHALL 支持预览单个目录或批量预览所有目录
4. WHEN 用户确认预览内容后，THE System SHALL 提供选项继续执行实际生成
5. THE System SHALL 在预览模式下验证生成内容的 Markdown 语法正确性

### Requirement 7: 增量更新支持

**User Story:** 作为文档维护者，我希望系统能够检测已存在的 index.md 文件，避免覆盖手动编辑的内容。

#### Acceptance Criteria

1. WHEN 目录已存在 index.md 文件时，THE System SHALL 默认跳过该目录
2. WHEN 用户启用强制覆盖模式时，THE System SHALL 覆盖已存在的 index.md 文件
3. WHEN 覆盖文件前，THE System SHALL 创建备份文件（如 index.md.backup）
4. THE System SHALL 支持仅更新特定类型目录的 index.md 文件
5. THE System SHALL 记录所有跳过和覆盖的操作日志

### Requirement 8: 配置文件支持

**User Story:** 作为系统配置员，我希望通过配置文件定义扫描规则和生成选项，以便灵活控制系统行为。

#### Acceptance Criteria

1. THE System SHALL 支持 YAML 或 JSON 格式的配置文件
2. WHEN 配置文件存在时，THE System SHALL 从配置文件读取：排除目录列表、模板路径、输出选项
3. WHEN 配置文件不存在时，THE System SHALL 使用默认配置并可选地生成示例配置文件
4. THE System SHALL 验证配置文件的格式和内容正确性
5. WHEN 配置项无效时，THE System SHALL 显示错误信息并使用默认值

### Requirement 9: 日志与报告

**User Story:** 作为运维人员，我希望系统提供详细的日志和执行报告，以便追踪问题和审计操作。

#### Acceptance Criteria

1. THE System SHALL 记录所有扫描、分析和生成操作的日志
2. WHEN 操作完成时，THE System SHALL 生成包含以下信息的报告：扫描的目录总数、缺失 index.md 的数量、生成成功的数量、失败的数量和原因
3. THE System SHALL 支持不同日志级别（DEBUG、INFO、WARNING、ERROR）
4. WHEN 错误发生时，THE System SHALL 记录详细的错误堆栈和上下文信息
5. THE System SHALL 支持将日志输出到文件或控制台

### Requirement 10: 命令行接口

**User Story:** 作为开发者，我希望通过命令行工具执行各种操作，以便集成到自动化脚本和 CI/CD 流程中。

#### Acceptance Criteria

1. THE System SHALL 提供命令行接口支持以下命令：scan（扫描）、generate（生成）、preview（预览）、validate（验证）
2. WHEN 用户执行命令时，THE System SHALL 支持选项参数：--config（配置文件路径）、--force（强制覆盖）、--dry-run（预览模式）、--type（目录类型过滤）
3. THE System SHALL 提供 --help 选项显示使用说明和示例
4. WHEN 命令执行成功时，THE System SHALL 返回退出码 0
5. WHEN 命令执行失败时，THE System SHALL 返回非零退出码并输出错误信息
