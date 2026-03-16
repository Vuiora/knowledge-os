"""
核心数据模型定义
定义系统中使用的所有数据结构
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime


class DirectoryType(Enum):
    """目录类型枚举"""
    MAIN_LAYER = "main_layer"      # 主层级目录 (XX-layer, XX-concerns)
    SUB_TOPIC = "sub_topic"        # 子主题目录 (01-xxx, 02-xxx)
    DIFFICULTY = "difficulty"      # 难度级别 (beginner, intermediate, advanced)
    CONTENT = "content"            # 内容目录 (包含 .md 文件)
    UNKNOWN = "unknown"            # 未知类型


@dataclass
class DirectoryInfo:
    """扫描得到的目录信息"""
    path: str                      # 完整路径
    name: str                      # 目录名称
    level: int                     # 目录层级
    has_index: bool                # 是否已有 index.md
    children: List[str]            # 子目录列表
    markdown_files: List[str]      # Markdown 文件列表
    parent: Optional[str] = None   # 父目录路径


@dataclass
class ChildItem:
    """子项信息"""
    name: str                      # 文件/目录名
    title: str                     # 显示标题
    path: str                      # 相对路径
    type: str                      # "directory" or "file"
    description: Optional[str] = None


@dataclass
class DirectoryMetadata:
    """分析得到的目录元数据"""
    type: DirectoryType
    title: str
    description: str
    children: List[ChildItem]
    breadcrumb: List[str]
    level_indicator: Optional[str] = None  # 🟢🟡🔴


@dataclass
class Config:
    """系统配置"""
    root_dir: str
    excluded_dirs: List[str]
    template_paths: dict
    force_overwrite: bool
    create_backup: bool
    dry_run: bool
    log_level: str
    log_file: str


@dataclass
class GenerateOptions:
    """文件生成选项"""
    force_overwrite: bool = False
    create_backup: bool = True
    dry_run: bool = False


@dataclass
class GenerateResult:
    """文件生成结果"""
    success: bool
    path: str
    action: str  # "created", "skipped", "overwritten", "failed"
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorInfo:
    """错误信息"""
    path: str
    error_type: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Summary:
    """执行摘要"""
    total_scanned: int
    missing_index: int
    generated: int
    skipped: int
    failed: int
    duration: float
    errors: List[ErrorInfo] = field(default_factory=list)
