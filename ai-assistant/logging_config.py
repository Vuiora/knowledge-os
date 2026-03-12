#!/usr/bin/env python3
"""
统一日志配置模块
为所有服务提供标准化的日志配置

Requirements: 13.1
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional


# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def setup_logging(
    service_name: str,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    json_format: bool = False
) -> logging.Logger:
    """
    配置统一的日志系统
    
    Args:
        service_name: 服务名称（用于日志标识）
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: 日志文件路径（可选，如果不提供则只输出到控制台）
        max_bytes: 日志文件最大大小（字节）
        backup_count: 保留的日志文件备份数量
        json_format: 是否使用 JSON 格式输出（便于日志聚合）
        
    Returns:
        配置好的 logger 实例
    """
    # 从环境变量获取日志级别（如果未指定）
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # 验证日志级别
    if log_level not in LOG_LEVELS:
        log_level = 'INFO'
    
    # 获取根 logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVELS[log_level])
    
    # 清除现有的 handlers
    logger.handlers.clear()
    
    # 创建格式化器
    if json_format:
        # JSON 格式（便于 ELK、Splunk 等日志系统解析）
        formatter = JsonFormatter(service_name)
    else:
        # 标准格式
        log_format = (
            '%(asctime)s - '
            f'{service_name} - '
            '%(name)s - '
            '%(levelname)s - '
            '%(message)s'
        )
        formatter = logging.Formatter(
            log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # 添加控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVELS[log_level])
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件 handler（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 使用 RotatingFileHandler 实现日志轮转
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(LOG_LEVELS[log_level])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 记录日志配置信息
    logger.info(f"日志系统已初始化 - 服务: {service_name}, 级别: {log_level}")
    if log_file:
        logger.info(f"日志文件: {log_file}")
    
    return logger


class JsonFormatter(logging.Formatter):
    """
    JSON 格式的日志格式化器
    输出结构化的 JSON 日志，便于日志聚合和分析
    """
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON
        
        Args:
            record: 日志记录
            
        Returns:
            JSON 格式的日志字符串
        """
        import json
        from datetime import datetime
        
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'service': self.service_name,
            'logger': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加异常信息（如果有）
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # 添加额外的字段（如果有）
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的 logger
    
    Args:
        name: logger 名称（通常使用 __name__）
        
    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger):
    """
    装饰器：记录函数调用
    
    Args:
        logger: Logger 实例
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"调用函数: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"函数 {func.__name__} 执行成功")
                return result
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行失败: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


def log_exception(logger: logging.Logger, message: str = "发生异常"):
    """
    装饰器：捕获并记录异常
    
    Args:
        logger: Logger 实例
        message: 异常消息前缀
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{message} - {func.__name__}: {e}", exc_info=True)
                raise
        return wrapper
    return decorator
