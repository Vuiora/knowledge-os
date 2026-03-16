"""
日志系统基础框架
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager


class ContextFilter(logging.Filter):
    """上下文过滤器，用于添加上下文信息到日志记录"""
    
    def __init__(self):
        super().__init__()
        self.context: Dict[str, Any] = {}
    
    def filter(self, record):
        """添加上下文信息到日志记录"""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True
    
    def set_context(self, **kwargs):
        """设置上下文信息"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """清除上下文信息"""
        self.context.clear()
    
    def remove_context(self, *keys):
        """移除特定的上下文键"""
        for key in keys:
            self.context.pop(key, None)


class Logger:
    """日志管理器"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    _context_filter: Optional[ContextFilter] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志系统"""
        if self._logger is None:
            self._logger = logging.getLogger('mkdocs_index_generator')
            self._logger.setLevel(logging.DEBUG)
            
            # 创建上下文过滤器
            self._context_filter = ContextFilter()
            self._logger.addFilter(self._context_filter)
            
            # 默认控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)
    
    def configure(self, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        配置日志系统
        
        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            log_file: 日志文件路径（可选）
        """
        # 设置日志级别
        level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger.setLevel(level)
        
        # 更新控制台处理器级别
        for handler in self._logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(level)
        
        # 添加文件处理器
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            # 文件日志包含更详细的信息，包括上下文
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
    
    def set_context(self, **kwargs):
        """
        设置日志上下文信息
        
        Args:
            **kwargs: 上下文键值对，例如 operation="scan", path="/some/path"
        
        Example:
            logger.set_context(operation="scan", directory="/path/to/dir")
            logger.info("开始扫描")  # 日志将包含上下文信息
        """
        if self._context_filter:
            self._context_filter.set_context(**kwargs)
    
    def clear_context(self):
        """清除所有上下文信息"""
        if self._context_filter:
            self._context_filter.clear_context()
    
    def remove_context(self, *keys):
        """
        移除特定的上下文键
        
        Args:
            *keys: 要移除的上下文键
        """
        if self._context_filter:
            self._context_filter.remove_context(*keys)
    
    @contextmanager
    def context(self, **kwargs):
        """
        上下文管理器，用于临时设置上下文信息
        
        Args:
            **kwargs: 上下文键值对
        
        Example:
            with logger.context(operation="generate", path="/some/path"):
                logger.info("生成文件")  # 日志将包含上下文信息
            # 退出 with 块后，上下文自动清除
        """
        self.set_context(**kwargs)
        try:
            yield
        finally:
            self.remove_context(*kwargs.keys())
    
    def debug(self, message: str, **context):
        """
        记录调试信息
        
        Args:
            message: 日志消息
            **context: 临时上下文信息（仅用于此条日志）
        """
        if context:
            with self.context(**context):
                self._logger.debug(message)
        else:
            self._logger.debug(message)
    
    def info(self, message: str, **context):
        """
        记录一般信息
        
        Args:
            message: 日志消息
            **context: 临时上下文信息（仅用于此条日志）
        """
        if context:
            with self.context(**context):
                self._logger.info(message)
        else:
            self._logger.info(message)
    
    def warning(self, message: str, **context):
        """
        记录警告信息
        
        Args:
            message: 日志消息
            **context: 临时上下文信息（仅用于此条日志）
        """
        if context:
            with self.context(**context):
                self._logger.warning(message)
        else:
            self._logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None, **context):
        """
        记录错误信息
        
        Args:
            message: 日志消息
            exception: 异常对象（可选）
            **context: 临时上下文信息（仅用于此条日志）
        """
        if context:
            with self.context(**context):
                if exception:
                    self._logger.error(f"{message}: {str(exception)}", exc_info=True)
                else:
                    self._logger.error(message)
        else:
            if exception:
                self._logger.error(f"{message}: {str(exception)}", exc_info=True)
            else:
                self._logger.error(message)
    
    def get_logger(self) -> logging.Logger:
        """获取底层 logger 对象"""
        return self._logger


# 全局日志实例
logger = Logger()
