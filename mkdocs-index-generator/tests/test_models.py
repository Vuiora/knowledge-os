"""
测试核心数据模型
"""

import pytest
from datetime import datetime
from src.models import (
    DirectoryType,
    DirectoryInfo,
    ChildItem,
    DirectoryMetadata,
    Config,
    GenerateOptions,
    GenerateResult,
    ErrorInfo,
    Summary
)


class TestDirectoryType:
    """测试目录类型枚举"""
    
    def test_directory_type_values(self):
        """测试枚举值"""
        assert DirectoryType.MAIN_LAYER.value == "main_layer"
        assert DirectoryType.SUB_TOPIC.value == "sub_topic"
        assert DirectoryType.DIFFICULTY.value == "difficulty"
        assert DirectoryType.CONTENT.value == "content"
        assert DirectoryType.UNKNOWN.value == "unknown"


class TestDirectoryInfo:
    """测试目录信息数据类"""
    
    def test_create_directory_info(self):
        """测试创建目录信息"""
        dir_info = DirectoryInfo(
            path="/test/path",
            name="test",
            level=1,
            has_index=False,
            children=["child1", "child2"],
            markdown_files=["file1.md", "file2.md"]
        )
        
        assert dir_info.path == "/test/path"
        assert dir_info.name == "test"
        assert dir_info.level == 1
        assert dir_info.has_index is False
        assert len(dir_info.children) == 2
        assert len(dir_info.markdown_files) == 2
        assert dir_info.parent is None
    
    def test_directory_info_with_parent(self):
        """测试带父目录的目录信息"""
        dir_info = DirectoryInfo(
            path="/test/path/child",
            name="child",
            level=2,
            has_index=True,
            children=[],
            markdown_files=[],
            parent="/test/path"
        )
        
        assert dir_info.parent == "/test/path"


class TestChildItem:
    """测试子项数据类"""
    
    def test_create_child_item(self):
        """测试创建子项"""
        child = ChildItem(
            name="test.md",
            title="Test",
            path="./test.md",
            type="file"
        )
        
        assert child.name == "test.md"
        assert child.title == "Test"
        assert child.path == "./test.md"
        assert child.type == "file"
        assert child.description is None


class TestDirectoryMetadata:
    """测试目录元数据数据类"""
    
    def test_create_metadata(self):
        """测试创建元数据"""
        metadata = DirectoryMetadata(
            type=DirectoryType.MAIN_LAYER,
            title="Test Layer",
            description="Test description",
            children=[],
            breadcrumb=["home", "test"]
        )
        
        assert metadata.type == DirectoryType.MAIN_LAYER
        assert metadata.title == "Test Layer"
        assert metadata.description == "Test description"
        assert len(metadata.children) == 0
        assert len(metadata.breadcrumb) == 2
        assert metadata.level_indicator is None


class TestConfig:
    """测试配置数据类"""
    
    def test_create_config(self):
        """测试创建配置"""
        config = Config(
            root_dir="knowledge",
            excluded_dirs=["_site", "_wiki"],
            template_paths={"main_layer": "templates/main.md"},
            force_overwrite=False,
            create_backup=True,
            dry_run=False,
            log_level="INFO",
            log_file="test.log"
        )
        
        assert config.root_dir == "knowledge"
        assert len(config.excluded_dirs) == 2
        assert config.force_overwrite is False
        assert config.create_backup is True
        assert config.dry_run is False
        assert config.log_level == "INFO"


class TestGenerateOptions:
    """测试生成选项数据类"""
    
    def test_default_options(self):
        """测试默认选项"""
        options = GenerateOptions()
        
        assert options.force_overwrite is False
        assert options.create_backup is True
        assert options.dry_run is False
    
    def test_custom_options(self):
        """测试自定义选项"""
        options = GenerateOptions(
            force_overwrite=True,
            create_backup=False,
            dry_run=True
        )
        
        assert options.force_overwrite is True
        assert options.create_backup is False
        assert options.dry_run is True


class TestGenerateResult:
    """测试生成结果数据类"""
    
    def test_create_result(self):
        """测试创建结果"""
        result = GenerateResult(
            success=True,
            path="/test/index.md",
            action="created",
            message="File created successfully"
        )
        
        assert result.success is True
        assert result.path == "/test/index.md"
        assert result.action == "created"
        assert result.message == "File created successfully"
        assert isinstance(result.timestamp, datetime)


class TestErrorInfo:
    """测试错误信息数据类"""
    
    def test_create_error_info(self):
        """测试创建错误信息"""
        error = ErrorInfo(
            path="/test/path",
            error_type="PermissionError",
            message="Permission denied"
        )
        
        assert error.path == "/test/path"
        assert error.error_type == "PermissionError"
        assert error.message == "Permission denied"
        assert isinstance(error.timestamp, datetime)


class TestSummary:
    """测试执行摘要数据类"""
    
    def test_create_summary(self):
        """测试创建摘要"""
        summary = Summary(
            total_scanned=100,
            missing_index=50,
            generated=45,
            skipped=3,
            failed=2,
            duration=10.5
        )
        
        assert summary.total_scanned == 100
        assert summary.missing_index == 50
        assert summary.generated == 45
        assert summary.skipped == 3
        assert summary.failed == 2
        assert summary.duration == 10.5
        assert len(summary.errors) == 0
    
    def test_summary_with_errors(self):
        """测试带错误的摘要"""
        error = ErrorInfo(
            path="/test",
            error_type="IOError",
            message="Cannot write file"
        )
        
        summary = Summary(
            total_scanned=10,
            missing_index=5,
            generated=3,
            skipped=1,
            failed=1,
            duration=2.0,
            errors=[error]
        )
        
        assert len(summary.errors) == 1
        assert summary.errors[0].error_type == "IOError"
