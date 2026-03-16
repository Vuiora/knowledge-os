"""
测试日志系统
"""

import pytest
import logging
from pathlib import Path
import tempfile
import os
from src.logger import Logger, logger


class TestLogger:
    """测试日志管理器"""
    
    def test_logger_singleton(self):
        """测试单例模式"""
        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2
    
    def test_logger_default_level(self):
        """测试默认日志级别"""
        test_logger = Logger()
        assert test_logger.get_logger().level == logging.DEBUG
    
    def test_configure_log_level(self):
        """测试配置日志级别"""
        test_logger = Logger()
        test_logger.configure(log_level="WARNING")
        
        # 验证日志级别已更改
        assert test_logger.get_logger().level == logging.WARNING
    
    def test_configure_with_file(self):
        """测试配置日志文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            test_logger = Logger()
            test_logger.configure(log_level="INFO", log_file=log_file)
            
            # 写入日志
            test_logger.info("Test message")
            
            # 验证文件已创建
            assert Path(log_file).exists()
            
            # 关闭文件处理器以释放文件句柄（Windows 需要）
            for handler in test_logger.get_logger().handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    test_logger.get_logger().removeHandler(handler)
    
    def test_log_methods(self):
        """测试日志方法"""
        test_logger = Logger()
        
        # 这些方法不应该抛出异常
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
    
    def test_error_with_exception(self):
        """测试带异常的错误日志"""
        test_logger = Logger()
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            # 不应该抛出异常
            test_logger.error("Error occurred", exception=e)
    
    def test_global_logger_instance(self):
        """测试全局日志实例"""
        assert logger is not None
        assert isinstance(logger, Logger)

    def test_set_context(self):
        """测试设置上下文信息"""
        test_logger = Logger()
        test_logger.set_context(operation="test", path="/test/path")
        
        # 验证上下文已设置
        assert test_logger._context_filter.context["operation"] == "test"
        assert test_logger._context_filter.context["path"] == "/test/path"
        
        # 清理
        test_logger.clear_context()
    
    def test_clear_context(self):
        """测试清除上下文信息"""
        test_logger = Logger()
        test_logger.set_context(operation="test", path="/test/path")
        test_logger.clear_context()
        
        # 验证上下文已清除
        assert len(test_logger._context_filter.context) == 0
    
    def test_remove_context(self):
        """测试移除特定上下文键"""
        test_logger = Logger()
        test_logger.set_context(operation="test", path="/test/path", level=1)
        test_logger.remove_context("path", "level")
        
        # 验证特定键已移除
        assert "operation" in test_logger._context_filter.context
        assert "path" not in test_logger._context_filter.context
        assert "level" not in test_logger._context_filter.context
        
        # 清理
        test_logger.clear_context()
    
    def test_context_manager(self):
        """测试上下文管理器"""
        test_logger = Logger()
        
        # 使用上下文管理器
        with test_logger.context(operation="test", path="/test/path"):
            # 在上下文中，应该有这些键
            assert "operation" in test_logger._context_filter.context
            assert "path" in test_logger._context_filter.context
        
        # 退出上下文后，这些键应该被移除
        assert "operation" not in test_logger._context_filter.context
        assert "path" not in test_logger._context_filter.context
    
    def test_log_with_inline_context(self):
        """测试带内联上下文的日志记录"""
        test_logger = Logger()
        
        # 这些方法不应该抛出异常
        test_logger.debug("Debug message", operation="test", path="/test")
        test_logger.info("Info message", operation="test", path="/test")
        test_logger.warning("Warning message", operation="test", path="/test")
        test_logger.error("Error message", operation="test", path="/test")
    
    def test_nested_context(self):
        """测试嵌套上下文"""
        test_logger = Logger()
        
        test_logger.set_context(operation="scan")
        
        with test_logger.context(path="/test/path"):
            # 应该同时有 operation 和 path
            assert "operation" in test_logger._context_filter.context
            assert "path" in test_logger._context_filter.context
        
        # 退出内层上下文后，operation 应该还在，path 应该被移除
        assert "operation" in test_logger._context_filter.context
        assert "path" not in test_logger._context_filter.context
        
        # 清理
        test_logger.clear_context()
