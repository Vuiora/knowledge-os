#!/usr/bin/env python3
"""
监控模块
提供健康检查、同步状态和系统指标 API

Requirements: 13.3
"""

import os
import time
import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """健康状态数据类"""
    status: str  # healthy, degraded, unhealthy
    timestamp: str
    uptime_seconds: float
    components: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    process_count: int
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class SyncStatus:
    """同步状态数据类"""
    last_sync_time: Optional[str]
    sync_count: int
    last_sync_success: bool
    last_sync_message: str
    files_synced: int
    errors_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class ServiceMonitor:
    """服务监控器"""
    
    def __init__(self, service_name: str):
        """
        初始化服务监控器
        
        Args:
            service_name: 服务名称
        """
        self.service_name = service_name
        self.start_time = time.time()
        self.sync_history = []
        self.error_count = 0
        self.request_count = 0
        self.last_sync_time = None
        self.last_sync_success = False
        self.last_sync_message = ""
        self.files_synced_total = 0
    
    def get_uptime(self) -> float:
        """
        获取服务运行时间（秒）
        
        Returns:
            运行时间（秒）
        """
        return time.time() - self.start_time
    
    def record_sync(self, success: bool, message: str, files_count: int = 0):
        """
        记录同步操作
        
        Args:
            success: 是否成功
            message: 同步消息
            files_count: 同步的文件数量
        """
        self.last_sync_time = datetime.now().isoformat()
        self.last_sync_success = success
        self.last_sync_message = message
        
        if success:
            self.files_synced_total += files_count
        else:
            self.error_count += 1
        
        # 记录到历史（保留最近 100 条）
        self.sync_history.append({
            'timestamp': self.last_sync_time,
            'success': success,
            'message': message,
            'files_count': files_count
        })
        
        if len(self.sync_history) > 100:
            self.sync_history.pop(0)
        
        logger.info(f"同步记录: success={success}, files={files_count}, message={message}")
    
    def record_request(self):
        """记录请求"""
        self.request_count += 1
    
    def record_error(self):
        """记录错误"""
        self.error_count += 1
    
    def get_sync_status(self) -> SyncStatus:
        """
        获取同步状态
        
        Returns:
            SyncStatus 对象
        """
        return SyncStatus(
            last_sync_time=self.last_sync_time,
            sync_count=len(self.sync_history),
            last_sync_success=self.last_sync_success,
            last_sync_message=self.last_sync_message,
            files_synced=self.files_synced_total,
            errors_count=self.error_count
        )
    
    def get_health_status(
        self,
        components: Optional[Dict[str, Any]] = None
    ) -> HealthStatus:
        """
        获取健康状态
        
        Args:
            components: 组件状态字典
            
        Returns:
            HealthStatus 对象
        """
        # 确定整体健康状态
        if components:
            # 检查是否有组件不健康
            unhealthy_components = [
                name for name, status in components.items()
                if isinstance(status, dict) and status.get('status') == 'error'
            ]
            
            if unhealthy_components:
                overall_status = 'unhealthy'
            elif self.error_count > 10:  # 错误数量过多
                overall_status = 'degraded'
            else:
                overall_status = 'healthy'
        else:
            overall_status = 'healthy'
        
        return HealthStatus(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            uptime_seconds=self.get_uptime(),
            components=components or {}
        )
    
    def get_system_metrics(self) -> SystemMetrics:
        """
        获取系统指标
        
        Returns:
            SystemMetrics 对象
        """
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)
        
        # 进程数量
        process_count = len(psutil.pids())
        
        return SystemMetrics(
            cpu_percent=round(cpu_percent, 2),
            memory_percent=round(memory_percent, 2),
            memory_used_mb=round(memory_used_mb, 2),
            memory_total_mb=round(memory_total_mb, 2),
            disk_percent=round(disk_percent, 2),
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            process_count=process_count,
            timestamp=datetime.now().isoformat()
        )
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息
        
        Returns:
            服务统计字典
        """
        return {
            'service_name': self.service_name,
            'uptime_seconds': round(self.get_uptime(), 2),
            'uptime_formatted': self._format_uptime(self.get_uptime()),
            'request_count': self.request_count,
            'error_count': self.error_count,
            'error_rate': round(
                self.error_count / max(self.request_count, 1) * 100, 2
            ),
            'sync_count': len(self.sync_history),
            'files_synced_total': self.files_synced_total,
            'last_sync_time': self.last_sync_time,
            'last_sync_success': self.last_sync_success
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """
        格式化运行时间
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if secs > 0 or not parts:
            parts.append(f"{secs}秒")
        
        return " ".join(parts)
    
    def get_recent_sync_history(self, limit: int = 10) -> list:
        """
        获取最近的同步历史
        
        Args:
            limit: 返回的记录数量
            
        Returns:
            同步历史列表
        """
        return self.sync_history[-limit:]


def check_component_health(
    component_name: str,
    check_func: callable,
    timeout: float = 5.0
) -> Dict[str, Any]:
    """
    检查组件健康状态
    
    Args:
        component_name: 组件名称
        check_func: 健康检查函数
        timeout: 超时时间（秒）
        
    Returns:
        组件健康状态字典
    """
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("健康检查超时")
    
    try:
        # 设置超时
        if hasattr(signal, 'SIGALRM'):  # Unix 系统
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))
        
        # 执行健康检查
        result = check_func()
        
        # 取消超时
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        
        return {
            'component': component_name,
            'status': 'ok',
            'details': result
        }
        
    except TimeoutError:
        logger.error(f"组件 {component_name} 健康检查超时")
        return {
            'component': component_name,
            'status': 'error',
            'message': '健康检查超时'
        }
    except Exception as e:
        logger.error(f"组件 {component_name} 健康检查失败: {e}")
        return {
            'component': component_name,
            'status': 'error',
            'message': str(e)
        }


async def async_check_component_health(
    component_name: str,
    check_func: callable,
    timeout: float = 5.0
) -> Dict[str, Any]:
    """
    异步检查组件健康状态
    
    Args:
        component_name: 组件名称
        check_func: 异步健康检查函数
        timeout: 超时时间（秒）
        
    Returns:
        组件健康状态字典
    """
    import asyncio
    
    try:
        # 使用 asyncio.wait_for 设置超时
        result = await asyncio.wait_for(check_func(), timeout=timeout)
        
        return {
            'component': component_name,
            'status': 'ok',
            'details': result
        }
        
    except asyncio.TimeoutError:
        logger.error(f"组件 {component_name} 健康检查超时")
        return {
            'component': component_name,
            'status': 'error',
            'message': '健康检查超时'
        }
    except Exception as e:
        logger.error(f"组件 {component_name} 健康检查失败: {e}")
        return {
            'component': component_name,
            'status': 'error',
            'message': str(e)
        }


def create_health_check_response(
    service_name: str,
    components: Dict[str, Any],
    uptime_seconds: float
) -> Dict[str, Any]:
    """
    创建标准的健康检查响应
    
    Args:
        service_name: 服务名称
        components: 组件状态字典
        uptime_seconds: 运行时间（秒）
        
    Returns:
        健康检查响应字典
    """
    # 确定整体状态
    unhealthy = any(
        c.get('status') == 'error' for c in components.values()
        if isinstance(c, dict)
    )
    
    return {
        'service': service_name,
        'status': 'unhealthy' if unhealthy else 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': round(uptime_seconds, 2),
        'components': components
    }
