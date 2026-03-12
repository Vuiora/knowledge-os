#!/usr/bin/env python3
"""
简单测试脚本，验证模块可以正确导入和基本功能
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """测试模块导入"""
    logger.info("Testing module imports...")
    
    try:
        from document_processor import DocumentProcessor, create_document_processor
        logger.info("✓ document_processor imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import document_processor: {e}")
        return False
    
    try:
        from embedding_generator import EmbeddingGenerator, create_embedding_generator
        logger.info("✓ embedding_generator imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import embedding_generator: {e}")
        return False
    
    try:
        from gitea_client import GiteaClient, create_gitea_client
        logger.info("✓ gitea_client imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import gitea_client: {e}")
        return False
    
    try:
        from qdrant_client_wrapper import QdrantClientWrapper, create_qdrant_client
        logger.info("✓ qdrant_client_wrapper imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import qdrant_client_wrapper: {e}")
        return False
    
    return True


def test_document_processor():
    """测试文档处理器基本功能"""
    logger.info("\nTesting DocumentProcessor...")
    
    try:
        from document_processor import create_document_processor
        
        processor = create_document_processor(chunk_size=100, chunk_overlap=20)
        
        # 测试元数据提取
        test_content = "# Test Document\n\nThis is a test document with some content."
        metadata = processor.extract_metadata("knowledge/01-foundations/test.md", test_content)
        
        assert metadata['file_name'] == 'test.md'
        assert metadata['layer'] == '01-foundations'
        assert metadata['title'] == 'Test Document'
        
        logger.info("✓ DocumentProcessor basic functionality works")
        return True
        
    except Exception as e:
        logger.error(f"✗ DocumentProcessor test failed: {e}")
        return False


def test_embedding_generator_structure():
    """测试嵌入生成器结构（不加载模型）"""
    logger.info("\nTesting EmbeddingGenerator structure...")
    
    try:
        from embedding_generator import EmbeddingGenerator
        
        # 只测试类结构，不实际加载模型
        assert hasattr(EmbeddingGenerator, 'generate_embedding')
        assert hasattr(EmbeddingGenerator, 'generate_embeddings_batch')
        assert hasattr(EmbeddingGenerator, 'generate_embeddings_for_chunks')
        
        logger.info("✓ EmbeddingGenerator structure is correct")
        return True
        
    except Exception as e:
        logger.error(f"✗ EmbeddingGenerator structure test failed: {e}")
        return False


def test_gitea_client_structure():
    """测试 Gitea 客户端结构"""
    logger.info("\nTesting GiteaClient structure...")
    
    try:
        from gitea_client import create_gitea_client
        
        client = create_gitea_client(
            base_url="http://localhost:3001",
            api_token="test_token",
            repo_path="admin/test-repo"
        )
        
        assert client.base_url == "http://localhost:3001"
        assert client.repo_path == "admin/test-repo"
        
        # 测试文件过滤
        test_files = [
            "knowledge/01-foundations/test.md",
            "knowledge/02-technologies/ai.md",
            "README.md",
            "scripts/init.sh"
        ]
        
        filtered = client.filter_knowledge_files(test_files)
        assert len(filtered) == 2
        assert "knowledge/01-foundations/test.md" in filtered
        
        logger.info("✓ GiteaClient structure and basic methods work")
        return True
        
    except Exception as e:
        logger.error(f"✗ GiteaClient structure test failed: {e}")
        return False


def main():
    """运行所有测试"""
    logger.info("=" * 60)
    logger.info("Running module tests for AI Assistant")
    logger.info("=" * 60)
    
    results = []
    
    results.append(("Module Imports", test_imports()))
    results.append(("DocumentProcessor", test_document_processor()))
    results.append(("EmbeddingGenerator Structure", test_embedding_generator_structure()))
    results.append(("GiteaClient Structure", test_gitea_client_structure()))
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Results:")
    logger.info("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("All tests passed! ✓")
        return 0
    else:
        logger.error("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
