#!/usr/bin/env python3
"""
错误处理模块
提供统一的错误处理、重试机制和错误恢复策略

Requirements: 13.2
"""

import time
import logging
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps
import asyncio


logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """可重试的错误基类"""
    pass


class GitOperationError(RetryableError):
    """Git 操作错误"""
    pass


class VectorDatabaseError(RetryableError):
    """向量数据库错误"""
    pass


class APICallError(RetryableError):
    """API 调用错误"""
    pass


class EmbeddingGenerationError(Exception):
    """嵌入生成错误（通常不可重试）"""
    pass


class ConfigurationError(Exception):
    """配置错误（不可重试）"""
    pass


def retry_on_exception(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (RetryableError,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    装饰器：在发生指定异常时自动重试
    使用指数退避策略
    
    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟时间（秒）
        backoff_factor: 退避因子（每次重试延迟时间乘以此因子）
        exceptions: 需要重试的异常类型元组
        on_retry: 重试时的回调函数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"函数 {func.__name__} 执行失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}"
                        )
                        
                        # 调用重试回调
                        if on_retry:
                            on_retry(e, attempt + 1)
                        
                        # 等待后重试
                        logger.info(f"等待 {delay:.2f} 秒后重试...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败"
                        )
            
            # 所有重试都失败，抛出最后一个异常
            raise last_exception
        
        return wrapper
    return decorator


def async_retry_on_exception(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (RetryableError,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    装饰器：异步函数的重试机制
    
    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟时间（秒）
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型元组
        on_retry: 重试时的回调函数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"异步函数 {func.__name__} 执行失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}"
                        )
                        
                        # 调用重试回调
                        if on_retry:
                            on_retry(e, attempt + 1)
                        
                        # 等待后重试
                        logger.info(f"等待 {delay:.2f} 秒后重试...")
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"异步函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败"
                        )
            
            # 所有重试都失败，抛出最后一个异常
            raise last_exception
        
        return wrapper
    return decorator


def handle_git_error(func: Callable) -> Callable:
    """
    装饰器：处理 Git 操作错误
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            
            # 检测常见的 Git 错误类型
            if 'permission denied' in error_msg or 'access denied' in error_msg:
                logger.error(f"Git 权限错误: {e}")
                raise GitOperationError(f"Git 权限不足: {e}") from e
            elif 'conflict' in error_msg or 'merge' in error_msg:
                logger.error(f"Git 冲突错误: {e}")
                raise GitOperationError(f"Git 冲突，需要手动解决: {e}") from e
            elif 'not found' in error_msg or '404' in error_msg:
                logger.error(f"Git 仓库不存在: {e}")
                raise GitOperationError(f"Git 仓库未找到: {e}") from e
            elif 'timeout' in error_msg or 'timed out' in error_msg:
                logger.error(f"Git 操作超时: {e}")
                raise GitOperationError(f"Git 操作超时: {e}") from e
            else:
                logger.error(f"Git 操作失败: {e}", exc_info=True)
                raise GitOperationError(f"Git 操作失败: {e}") from e
    
    return wrapper


def handle_vector_db_error(func: Callable) -> Callable:
    """
    装饰器：处理向量数据库错误
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            
            # 检测常见的向量数据库错误
            if 'connection' in error_msg or 'connect' in error_msg:
                logger.error(f"向量数据库连接错误: {e}")
                raise VectorDatabaseError(f"无法连接到向量数据库: {e}") from e
            elif 'timeout' in error_msg or 'timed out' in error_msg:
                logger.error(f"向量数据库查询超时: {e}")
                raise VectorDatabaseError(f"向量数据库查询超时: {e}") from e
            elif 'not found' in error_msg or 'does not exist' in error_msg:
                logger.error(f"向量数据库集合不存在: {e}")
                raise VectorDatabaseError(f"向量数据库集合不存在: {e}") from e
            elif 'disk' in error_msg or 'space' in error_msg:
                logger.error(f"向量数据库存储空间不足: {e}")
                raise VectorDatabaseError(f"向量数据库存储空间不足: {e}") from e
            else:
                logger.error(f"向量数据库操作失败: {e}", exc_info=True)
                raise VectorDatabaseError(f"向量数据库操作失败: {e}") from e
    
    return wrapper


def handle_api_error(func: Callable) -> Callable:
    """
    装饰器：处理 API 调用错误
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            
            # 检测常见的 API 错误
            if 'timeout' in error_msg or 'timed out' in error_msg:
                logger.error(f"API 调用超时: {e}")
                raise APICallError(f"API 调用超时: {e}") from e
            elif '401' in error_msg or 'unauthorized' in error_msg:
                logger.error(f"API 认证失败: {e}")
                raise APICallError(f"API 认证失败，请检查 API 密钥: {e}") from e
            elif '403' in error_msg or 'forbidden' in error_msg:
                logger.error(f"API 权限不足: {e}")
                raise APICallError(f"API 权限不足: {e}") from e
            elif '404' in error_msg or 'not found' in error_msg:
                logger.error(f"API 资源不存在: {e}")
                raise APICallError(f"API 资源不存在: {e}") from e
            elif '429' in error_msg or 'rate limit' in error_msg:
                logger.error(f"API 速率限制: {e}")
                raise APICallError(f"API 速率限制，请稍后重试: {e}") from e
            elif '500' in error_msg or '502' in error_msg or '503' in error_msg:
                logger.error(f"API 服务器错误: {e}")
                raise APICallError(f"API 服务器错误: {e}") from e
            else:
                logger.error(f"API 调用失败: {e}", exc_info=True)
                raise APICallError(f"API 调用失败: {e}") from e
    
    return wrapper


def safe_execute(
    func: Callable,
    *args,
    default_value: Any = None,
    log_error: bool = True,
    **kwargs
) -> Any:
    """
    安全执行函数，捕获所有异常并返回默认值
    
    Args:
        func: 要执行的函数
        *args: 函数参数
        default_value: 发生异常时返回的默认值
        log_error: 是否记录错误日志
        **kwargs: 函数关键字参数
        
    Returns:
        函数执行结果或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"函数 {func.__name__} 执行失败: {e}", exc_info=True)
        return default_value


async def async_safe_execute(
    func: Callable,
    *args,
    default_value: Any = None,
    log_error: bool = True,
    **kwargs
) -> Any:
    """
    安全执行异步函数，捕获所有异常并返回默认值
    
    Args:
        func: 要执行的异步函数
        *args: 函数参数
        default_value: 发生异常时返回的默认值
        log_error: 是否记录错误日志
        **kwargs: 函数关键字参数
        
    Returns:
        函数执行结果或默认值
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"异步函数 {func.__name__} 执行失败: {e}", exc_info=True)
        return default_value


class CircuitBreaker:
    """
    断路器模式实现
    防止对失败的服务进行重复调用
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        初始化断路器
        
        Args:
            failure_threshold: 失败阈值（连续失败多少次后打开断路器）
            recovery_timeout: 恢复超时时间（秒）
            expected_exception: 预期的异常类型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过断路器调用函数
        
        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 如果断路器打开或函数执行失败
        """
        if self.state == 'open':
            # 检查是否可以尝试恢复
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info("断路器进入半开状态，尝试恢复")
                self.state = 'half_open'
            else:
                raise Exception("断路器已打开，服务暂时不可用")
        
        try:
            result = func(*args, **kwargs)
            
            # 成功执行，重置失败计数
            if self.state == 'half_open':
                logger.info("断路器恢复，关闭断路器")
                self.state = 'closed'
            
            self.failure_count = 0
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(
                f"断路器记录失败 ({self.failure_count}/{self.failure_threshold}): {e}"
            )
            
            # 检查是否达到失败阈值
            if self.failure_count >= self.failure_threshold:
                logger.error("断路器打开，服务暂时不可用")
                self.state = 'open'
            
            raise
