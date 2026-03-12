#!/usr/bin/env python3
"""
Qdrant 客户端封装库
提供向量数据库的 CRUD 操作和 Collection 管理
"""

import os
import logging
import uuid
from typing import List, Dict, Any, Optional, Union
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest
)

logger = logging.getLogger(__name__)


class QdrantClientWrapper:
    """Qdrant 向量数据库客户端封装"""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = "knowledge_embeddings"
    ):
        """
        初始化 Qdrant 客户端
        
        Args:
            host: Qdrant 服务器地址
            port: Qdrant 服务器端口
            collection_name: Collection 名称
        """
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = collection_name
        
        # 初始化客户端
        self.client = QdrantClient(host=self.host, port=self.port)
        logger.info(f"Qdrant client initialized: {self.host}:{self.port}")
    
    def initialize_collection(
        self,
        vector_size: int = 384,
        distance: Distance = Distance.COSINE
    ) -> bool:
        """
        初始化 Collection
        
        Args:
            vector_size: 向量维度（默认 384 for MiniLM）
            distance: 距离度量方式
            
        Returns:
            bool: 是否成功创建
        """
        try:
            # 检查 collection 是否已存在
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            
            # 创建新 collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            logger.info(f"Collection '{self.collection_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            return False
    
    def upsert_vectors(
        self,
        vectors: List[List[float]],
        ids: List[Union[str, int]],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """
        插入或更新向量
        
        Args:
            vectors: 向量列表
            ids: 向量 ID 列表（字符串会被转换为 UUID）
            metadata: 元数据列表
            
        Returns:
            bool: 是否成功
        """
        try:
            if len(vectors) != len(ids) or len(vectors) != len(metadata):
                raise ValueError("vectors, ids, and metadata must have the same length")
            
            # 转换 ID 为 UUID 或整数
            converted_ids = []
            for id_ in ids:
                if isinstance(id_, str):
                    # 尝试解析为 UUID，如果失败则生成新的 UUID
                    try:
                        converted_ids.append(str(uuid.UUID(id_)))
                    except ValueError:
                        # 使用字符串生成确定性 UUID
                        converted_ids.append(str(uuid.uuid5(uuid.NAMESPACE_DNS, id_)))
                else:
                    converted_ids.append(id_)
            
            points = [
                PointStruct(
                    id=id_,
                    vector=vector,
                    payload=meta
                )
                for id_, vector, meta in zip(converted_ids, vectors, metadata)
            ]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Upserted {len(points)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            return False
    
    def search_vectors(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似向量
        
        Args:
            query_vector: 查询向量
            limit: 返回结果数量
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            # 构建过滤器
            query_filter = None
            if filter_conditions:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                        for key, value in filter_conditions.items()
                    ]
                )
            
            # 执行搜索
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter
            )
            
            # 格式化结果
            formatted_results = [
                {
                    'id': result.id,
                    'score': result.score,
                    'metadata': result.payload
                }
                for result in results.points
            ]
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []
    
    def get_vector_by_id(self, vector_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取向量
        
        Args:
            vector_id: 向量 ID（字符串会被转换为 UUID）
            
        Returns:
            Dict: 向量数据，如果不存在返回 None
        """
        try:
            # 转换 ID
            if isinstance(vector_id, str):
                try:
                    converted_id = str(uuid.UUID(vector_id))
                except ValueError:
                    converted_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, vector_id))
            else:
                converted_id = vector_id
            
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[converted_id]
            )
            
            if result:
                point = result[0]
                return {
                    'id': point.id,
                    'vector': point.vector,
                    'metadata': point.payload
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get vector by id: {e}")
            return None
    
    def delete_vectors(self, vector_ids: List[Union[str, int]]) -> bool:
        """
        删除向量
        
        Args:
            vector_ids: 要删除的向量 ID 列表（字符串会被转换为 UUID）
            
        Returns:
            bool: 是否成功
        """
        try:
            # 转换 ID
            converted_ids = []
            for id_ in vector_ids:
                if isinstance(id_, str):
                    try:
                        converted_ids.append(str(uuid.UUID(id_)))
                    except ValueError:
                        converted_ids.append(str(uuid.uuid5(uuid.NAMESPACE_DNS, id_)))
                else:
                    converted_ids.append(id_)
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=converted_ids
            )
            logger.info(f"Deleted {len(converted_ids)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False
    
    def delete_by_filter(self, filter_conditions: Dict[str, Any]) -> bool:
        """
        根据过滤条件删除向量
        
        Args:
            filter_conditions: 过滤条件
            
        Returns:
            bool: 是否成功
        """
        try:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                    for key, value in filter_conditions.items()
                ]
            )
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=query_filter
            )
            logger.info(f"Deleted vectors matching filter: {filter_conditions}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete by filter: {e}")
            return False
    
    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """
        获取 Collection 信息
        
        Returns:
            Dict: Collection 信息
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.config.params.vectors.size,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# 便捷函数
def create_qdrant_client(
    host: str = None,
    port: int = None,
    collection_name: str = "knowledge_embeddings",
    vector_size: int = 384
) -> QdrantClientWrapper:
    """
    创建并初始化 Qdrant 客户端
    
    Args:
        host: Qdrant 服务器地址
        port: Qdrant 服务器端口
        collection_name: Collection 名称
        vector_size: 向量维度
        
    Returns:
        QdrantClientWrapper: 初始化的客户端
    """
    client = QdrantClientWrapper(host, port, collection_name)
    client.initialize_collection(vector_size)
    return client
