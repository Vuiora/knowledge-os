#!/usr/bin/env python3
"""
MkDocs 构建服务
负责从 Gitea 克隆仓库、构建 MkDocs 站点并提供静态文件服务
"""

import os
import logging
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx

from gitea_client import GiteaClient
from builder import MkDocsBuilder
from monitoring import ServiceMonitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 环境变量配置
GITEA_URL = os.getenv('GITEA_URL', 'http://gitea:3000')
GITEA_TOKEN = os.getenv('GITEA_TOKEN', '')
REPO_PATH = os.getenv('REPO_PATH', 'admin/knowledge-system')
BUILD_ON_STARTUP = os.getenv('BUILD_ON_STARTUP', 'true').lower() == 'true'
NOTIFICATION_URL = os.getenv('NOTIFICATION_URL', '')  # 可选的构建通知 URL

# 目录配置
REPO_DIR = '/app/repo'
SITE_DIR = '/app/site'
CONFIG_TEMPLATE = '/app/mkdocs.yml.template'

# 全局变量
gitea_client: Optional[GiteaClient] = None
builder: Optional[MkDocsBuilder] = None
monitor: Optional[ServiceMonitor] = None
is_building = False


async def send_build_notification(build_result: dict):
    """
    发送构建状态通知
    
    Args:
        build_result: 构建结果字典
    """
    if not NOTIFICATION_URL:
        return
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            notification_data = {
                'service': 'mkdocs-builder',
                'event': 'build_completed',
                'success': build_result['success'],
                'message': build_result['message'],
                'duration': build_result.get('duration'),
                'commit_sha': build_result.get('commit_sha'),
                'build_time': build_result.get('build_time')
            }
            
            logger.info(f"发送构建通知到: {NOTIFICATION_URL}")
            response = await client.post(NOTIFICATION_URL, json=notification_data)
            
            if response.status_code == 200:
                logger.info("构建通知发送成功")
            else:
                logger.warning(f"构建通知发送失败: {response.status_code}")
                
    except Exception as e:
        logger.error(f"发送构建通知异常: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global gitea_client, builder, monitor
    
    # 启动时初始化
    logger.info("初始化 MkDocs 构建服务...")
    
    # 初始化监控器
    monitor = ServiceMonitor("mkdocs-builder")
    logger.info("服务监控器已初始化")
    
    # 初始化 Gitea 客户端
    gitea_client = GiteaClient(GITEA_URL, GITEA_TOKEN, REPO_PATH)
    
    # 初始化构建器
    builder = MkDocsBuilder(REPO_DIR, SITE_DIR, CONFIG_TEMPLATE)
    
    # 如果配置了启动时构建，则执行初始构建
    if BUILD_ON_STARTUP:
        logger.info("执行启动时构建...")
        try:
            # 克隆或拉取仓库
            if gitea_client.clone_or_pull(REPO_DIR):
                # 执行构建
                result = builder.build()
                if result['success']:
                    logger.info("启动时构建成功")
                else:
                    logger.error(f"启动时构建失败: {result['message']}")
            else:
                logger.error("克隆仓库失败")
        except Exception as e:
            logger.error(f"启动时构建异常: {e}")
    
    yield
    
    # 关闭时清理
    logger.info("关闭 MkDocs 构建服务...")


app = FastAPI(
    title="MkDocs 构建服务",
    description="从 Gitea 仓库构建 MkDocs 文档站点",
    version="1.0.0",
    lifespan=lifespan
)


class BuildRequest(BaseModel):
    """构建请求模型"""
    force: bool = False  # 是否强制重新构建


class BuildResponse(BaseModel):
    """构建响应模型"""
    success: bool
    message: str
    duration: Optional[float] = None
    commit_sha: Optional[str] = None
    build_time: Optional[str] = None


@app.get('/health')
def health():
    """
    健康检查端点
    
    Requirements: 13.3
    """
    if not monitor:
        return {
            'status': 'initializing',
            'message': 'Service is starting up'
        }
    
    # 记录请求
    monitor.record_request()
    
    components = {}
    
    # 检查构建器状态
    if builder:
        components['builder'] = {
            'status': 'ok',
            'is_building': is_building
        }
    else:
        components['builder'] = {
            'status': 'error',
            'message': 'Not initialized'
        }
    
    # 检查 Gitea 客户端
    if gitea_client:
        components['gitea'] = {
            'status': 'ok',
            'url': GITEA_URL,
            'repo': REPO_PATH
        }
    else:
        components['gitea'] = {
            'status': 'error',
            'message': 'Not initialized'
        }
    
    # 检查站点目录
    site_exists = Path(SITE_DIR).exists() and any(Path(SITE_DIR).iterdir())
    components['site'] = {
        'status': 'ok' if site_exists else 'warning',
        'exists': site_exists,
        'path': SITE_DIR
    }
    
    # 获取健康状态
    health_status = monitor.get_health_status(components)
    
    return health_status.to_dict()


@app.get('/status')
def get_status():
    """获取构建状态"""
    if builder is None or monitor is None:
        raise HTTPException(status_code=503, detail="构建器未初始化")
    
    # 记录请求
    monitor.record_request()
    
    status = builder.get_build_status()
    status['is_building'] = is_building
    status['repo_dir'] = REPO_DIR
    status['site_dir'] = SITE_DIR
    
    return status


@app.get('/api/sync/status')
def sync_status():
    """
    获取同步状态 API
    
    Requirements: 13.3
    """
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    # 记录请求
    monitor.record_request()
    
    try:
        sync_status = monitor.get_sync_status()
        return sync_status.to_dict()
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error getting sync status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )


@app.get('/api/metrics')
def system_metrics():
    """
    获取系统指标 API
    
    Requirements: 13.3
    """
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    # 记录请求
    monitor.record_request()
    
    try:
        metrics = monitor.get_system_metrics()
        service_stats = monitor.get_service_stats()
        
        return {
            'system': metrics.to_dict(),
            'service': service_stats
        }
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error getting system metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@app.get('/api/sync/history')
def sync_history(limit: int = 10):
    """
    获取最近的同步历史
    
    Requirements: 13.3
    """
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    # 记录请求
    monitor.record_request()
    
    try:
        history = monitor.get_recent_sync_history(limit=limit)
        return {
            'status': 'ok',
            'history': history,
            'count': len(history)
        }
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error getting sync history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync history: {str(e)}"
        )


@app.post('/build', response_model=BuildResponse)
async def trigger_build(request: BuildRequest, background_tasks: BackgroundTasks):
    """
    触发 MkDocs 构建
    
    Args:
        request: 构建请求
        background_tasks: 后台任务
        
    Returns:
        BuildResponse: 构建结果
    """
    global is_building
    
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    # 记录请求
    monitor.record_request()
    
    if is_building:
        return BuildResponse(
            success=False,
            message='构建正在进行中，请稍后再试'
        )
    
    if gitea_client is None or builder is None:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    # 标记为正在构建
    is_building = True
    
    try:
        logger.info("开始构建流程...")
        
        # 1. 克隆或拉取仓库
        logger.info("同步 Git 仓库...")
        if not gitea_client.clone_or_pull(REPO_DIR):
            is_building = False
            monitor.record_sync(False, "Git 仓库同步失败", 0)
            monitor.record_error()
            return BuildResponse(
                success=False,
                message='Git 仓库同步失败'
            )
        
        # 2. 执行构建
        logger.info("执行 MkDocs 构建...")
        result = builder.build()
        
        is_building = False
        
        # 记录构建结果
        if result['success']:
            monitor.record_sync(True, "构建成功", 1)
        else:
            monitor.record_sync(False, f"构建失败: {result['message']}", 0)
            monitor.record_error()
        
        # 3. 发送构建状态通知（如果配置了 webhook URL）
        if result['success']:
            background_tasks.add_task(send_build_notification, result)
        
        return BuildResponse(
            success=result['success'],
            message=result['message'],
            duration=result.get('duration'),
            commit_sha=result.get('commit_sha'),
            build_time=result.get('build_time')
        )
        
    except Exception as e:
        is_building = False
        monitor.record_sync(False, f"构建异常: {str(e)}", 0)
        monitor.record_error()
        logger.error(f"构建异常: {e}")
        return BuildResponse(
            success=False,
            message=f'构建异常: {str(e)}'
        )


@app.post('/rebuild')
async def rebuild(background_tasks: BackgroundTasks):
    """
    强制重新构建（清理后构建）
    """
    global is_building
    
    if is_building:
        return JSONResponse(
            status_code=409,
            content={'message': '构建正在进行中，请稍后再试'}
        )
    
    if builder is None:
        raise HTTPException(status_code=503, detail="构建器未初始化")
    
    try:
        # 清理旧的构建
        logger.info("清理旧的构建...")
        builder.clean()
        
        # 触发新构建
        return await trigger_build(BuildRequest(force=True), background_tasks)
        
    except Exception as e:
        logger.error(f"重新构建异常: {e}")
        return JSONResponse(
            status_code=500,
            content={'message': f'重新构建失败: {str(e)}'}
        )


@app.get('/sync')
async def sync_repo():
    """
    仅同步 Git 仓库（不构建）
    """
    if gitea_client is None:
        raise HTTPException(status_code=503, detail="Gitea 客户端未初始化")
    
    try:
        logger.info("同步 Git 仓库...")
        success = gitea_client.clone_or_pull(REPO_DIR)
        
        if success:
            commit_sha = gitea_client.get_latest_commit(REPO_DIR)
            return {
                'success': True,
                'message': '仓库同步成功',
                'commit_sha': commit_sha
            }
        else:
            return JSONResponse(
                status_code=500,
                content={'success': False, 'message': '仓库同步失败'}
            )
            
    except Exception as e:
        logger.error(f"同步仓库异常: {e}")
        return JSONResponse(
            status_code=500,
            content={'success': False, 'message': f'同步异常: {str(e)}'}
        )


# 挂载静态文件服务
site_path = Path(SITE_DIR)
if site_path.exists():
    app.mount("/docs", StaticFiles(directory=SITE_DIR, html=True), name="docs")
    logger.info(f"静态文件服务已挂载: /docs -> {SITE_DIR}")


@app.get('/')
def root():
    """根路径重定向到文档"""
    return {
        'service': 'MkDocs 构建服务',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'status': '/status',
            'build': '/build (POST)',
            'rebuild': '/rebuild (POST)',
            'sync': '/sync (GET)',
            'webhook': '/webhook (POST)',
            'docs': '/docs/'
        }
    }


@app.post('/webhook')
async def webhook_handler(request: dict, background_tasks: BackgroundTasks):
    """
    Webhook 端点，接收来自 Gitea 或其他服务的构建触发请求
    
    Args:
        request: Webhook 请求数据
        background_tasks: 后台任务
        
    Returns:
        构建触发结果
    """
    logger.info(f"收到 webhook 请求: {request}")
    
    # 提取事件信息
    event_type = request.get('event_type', 'unknown')
    changed_files = request.get('changed_files', [])
    
    logger.info(f"Webhook 事件类型: {event_type}, 变更文件数: {len(changed_files)}")
    
    # 检查是否有 knowledge 目录的文件变更
    knowledge_files = [f for f in changed_files if f.startswith('knowledge/')]
    
    if not knowledge_files and changed_files:
        logger.info("没有 knowledge 目录的文件变更，跳过构建")
        return {
            'status': 'skipped',
            'message': '没有需要构建的文件变更',
            'changed_files': changed_files
        }
    
    # 触发构建
    build_request = BuildRequest(force=False)
    result = await trigger_build(build_request, background_tasks)
    
    return {
        'status': 'triggered',
        'build_result': result.dict(),
        'changed_files': knowledge_files
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
