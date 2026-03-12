#!/usr/bin/env python3
"""
文档处理模块
负责 Markdown 文件读取、文档分块（Chunking）和元数据提取

Requirements: 6.2
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentChunk:
    """文档分块数据结构"""
    
    def __init__(
        self,
        content: str,
        chunk_index: int,
        file_path: str,
        metadata: Dict[str, Any]
    ):
        """
        初始化文档分块
        
        Args:
            content: 分块内容
            chunk_index: 分块索引
            file_path: 源文件路径
            metadata: 元数据
        """
        self.content = content
        self.chunk_index = chunk_index
        self.file_path = file_path
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'content': self.content,
            'chunk_index': self.chunk_index,
            'file_path': self.file_path,
            'metadata': self.metadata
        }


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 分块大小（字符数）
            chunk_overlap: 分块重叠大小（字符数）
            min_chunk_size: 最小分块大小（字符数）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        logger.info(
            f"DocumentProcessor initialized: "
            f"chunk_size={chunk_size}, overlap={chunk_overlap}"
        )
    
    def read_markdown_file(self, file_path: str) -> Optional[str]:
        """
        读取 Markdown 文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容，如果读取失败返回 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.debug(f"Read file: {file_path} ({len(content)} chars)")
            return content
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def extract_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        从文件路径和内容中提取元数据
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            元数据字典
        """
        metadata = {}
        
        # 基本文件信息
        path_obj = Path(file_path)
        metadata['file_name'] = path_obj.name
        metadata['file_path'] = file_path
        metadata['file_extension'] = path_obj.suffix
        
        # 提取知识层次（从路径中）
        metadata['layer'] = self._extract_layer_from_path(file_path)
        
        # 提取标题（从内容中）
        metadata['title'] = self._extract_title_from_content(content)
        
        # 提取标签（从内容中）
        metadata['tags'] = self._extract_tags_from_content(content)
        
        # 文件统计信息
        metadata['content_length'] = len(content)
        metadata['word_count'] = len(content.split())
        
        # 时间戳
        try:
            stat = os.stat(file_path)
            metadata['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            metadata['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception as e:
            logger.warning(f"Could not get file stats for {file_path}: {e}")
            metadata['created_at'] = None
            metadata['modified_at'] = None
        
        return metadata
    
    def _extract_layer_from_path(self, file_path: str) -> Optional[str]:
        """
        从文件路径中提取知识层次
        
        Args:
            file_path: 文件路径
            
        Returns:
            知识层次名称
        """
        # 匹配知识层次模式：01-foundations, 02-technologies, etc.
        layer_pattern = r'/(0[1-5]-[a-z\-]+)/'
        match = re.search(layer_pattern, file_path.replace('\\', '/'))
        
        if match:
            return match.group(1)
        
        # 检查是否在 _wiki 或 _site 目录
        if '/_wiki/' in file_path.replace('\\', '/'):
            return '_wiki'
        if '/_site/' in file_path.replace('\\', '/'):
            return '_site'
        
        return None
    
    def _extract_title_from_content(self, content: str) -> Optional[str]:
        """
        从 Markdown 内容中提取标题
        
        Args:
            content: Markdown 内容
            
        Returns:
            标题文本
        """
        # 查找第一个 # 标题
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        return None
    
    def _extract_tags_from_content(self, content: str) -> List[str]:
        """
        从 Markdown 内容中提取标签
        
        Args:
            content: Markdown 内容
            
        Returns:
            标签列表
        """
        tags = []
        
        # 查找 #tag 格式的标签
        tag_pattern = r'#([a-zA-Z0-9_\-]+)'
        matches = re.findall(tag_pattern, content)
        
        # 过滤掉 Markdown 标题符号
        for match in matches:
            # 排除纯数字和单字符标签
            if len(match) > 1 and not match.isdigit():
                tags.append(match)
        
        # 去重并排序
        return sorted(list(set(tags)))
    
    def split_into_chunks(
        self,
        content: str,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """
        将文档内容分块
        
        Args:
            content: 文档内容
            file_path: 文件路径
            metadata: 可选的元数据
            
        Returns:
            文档分块列表
        """
        if not content or len(content) < self.min_chunk_size:
            logger.warning(
                f"Content too short for chunking: {file_path} "
                f"({len(content)} chars)"
            )
            # 如果内容太短，返回单个分块
            if content:
                return [DocumentChunk(
                    content=content,
                    chunk_index=0,
                    file_path=file_path,
                    metadata=metadata or {}
                )]
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(content):
            # 计算结束位置
            end = start + self.chunk_size
            
            # 如果不是最后一个分块，尝试在句子边界处分割
            if end < len(content):
                # 查找最近的句子结束符
                sentence_end = self._find_sentence_boundary(
                    content,
                    end,
                    search_range=100
                )
                if sentence_end > start:
                    end = sentence_end
            
            # 提取分块内容
            chunk_content = content[start:end].strip()
            
            if len(chunk_content) >= self.min_chunk_size:
                chunk = DocumentChunk(
                    content=chunk_content,
                    chunk_index=chunk_index,
                    file_path=file_path,
                    metadata=metadata or {}
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # 移动到下一个分块，考虑重叠
            start = end - self.chunk_overlap
            
            # 避免无限循环
            if start <= 0:
                start = end
        
        logger.debug(
            f"Split {file_path} into {len(chunks)} chunks "
            f"(content length: {len(content)})"
        )
        
        return chunks
    
    def _find_sentence_boundary(
        self,
        text: str,
        position: int,
        search_range: int = 100
    ) -> int:
        """
        在指定位置附近查找句子边界
        
        Args:
            text: 文本内容
            position: 起始位置
            search_range: 搜索范围
            
        Returns:
            句子边界位置
        """
        # 句子结束符
        sentence_endings = ['. ', '。', '! ', '！', '? ', '？', '\n\n']
        
        # 在指定范围内搜索
        search_start = max(0, position - search_range // 2)
        search_end = min(len(text), position + search_range // 2)
        search_text = text[search_start:search_end]
        
        # 查找最近的句子结束符
        best_pos = position
        best_distance = float('inf')
        
        for ending in sentence_endings:
            pos = search_text.rfind(ending, 0, position - search_start)
            if pos != -1:
                actual_pos = search_start + pos + len(ending)
                distance = abs(actual_pos - position)
                if distance < best_distance:
                    best_distance = distance
                    best_pos = actual_pos
        
        return best_pos
    
    def process_document(
        self,
        file_path: str
    ) -> List[DocumentChunk]:
        """
        处理单个文档：读取、提取元数据、分块
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档分块列表
        """
        # 读取文件
        content = self.read_markdown_file(file_path)
        if content is None:
            return []
        
        # 提取元数据
        metadata = self.extract_metadata(file_path, content)
        
        # 分块
        chunks = self.split_into_chunks(content, file_path, metadata)
        
        logger.info(
            f"Processed document: {file_path} -> {len(chunks)} chunks"
        )
        
        return chunks
    
    def process_documents(
        self,
        file_paths: List[str]
    ) -> List[DocumentChunk]:
        """
        批量处理多个文档
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            所有文档的分块列表
        """
        all_chunks = []
        
        for file_path in file_paths:
            chunks = self.process_document(file_path)
            all_chunks.extend(chunks)
        
        logger.info(
            f"Processed {len(file_paths)} documents -> "
            f"{len(all_chunks)} total chunks"
        )
        
        return all_chunks


def create_document_processor(
    chunk_size: int = 512,
    chunk_overlap: int = 50
) -> DocumentProcessor:
    """
    创建文档处理器实例的便捷函数
    
    Args:
        chunk_size: 分块大小
        chunk_overlap: 分块重叠大小
        
    Returns:
        DocumentProcessor 实例
    """
    return DocumentProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
