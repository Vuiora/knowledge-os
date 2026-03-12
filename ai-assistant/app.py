#!/usr/bin/env python3
"""
AI 知识助手服务
提供嵌入生成、向量存储和知识检索功能

Requirements: 6.2, 6.3, 6.4, 6.5, 8.4
"""

import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from document_processor import create_document_processor, DocumentProcessor
from embedding_generator import create_embedding_generator, EmbeddingGenerator
from gitea_client import create_gitea_client, GiteaClient
from qdrant_client_wrapper import create_qdrant_client, QdrantClientWrapper
from rag_engine import create_rag_engine, RAGQueryEngine
from monitoring import ServiceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Knowledge Assistant",
    description="Embedding generation and knowledge retrieval service",
    version="1.0.0"
)

# Global instances (will be initialized on startup)
document_processor: Optional[DocumentProcessor] = None
embedding_generator: Optional[EmbeddingGenerator] = None
gitea_client: Optional[GiteaClient] = None
qdrant_client: Optional[QdrantClientWrapper] = None
rag_engine: Optional[RAGQueryEngine] = None
monitor: Optional[ServiceMonitor] = None


# Request/Response models
class UpdateEmbeddingsRequest(BaseModel):
    """嵌入更新请求"""
    files: List[str]


class UpdateEmbeddingsResponse(BaseModel):
    """嵌入更新响应"""
    status: str
    message: str
    files_processed: int
    chunks_created: int
    embeddings_stored: int


class QueryRequest(BaseModel):
    """查询请求"""
    question: str
    limit: int = 5
    score_threshold: float = 0.7


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str
    sources: List[Dict[str, Any]]


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化所有组件"""
    global document_processor, embedding_generator, gitea_client, qdrant_client, rag_engine, monitor
    
    logger.info("Initializing AI Knowledge Assistant...")
    
    try:
        # 初始化监控器
        monitor = ServiceMonitor("ai-assistant")
        logger.info("Service monitor initialized")
        
        # 初始化文档处理器
        document_processor = create_document_processor(
            chunk_size=512,
            chunk_overlap=50
        )
        logger.info("Document processor initialized")
        
        # 初始化嵌入生成器
        embedding_generator = create_embedding_generator(
            batch_size=32,
            enable_cache=True
        )
        logger.info("Embedding generator initialized")
        
        # 初始化 Gitea 客户端
        gitea_client = create_gitea_client()
        logger.info("Gitea client initialized")
        
        # 初始化 Qdrant 客户端
        qdrant_client = create_qdrant_client(
            collection_name="knowledge_embeddings",
            vector_size=embedding_generator.embedding_dim
        )
        logger.info("Qdrant client initialized")
        
        # 初始化 RAG 查询引擎
        rag_engine = create_rag_engine(
            embedding_generator=embedding_generator,
            qdrant_client=qdrant_client
        )
        logger.info("RAG query engine initialized")
        
        logger.info("AI Knowledge Assistant started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI Knowledge Assistant: {e}")
        raise


@app.get('/')
async def root():
    """根端点"""
    return {
        'service': 'AI Knowledge Assistant',
        'status': 'running',
        'version': '1.0.0'
    }


@app.get('/health')
async def health():
    """
    健康检查端点
    
    Requirements: 13.3
    """
    if not monitor:
        return JSONResponse(
            status_code=503,
            content={'status': 'initializing', 'message': 'Service is starting up'}
        )
    
    # 记录请求
    monitor.record_request()
    
    components = {}
    
    # 检查各组件状态
    if document_processor:
        components['document_processor'] = {'status': 'ok'}
    else:
        components['document_processor'] = {'status': 'error', 'message': 'Not initialized'}
    
    if embedding_generator:
        components['embedding_generator'] = {
            'status': 'ok',
            'model': embedding_generator.model_name,
            'dimension': embedding_generator.embedding_dim
        }
    else:
        components['embedding_generator'] = {'status': 'error', 'message': 'Not initialized'}
    
    if gitea_client:
        try:
            gitea_health = await gitea_client.health_check()
            components['gitea'] = gitea_health
        except Exception as e:
            components['gitea'] = {'status': 'error', 'message': str(e)}
    else:
        components['gitea'] = {'status': 'error', 'message': 'Not initialized'}
    
    if qdrant_client:
        try:
            qdrant_healthy = qdrant_client.health_check()
            components['qdrant'] = {
                'status': 'ok' if qdrant_healthy else 'error'
            }
        except Exception as e:
            components['qdrant'] = {'status': 'error', 'message': str(e)}
    else:
        components['qdrant'] = {'status': 'error', 'message': 'Not initialized'}
    
    if rag_engine:
        try:
            engine_info = rag_engine.get_engine_info()
            components['rag_engine'] = {
                'status': 'ok',
                'model': engine_info['model'],
                'openai_configured': engine_info['openai_configured']
            }
        except Exception as e:
            components['rag_engine'] = {'status': 'error', 'message': str(e)}
    else:
        components['rag_engine'] = {'status': 'error', 'message': 'Not initialized'}
    
    # 获取健康状态
    health_status = monitor.get_health_status(components)
    
    return health_status.to_dict()


@app.post('/api/update-embeddings')
async def update_embeddings(
    request: UpdateEmbeddingsRequest,
    background_tasks: BackgroundTasks
):
    """
    更新指定文件的嵌入向量
    
    Requirements: 6.2, 8.4
    """
    if not gitea_client or not document_processor or not embedding_generator or not qdrant_client or not monitor:
        raise HTTPException(
            status_code=503,
            detail="Service not fully initialized"
        )
    
    # 记录请求
    monitor.record_request()
    
    logger.info(f"Received embedding update request for {len(request.files)} files")
    
    # 过滤出知识目录中的 Markdown 文件
    knowledge_files = gitea_client.filter_knowledge_files(request.files)
    
    if not knowledge_files:
        monitor.record_sync(True, "No knowledge files to process", 0)
        return UpdateEmbeddingsResponse(
            status="skipped",
            message="No knowledge Markdown files to process",
            files_processed=0,
            chunks_created=0,
            embeddings_stored=0
        )
    
    logger.info(f"Processing {len(knowledge_files)} knowledge files")
    
    try:
        # 处理每个文件
        all_chunks = []
        files_processed = 0
        
        for file_path in knowledge_files:
            # 从 Gitea 获取文件内容
            content = await gitea_client.get_file_content(file_path)
            
            if content is None:
                logger.warning(f"Could not fetch content for {file_path}")
                continue
            
            # 提取元数据
            metadata = document_processor.extract_metadata(file_path, content)
            
            # 分块
            chunks = document_processor.split_into_chunks(
                content,
                file_path,
                metadata
            )
            
            # 转换为字典格式
            chunk_dicts = [chunk.to_dict() for chunk in chunks]
            all_chunks.extend(chunk_dicts)
            files_processed += 1
        
        if not all_chunks:
            monitor.record_sync(True, "No chunks created", files_processed)
            return UpdateEmbeddingsResponse(
                status="completed",
                message="No chunks created from files",
                files_processed=files_processed,
                chunks_created=0,
                embeddings_stored=0
            )
        
        # 生成嵌入向量
        chunks_with_embeddings = embedding_generator.generate_embeddings_for_chunks(
            all_chunks,
            show_progress=False
        )
        
        # 存储到 Qdrant
        vectors = [chunk['embedding'] for chunk in chunks_with_embeddings]
        ids = [
            f"{chunk['file_path']}_{chunk['chunk_index']}"
            for chunk in chunks_with_embeddings
        ]
        metadata_list = [chunk['metadata'] for chunk in chunks_with_embeddings]
        
        # 添加内容到元数据
        for i, chunk in enumerate(chunks_with_embeddings):
            metadata_list[i]['content'] = chunk['content']
            metadata_list[i]['chunk_index'] = chunk['chunk_index']
            metadata_list[i]['file_path'] = chunk['file_path']
        
        success = qdrant_client.upsert_vectors(vectors, ids, metadata_list)
        
        if not success:
            monitor.record_sync(False, "Failed to store embeddings", files_processed)
            monitor.record_error()
            raise HTTPException(
                status_code=500,
                detail="Failed to store embeddings in vector database"
            )
        
        # 记录成功的同步
        monitor.record_sync(
            True,
            f"Successfully processed {files_processed} files",
            files_processed
        )
        
        logger.info(
            f"Successfully processed {files_processed} files, "
            f"created {len(all_chunks)} chunks, "
            f"stored {len(vectors)} embeddings"
        )
        
        return UpdateEmbeddingsResponse(
            status="completed",
            message="Embeddings updated successfully",
            files_processed=files_processed,
            chunks_created=len(all_chunks),
            embeddings_stored=len(vectors)
        )
        
    except Exception as e:
        monitor.record_sync(False, f"Error: {str(e)}", 0)
        monitor.record_error()
        logger.error(f"Error updating embeddings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update embeddings: {str(e)}"
        )


@app.post('/api/query')
async def query(request: QueryRequest):
    """
    查询知识库 - 完整的 RAG 实现
    
    Requirements: 6.4, 6.5
    """
    if not rag_engine or not monitor:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    # 记录请求
    monitor.record_request()
    
    logger.info(f"Received query: {request.question}")
    
    try:
        # 使用 RAG 引擎处理查询
        result = rag_engine.query(
            question=request.question,
            limit=request.limit,
            score_threshold=request.score_threshold,
            include_sources=True
        )
        
        # 检查是否有错误
        if 'error' in result:
            monitor.record_error()
            raise HTTPException(
                status_code=500,
                detail=result['error']
            )
        
        return QueryResponse(
            answer=result['answer'],
            sources=result['sources']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


@app.get('/api/embeddings/status')
async def embeddings_status():
    """
    获取嵌入向量状态
    """
    if not qdrant_client or not embedding_generator:
        raise HTTPException(
            status_code=503,
            detail="Service not fully initialized"
        )
    
    try:
        # 获取 Qdrant 集合信息
        collection_info = qdrant_client.get_collection_info()
        
        # 获取缓存统计
        cache_stats = embedding_generator.get_cache_stats()
        
        # 获取模型信息
        model_info = embedding_generator.get_model_info()
        
        return {
            'status': 'ok',
            'collection': collection_info,
            'cache': cache_stats,
            'model': model_info
        }
        
    except Exception as e:
        logger.error(f"Error getting embeddings status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )


@app.get('/api/rag/info')
async def rag_info():
    """
    获取 RAG 引擎信息
    
    Requirements: 6.4
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    try:
        engine_info = rag_engine.get_engine_info()
        return {
            'status': 'ok',
            'engine': engine_info
        }
    except Exception as e:
        logger.error(f"Error getting RAG info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get RAG info: {str(e)}"
        )


@app.get('/api/sync/status')
async def sync_status():
    """
    获取同步状态 API
    
    Requirements: 13.3
    """
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    try:
        sync_status = monitor.get_sync_status()
        return sync_status.to_dict()
    except Exception as e:
        logger.error(f"Error getting sync status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )


@app.get('/api/metrics')
async def system_metrics():
    """
    获取系统指标 API
    
    Requirements: 13.3
    """
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    try:
        metrics = monitor.get_system_metrics()
        service_stats = monitor.get_service_stats()
        
        return {
            'system': metrics.to_dict(),
            'service': service_stats
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@app.get('/api/sync/history')
async def sync_history(limit: int = 10):
    """
    获取最近的同步历史
    
    Requirements: 13.3
    """
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    try:
        history = monitor.get_recent_sync_history(limit=limit)
        return {
            'status': 'ok',
            'history': history,
            'count': len(history)
        }
    except Exception as e:
        logger.error(f"Error getting sync history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync history: {str(e)}"
        )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
