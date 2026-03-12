#!/usr/bin/env python3
"""
RAG 查询引擎测试
测试 RAG 引擎的核心功能

Requirements: 6.4, 6.5
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_engine import RAGQueryEngine


class MockEmbeddingGenerator:
    """模拟嵌入生成器"""
    
    def __init__(self):
        self.model_name = "mock-model"
        self.embedding_dim = 384
    
    def generate_embedding(self, text):
        """生成模拟嵌入向量"""
        return [0.1] * self.embedding_dim


class MockQdrantClient:
    """模拟 Qdrant 客户端"""
    
    def __init__(self):
        self.mock_results = []
    
    def search_vectors(self, query_vector, limit=5, score_threshold=0.7, filter_conditions=None):
        """返回模拟搜索结果"""
        return self.mock_results
    
    def set_mock_results(self, results):
        """设置模拟结果"""
        self.mock_results = results


def test_rag_engine_initialization():
    """测试 RAG 引擎初始化"""
    print("Testing RAG engine initialization...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    
    # 不使用 OpenAI API 进行测试
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None
    )
    
    assert engine is not None
    assert engine.embedding_generator == mock_embedding
    assert engine.qdrant_client == mock_qdrant
    assert engine.openai_client is None  # 没有 API key
    
    print("✓ RAG engine initialization test passed")


def test_question_embedding_generation():
    """测试问题嵌入生成"""
    print("Testing question embedding generation...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None
    )
    
    question = "什么是 TCP 协议？"
    embedding = engine.generate_question_embedding(question)
    
    assert embedding is not None
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)
    
    print("✓ Question embedding generation test passed")


def test_search_relevant_documents():
    """测试相关文档搜索"""
    print("Testing relevant document search...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    
    # 设置模拟搜索结果
    mock_results = [
        {
            'id': '1',
            'score': 0.95,
            'metadata': {
                'file_path': 'knowledge/02-technologies/network/tcp.md',
                'title': 'TCP 协议',
                'content': 'TCP 是传输控制协议...',
                'layer': '02-technologies'
            }
        },
        {
            'id': '2',
            'score': 0.85,
            'metadata': {
                'file_path': 'knowledge/01-foundations/network/protocols.md',
                'title': '网络协议基础',
                'content': 'TCP/IP 协议栈...',
                'layer': '01-foundations'
            }
        }
    ]
    mock_qdrant.set_mock_results(mock_results)
    
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None
    )
    
    question_embedding = [0.1] * 384
    results = engine.search_relevant_documents(
        question_embedding=question_embedding,
        limit=5,
        score_threshold=0.7
    )
    
    assert len(results) == 2
    assert results[0]['score'] == 0.95
    assert results[0]['metadata']['title'] == 'TCP 协议'
    
    print("✓ Relevant document search test passed")


def test_context_building():
    """测试上下文构建"""
    print("Testing context building...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None
    )
    
    search_results = [
        {
            'id': '1',
            'score': 0.95,
            'metadata': {
                'file_path': 'knowledge/02-technologies/network/tcp.md',
                'title': 'TCP 协议',
                'content': 'TCP 是传输控制协议，提供可靠的、面向连接的数据传输服务。',
                'layer': '02-technologies'
            }
        }
    ]
    
    context = engine.build_context(search_results)
    
    assert context is not None
    assert len(context) > 0
    assert 'TCP 协议' in context
    assert 'knowledge/02-technologies/network/tcp.md' in context
    assert '0.95' in context
    
    print("✓ Context building test passed")


def test_context_building_with_length_limit():
    """测试带长度限制的上下文构建"""
    print("Testing context building with length limit...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None
    )
    
    # 创建多个长文档
    search_results = [
        {
            'id': str(i),
            'score': 0.9 - i * 0.1,
            'metadata': {
                'file_path': f'knowledge/doc{i}.md',
                'title': f'Document {i}',
                'content': 'A' * 1000,  # 长内容
                'layer': '02-technologies'
            }
        }
        for i in range(5)
    ]
    
    context = engine.build_context(search_results, max_length=500)
    
    assert context is not None
    assert len(context) <= 600  # 允许一些格式化开销
    
    print("✓ Context building with length limit test passed")


def test_query_without_openai():
    """测试不使用 OpenAI 的查询（仅搜索）"""
    print("Testing query without OpenAI...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    
    # 设置模拟搜索结果
    mock_results = [
        {
            'id': '1',
            'score': 0.95,
            'metadata': {
                'file_path': 'knowledge/02-technologies/network/tcp.md',
                'title': 'TCP 协议',
                'content': 'TCP 是传输控制协议...',
                'layer': '02-technologies'
            }
        }
    ]
    mock_qdrant.set_mock_results(mock_results)
    
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None
    )
    
    result = engine.query(
        question="什么是 TCP 协议？",
        limit=5,
        score_threshold=0.7
    )
    
    assert 'answer' in result
    assert 'sources' in result
    assert 'num_sources' in result
    assert result['num_sources'] == 1
    assert len(result['sources']) == 1
    assert result['sources'][0]['title'] == 'TCP 协议'
    
    # 答案应该提示 LLM 未配置
    assert 'LLM' in result['answer'] or '未配置' in result['answer']
    
    print("✓ Query without OpenAI test passed")


def test_query_with_no_results():
    """测试没有搜索结果的查询"""
    print("Testing query with no results...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    mock_qdrant.set_mock_results([])  # 空结果
    
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None
    )
    
    result = engine.query(
        question="这是一个不存在的问题",
        limit=5,
        score_threshold=0.7
    )
    
    assert 'answer' in result
    assert 'sources' in result
    assert result['num_sources'] == 0
    assert len(result['sources']) == 0
    assert '没有找到' in result['answer'] or '未找到' in result['answer']
    
    print("✓ Query with no results test passed")


def test_engine_info():
    """测试引擎信息获取"""
    print("Testing engine info...")
    
    mock_embedding = MockEmbeddingGenerator()
    mock_qdrant = MockQdrantClient()
    
    engine = RAGQueryEngine(
        embedding_generator=mock_embedding,
        qdrant_client=mock_qdrant,
        openai_api_key=None,
        model="gpt-4"
    )
    
    info = engine.get_engine_info()
    
    assert 'model' in info
    assert 'max_context_length' in info
    assert 'temperature' in info
    assert 'openai_configured' in info
    assert 'embedding_model' in info
    assert 'embedding_dimension' in info
    
    assert info['model'] == 'gpt-4'
    assert info['openai_configured'] is False
    assert info['embedding_model'] == 'mock-model'
    assert info['embedding_dimension'] == 384
    
    print("✓ Engine info test passed")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Running RAG Engine Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_rag_engine_initialization,
        test_question_embedding_generation,
        test_search_relevant_documents,
        test_context_building,
        test_context_building_with_length_limit,
        test_query_without_openai,
        test_query_with_no_results,
        test_engine_info
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
