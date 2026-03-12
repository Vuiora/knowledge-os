#!/usr/bin/env python3
"""
嵌入生成器模块
使用 Sentence Transformers 生成文档嵌入向量
支持批处理和缓存机制

Requirements: 6.2
"""

import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """嵌入向量生成器"""
    
    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        cache_dir: Optional[str] = None,
        batch_size: int = 32,
        enable_cache: bool = True
    ):
        """
        初始化嵌入生成器
        
        Args:
            model_name: Sentence Transformers 模型名称
            cache_dir: 缓存目录路径
            batch_size: 批处理大小
            enable_cache: 是否启用缓存
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.enable_cache = enable_cache
        
        # 设置缓存目录
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(os.getenv("CACHE_DIR", "/app/cache"))
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载模型
        logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(
                f"Model loaded successfully. "
                f"Embedding dimension: {self.embedding_dim}"
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _compute_cache_key(self, text: str) -> str:
        """
        计算文本的缓存键
        
        Args:
            text: 输入文本
            
        Returns:
            缓存键（MD5 哈希）
        """
        # 使用 MD5 哈希作为缓存键
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{self.model_name}_{text_hash}"
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """
        从缓存加载嵌入向量
        
        Args:
            cache_key: 缓存键
            
        Returns:
            嵌入向量，如果不存在返回 None
        """
        if not self.enable_cache:
            return None
        
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    return data['embedding']
            except Exception as e:
                logger.warning(f"Failed to load cache {cache_key}: {e}")
                return None
        
        return None
    
    def _save_to_cache(self, cache_key: str, embedding: List[float]) -> bool:
        """
        保存嵌入向量到缓存
        
        Args:
            cache_key: 缓存键
            embedding: 嵌入向量
            
        Returns:
            是否成功保存
        """
        if not self.enable_cache:
            return False
        
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'model': self.model_name,
                    'embedding': embedding
                }, f)
            return True
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_key}: {e}")
            return False
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        为单个文本生成嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.embedding_dim
        
        # 检查缓存
        cache_key = self._compute_cache_key(text)
        cached_embedding = self._load_from_cache(cache_key)
        
        if cached_embedding is not None:
            logger.debug(f"Loaded embedding from cache: {cache_key}")
            return cached_embedding
        
        # 生成嵌入
        try:
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            embedding_list = embedding.tolist()
            
            # 保存到缓存
            self._save_to_cache(cache_key, embedding_list)
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # 返回零向量作为后备
            return [0.0] * self.embedding_dim
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        批量生成嵌入向量
        
        Args:
            texts: 文本列表
            show_progress: 是否显示进度条
            
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []
        
        embeddings = []
        texts_to_encode = []
        text_indices = []
        
        # 检查缓存
        for i, text in enumerate(texts):
            if not text or not text.strip():
                embeddings.append([0.0] * self.embedding_dim)
                continue
            
            cache_key = self._compute_cache_key(text)
            cached_embedding = self._load_from_cache(cache_key)
            
            if cached_embedding is not None:
                embeddings.append(cached_embedding)
            else:
                # 需要生成嵌入
                embeddings.append(None)  # 占位符
                texts_to_encode.append(text)
                text_indices.append(i)
        
        # 批量生成未缓存的嵌入
        if texts_to_encode:
            logger.info(
                f"Generating embeddings for {len(texts_to_encode)} texts "
                f"(cached: {len(texts) - len(texts_to_encode)})"
            )
            
            try:
                # 使用批处理生成嵌入
                batch_embeddings = self.model.encode(
                    texts_to_encode,
                    batch_size=self.batch_size,
                    convert_to_numpy=True,
                    show_progress_bar=show_progress
                )
                
                # 填充结果并保存到缓存
                for i, embedding in enumerate(batch_embeddings):
                    embedding_list = embedding.tolist()
                    text_idx = text_indices[i]
                    embeddings[text_idx] = embedding_list
                    
                    # 保存到缓存
                    cache_key = self._compute_cache_key(texts_to_encode[i])
                    self._save_to_cache(cache_key, embedding_list)
                
            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {e}")
                # 填充零向量
                for text_idx in text_indices:
                    if embeddings[text_idx] is None:
                        embeddings[text_idx] = [0.0] * self.embedding_dim
        
        return embeddings
    
    def generate_embeddings_for_chunks(
        self,
        chunks: List[Dict[str, Any]],
        show_progress: bool = False
    ) -> List[Dict[str, Any]]:
        """
        为文档分块生成嵌入向量
        
        Args:
            chunks: 文档分块列表（每个分块包含 'content' 字段）
            show_progress: 是否显示进度条
            
        Returns:
            包含嵌入向量的分块列表
        """
        if not chunks:
            return []
        
        # 提取文本内容
        texts = [chunk.get('content', '') for chunk in chunks]
        
        # 批量生成嵌入
        embeddings = self.generate_embeddings_batch(texts, show_progress)
        
        # 将嵌入添加到分块中
        result_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_with_embedding = chunk.copy()
            chunk_with_embedding['embedding'] = embedding
            result_chunks.append(chunk_with_embedding)
        
        logger.info(f"Generated embeddings for {len(result_chunks)} chunks")
        
        return result_chunks
    
    def clear_cache(self) -> int:
        """
        清除所有缓存文件
        
        Returns:
            删除的文件数量
        """
        if not self.enable_cache:
            return 0
        
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            
            logger.info(f"Cleared {count} cache files")
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        if not self.enable_cache:
            return {
                'enabled': False,
                'cache_dir': None,
                'file_count': 0,
                'total_size_mb': 0
            }
        
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'enabled': True,
                'cache_dir': str(self.cache_dir),
                'file_count': len(cache_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                'enabled': True,
                'cache_dir': str(self.cache_dir),
                'file_count': 0,
                'total_size_mb': 0,
                'error': str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'batch_size': self.batch_size,
            'cache_enabled': self.enable_cache,
            'cache_dir': str(self.cache_dir) if self.enable_cache else None
        }


def create_embedding_generator(
    model_name: Optional[str] = None,
    cache_dir: Optional[str] = None,
    batch_size: int = 32,
    enable_cache: bool = True
) -> EmbeddingGenerator:
    """
    创建嵌入生成器实例的便捷函数
    
    Args:
        model_name: 模型名称（默认从环境变量读取）
        cache_dir: 缓存目录
        batch_size: 批处理大小
        enable_cache: 是否启用缓存
        
    Returns:
        EmbeddingGenerator 实例
    """
    if model_name is None:
        model_name = os.getenv(
            "EMBEDDING_MODEL",
            "paraphrase-multilingual-MiniLM-L12-v2"
        )
    
    return EmbeddingGenerator(
        model_name=model_name,
        cache_dir=cache_dir,
        batch_size=batch_size,
        enable_cache=enable_cache
    )
