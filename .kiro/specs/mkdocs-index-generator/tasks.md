# Implementation Plan: MkDocs Index Generator

## Overview

本实现计划将 MkDocs Index Generator 分解为增量式的开发任务。每个任务都是独立的代码单元，按照从核心功能到高级特性的顺序组织。实现采用 Python 3.8+，使用 hypothesis 库进行属性测试。

## Tasks

- [x] 1. 项目初始化和核心数据结构
  - 创建项目目录结构
  - 定义核心数据类（DirectoryInfo, DirectoryMetadata, Config 等）
  - 设置 Python 包管理（requirements.txt, setup.py）
  - 配置日志系统基础框架
  - _Requirements: 9.1, 9.3_

- [ ]* 1.1 编写数据结构单元测试
  - 测试数据类的创建和序列化
  - 测试枚举类型的有效性
  - _Requirements: 所有数据模型_

- [x] 2. 实现目录扫描器 (DirectoryScanner)
  - [x] 2.1 实现基础扫描功能
    - 递归遍历目录
    - 检测 index.md 文件存在性
    - 收集目录信息（路径、层级、子目录、文件列表）
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 2.2 实现排除目录过滤
    - 支持排除目录列表
    - 跳过排除目录及其子目录
    - _Requirements: 1.3_

  - [ ]* 2.3 编写扫描器属性测试
    - **Property 1: 扫描完整性**
    - **Property 2: 排除目录过滤**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

  - [ ]* 2.4 编写扫描器单元测试
    - 测试空目录
    - 测试深层嵌套目录
    - 测试特殊字符目录名
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 3. 实现内容分析器 (ContentAnalyzer)
  - [x] 3.1 实现目录类型检测
    - 识别难度级别目录（beginner/intermediate/advanced）
    - 识别主层级目录（XX-layer, XX-concerns）
    - 识别子主题目录（数字前缀）
    - 识别内容目录（包含 .md 文件）
    - _Requirements: 1.5, 2.1, 2.2, 2.3, 2.4_

  - [x] 3.2 实现元数据提取
    - 从目录名提取标题（去除前缀和连字符）
    - 生成目录描述
    - 收集子项列表
    - 构建面包屑导航
    - _Requirements: 2.5, 3.5_

  - [ ]* 3.3 编写分析器属性测试
    - **Property 3: 目录类型分类正确性**
    - **Property 4: 元数据完整性**
    - **Property 6: 标题提取正确性**
    - **Validates: Requirements 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.5**

  - [ ]* 3.4 编写分析器单元测试
    - 测试各种目录名格式
    - 测试边缘情况（空名称、特殊字符）
    - _Requirements: 2.1, 2.2, 2.3, 2.4_


- [x] 4. 实现模板引擎 (TemplateEngine)
  - [x] 4.1 创建默认模板
    - 主层级模板（main_layer.md）
    - 子主题模板（sub_topic.md）
    - 难度级别模板（difficulty.md）
    - 内容目录模板（content.md）
    - _Requirements: 4.1_

  - [x] 4.2 实现模板加载和管理
    - 加载自定义模板文件
    - 回退到默认模板
    - 模板缓存机制
    - _Requirements: 4.2, 4.4_

  - [x] 4.3 实现模板渲染
    - 变量替换（{{title}}, {{description}}, {{children}} 等）
    - 生成 YAML front matter
    - 格式化子项列表
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 4.3_

  - [ ]* 4.4 编写模板引擎属性测试
    - **Property 5: 模板内容元素完整性**
    - **Property 7: Front Matter 格式正确性**
    - **Property 8: 模板变量替换**
    - **Property 9: 自定义模板优先级**
    - **Property 10: 模板错误回退**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.6, 4.2, 4.3, 4.4**

  - [ ]* 4.5 编写模板引擎单元测试
    - 测试各种模板变量组合
    - 测试模板文件不存在的情况
    - 测试模板语法错误
    - _Requirements: 4.2, 4.3, 4.4_

- [x] 5. 实现配置管理器 (ConfigManager)
  - [x] 5.1 实现配置加载
    - 支持 YAML 格式配置文件
    - 支持 JSON 格式配置文件
    - 提供默认配置值
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 5.2 实现配置验证
    - 验证配置文件格式
    - 验证配置项类型和值
    - 处理无效配置项
    - _Requirements: 8.4, 8.5_

  - [ ]* 5.3 编写配置管理器属性测试
    - **Property 22: 配置文件加载**
    - **Property 23: 默认配置回退**
    - **Property 24: 配置验证**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

  - [ ]* 5.4 编写配置管理器单元测试
    - 测试有效配置文件
    - 测试无效配置文件
    - 测试配置文件不存在
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 6. 检查点 - 核心功能验证
  - 确保所有核心模块测试通过
  - 验证模块间集成正常
  - 如有问题，询问用户

- [x] 7. 实现文件生成器 (FileGenerator)
  - [x] 7.1 实现文件写入功能
    - 验证目标目录权限
    - 写入 index.md 文件
    - 处理文件系统错误
    - _Requirements: 5.1, 5.2_

  - [x] 7.2 实现覆盖和备份逻辑
    - 检测已存在的 index.md
    - 默认跳过已存在文件
    - 强制覆盖模式
    - 创建备份文件
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 7.3 实现预览模式（dry-run）
    - 预览模式不写入文件
    - 返回将要生成的内容
    - _Requirements: 6.1_

  - [ ]* 7.4 编写文件生成器属性测试
    - **Property 12: 文件系统权限检查**
    - **Property 15: 预览模式不写入文件**
    - **Property 18: 默认跳过已存在文件**
    - **Property 19: 强制覆盖模式**
    - **Property 20: 备份文件创建**
    - **Validates: Requirements 5.2, 6.1, 7.1, 7.2, 7.3**

  - [ ]* 7.5 编写文件生成器单元测试
    - 测试权限不足的情况
    - 测试磁盘空间不足
    - 测试文件锁定
    - _Requirements: 5.2, 7.1, 7.2_


- [x] 8. 实现报告生成器 (Reporter)
  - [x] 8.1 实现结果收集
    - 收集生成结果（成功、失败、跳过）
    - 记录错误信息
    - 计算统计数据
    - _Requirements: 5.3, 5.4, 5.5_

  - [x] 8.2 实现报告输出
    - 文本格式报告
    - JSON 格式报告
    - 包含详细的错误信息
    - _Requirements: 9.2, 9.4_

  - [ ]* 8.3 编写报告生成器属性测试
    - **Property 14: 统计报告准确性**
    - **Property 25: 错误日志详细性**
    - **Validates: Requirements 5.5, 9.2, 9.4**

  - [ ]* 8.4 编写报告生成器单元测试
    - 测试空结果集
    - 测试大量结果
    - 测试报告格式
    - _Requirements: 9.2_

- [x] 9. 实现日志系统增强
  - [x] 9.1 完善日志功能
    - 支持不同日志级别
    - 支持文件和控制台输出
    - 记录操作上下文
    - _Requirements: 9.1, 9.3, 9.5_

  - [ ]* 9.2 编写日志系统属性测试
    - **Property 13: 操作日志完整性**
    - **Validates: Requirements 5.3, 7.5, 9.1**

- [x] 10. 实现命令行接口 (CLI)
  - [x] 10.1 实现命令解析
    - scan 命令
    - generate 命令
    - preview 命令
    - validate 命令
    - _Requirements: 10.1_

  - [x] 10.2 实现命令选项
    - --config 配置文件路径
    - --force 强制覆盖
    - --dry-run 预览模式
    - --type 目录类型过滤
    - --help 帮助信息
    - _Requirements: 10.2, 10.3_

  - [x] 10.3 实现命令执行流程
    - 加载配置
    - 协调各模块执行
    - 处理错误和退出码
    - _Requirements: 10.4, 10.5_

  - [ ]* 10.4 编写 CLI 属性测试
    - **Property 21: 类型过滤功能**
    - **Property 26: 退出码正确性**
    - **Validates: Requirements 7.4, 10.4, 10.5**

  - [ ]* 10.5 编写 CLI 单元测试
    - 测试参数解析
    - 测试命令执行
    - 测试帮助信息
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 11. 检查点 - 完整功能验证
  - 运行所有测试确保通过
  - 手动测试主要使用场景
  - 如有问题，询问用户

- [x] 12. 实现端到端集成
  - [x] 12.1 集成所有模块
    - 连接扫描器、分析器、模板引擎、生成器
    - 实现完整的处理流程
    - 处理模块间的数据传递
    - _Requirements: 所有需求_

  - [x] 12.2 实现批量处理逻辑
    - 批量扫描和生成
    - 错误恢复机制
    - 进度显示
    - _Requirements: 5.1, 5.4_

  - [ ]* 12.3 编写集成属性测试
    - **Property 11: 批量生成完整性**
    - **Property 16: 预览输出完整性**
    - **Property 17: Markdown 语法有效性**
    - **Validates: Requirements 5.1, 5.4, 6.2, 6.5**

  - [ ]* 12.4 编写端到端测试
    - 测试完整的 scan 流程
    - 测试完整的 generate 流程
    - 测试完整的 preview 流程
    - _Requirements: 所有需求_

- [x] 13. 文档和示例
  - [x] 13.1 编写用户文档
    - README.md 使用说明
    - 配置文件示例
    - 命令行使用示例
    - 常见问题解答

  - [x] 13.2 创建示例配置和模板
    - 示例配置文件（config.example.yml）
    - 自定义模板示例
    - 测试数据集

- [x] 14. 最终检查点
  - 运行完整测试套件
  - 验证所有 26 个属性测试通过
  - 检查代码覆盖率（目标 > 85%）
  - 确认所有需求都已实现
  - 询问用户是否需要调整

## Notes

- 标记 `*` 的任务为可选任务，可以跳过以加快 MVP 开发
- 每个任务都引用了相关的需求编号以便追溯
- 检查点任务确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证特定示例和边缘情况
- 建议按顺序执行任务，每个任务完成后进行验证

