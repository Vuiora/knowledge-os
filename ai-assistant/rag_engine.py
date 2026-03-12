#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) 查询引擎
负责问题嵌入生成、向量相似度搜索、上下文构建和 LLM 集成

Requirements: 6.4, 6.5
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class RAGQueryEngine:
    """RAG 查询引擎"""
    
    def __init__(
        self,
        embedding_generator,
        qdrant_client,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_context_length: int = 3000,
        temperature: float = 0.7
    ):
        """
        初始化 RAG 查询引擎
        
        Args:
            embedding_generator: 嵌入生成器实例
            qdrant_client: Qdrant 客户端实例
            openai_api_key: OpenAI API 密钥
            model: LLM 模型名称
            max_context_length: 最大上下文长度（字符数）
            temperature: 生成温度
        """
        self.embedding_generator = embedding_generator
        self.qdrant_client = qdrant_client
        self.model = model
        self.max_context_length = max_context_length
        self.temperature = temperature
        
        # 初始化 OpenAI 客户端
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not provided. LLM generation will not work.")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=api_key)
            logger.info(f"OpenAI client initialized with model: {model}")
    
    def generate_question_embedding(self, question: str) -> List[float]:
        """
        为问题生成嵌入向量
        
        Args:
            question: 用户问题
            
        Returns:
            嵌入向量
        """
        try:
            embedding = self.embedding_generator.generate_embedding(question)
            logger.debug(f"Generated embedding for question: {question[:50]}...")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate question embedding: {e}")
            raise
    
    def search_relevant_documents(
        self,
        question_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相关文档
        
        Args:
            question_embedding: 问题嵌入向量
            limit: 返回结果数量
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件（如按知识层次过滤）
            
        Returns:
            相关文档列表
        """
        try:
            results = self.qdrant_client.search_vectors(
                query_vector=question_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions
            )
            
            logger.info(f"Found {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search relevant documents: {e}")
            return []
    
    def build_context(
        self,
        search_results: List[Dict[str, Any]],
        max_length: Optional[int] = None
    ) -> str:
        """
        从搜索结果构建上下文
        
        Args:
            search_results: 搜索结果列表
            max_length: 最大上下文长度（字符数）
            
        Returns:
            构建的上下文字符串
        """
        if not search_results:
            return ""
        
        max_len = max_length or self.max_context_length
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(search_results):
            metadata = result.get('metadata', {})
            content = metadata.get('content', '')
            file_path = metadata.get('file_path', 'Unknown')
            title = metadata.get('title', 'Untitled')
            score = result.get('score', 0.0)
            
            # 格式化文档片段
            doc_part = f"""
[文档 {i+1}]
来源: {file_path}
标题: {title}
相关度: {score:.2f}
内容:
{content}
---
"""
            
            # 检查是否超过最大长度
            if current_length + len(doc_part) > max_len:
                # 如果是第一个文档，至少包含部分内容
                if i == 0:
                    remaining = max_len - current_length
                    if remaining > 200:  # 至少保留 200 字符
                        truncated_content = content[:remaining - 100] + "..."
                        doc_part = f"""
[文档 {i+1}]
来源: {file_path}
标题: {title}
相关度: {score:.2f}
内容:
{truncated_content}
---
"""
                        context_parts.append(doc_part)
                break
            
            context_parts.append(doc_part)
            current_length += len(doc_part)
        
        context = "\n".join(context_parts)
        logger.debug(f"Built context with {len(context_parts)} documents ({len(context)} chars)")
        
        return context
    
    def generate_answer(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        使用 LLM 生成答案
        
        Args:
            question: 用户问题
            context: 上下文信息
            system_prompt: 系统提示词
            
        Returns:
            生成的答案
        """
        if not self.openai_client:
            logger.warning("OpenAI client not initialized. Cannot generate answer.")
            return "抱歉，LLM 服务未配置。请设置 OPENAI_API_KEY 环境变量。"
        
        # 默认系统提示词
        if system_prompt is None:
            system_prompt = """你是一个专业的工程师知识助手。
你的任务是基于提供的知识库内容回答用户的技术问题。

回答要求：
1. 基于提供的知识库内容回答，不要编造信息
2. 如果知识库中没有相关信息，明确告知用户
3. 回答要准确、专业、易懂
4. 适当引用知识库中的关键信息
5. 使用中文回答

知识库内容：
{context}
"""
        
        # 构建完整的系统提示词
        full_system_prompt = system_prompt.format(context=context)
        
        try:
            # 调用 OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question: {question[:50]}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"抱歉，生成答案时出错：{str(e)}"
    
    def query(
        self,
        question: str,
        limit: int = 5,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict[str, Any]] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        完整的 RAG 查询流程
        
        Args:
            question: 用户问题
            limit: 返回的相关文档数量
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件
            include_sources: 是否包含源文档信息
            
        Returns:
            查询结果字典，包含 answer 和 sources
        """
        logger.info(f"Processing RAG query: {question}")
        
        try:
            # 1. 生成问题嵌入向量
            question_embedding = self.generate_question_embedding(question)
            
            # 2. 搜索相关文档
            search_results = self.search_relevant_documents(
                question_embedding=question_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions
            )
            
            # 3. 构建上下文
            context = self.build_context(search_results)
            
            # 4. 生成答案
            if context:
                answer = self.generate_answer(question, context)
            else:
                answer = "抱歉，我在知识库中没有找到相关信息来回答您的问题。"
            
            # 5. 格式化源文档信息
            sources = []
            if include_sources:
                for result in search_results:
                    metadata = result.get('metadata', {})
                    sources.append({
                        'file_path': metadata.get('file_path'),
                        'title': metadata.get('title'),
                        'layer': metadata.get('layer'),
                        'score': result.get('score'),
                        'content_preview': metadata.get('content', '')[:200] + '...'
                    })
            
            return {
                'answer': answer,
                'sources': sources,
                'num_sources': len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}", exc_info=True)
            return {
                'answer': f"抱歉，处理查询时出错：{str(e)}",
                'sources': [],
                'num_sources': 0,
                'error': str(e)
            }
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        获取引擎信息
        
        Returns:
            引擎信息字典
        """
        return {
            'model': self.model,
            'max_context_length': self.max_context_length,
            'temperature': self.temperature,
            'openai_configured': self.openai_client is not None,
            'embedding_model': self.embedding_generator.model_name,
            'embedding_dimension': self.embedding_generator.embedding_dim
        }


def create_rag_engine(
    embedding_generator,
    qdrant_client,
    openai_api_key: Optional[str] = None,
    model: Optional[str] = None
) -> RAGQueryEngine:
    """
    创建 RAG 查询引擎实例的便捷函数
    
    Args:
        embedding_generator: 嵌入生成器实例
        qdrant_client: Qdrant 客户端实例
        openai_api_key: OpenAI API 密钥
        model: LLM 模型名称
        
    Returns:
        RAGQueryEngine 实例
    """
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    return RAGQueryEngine(
        embedding_generator=embedding_generator,
        qdrant_client=qdrant_client,
        openai_api_key=openai_api_key,
        model=model
    )
