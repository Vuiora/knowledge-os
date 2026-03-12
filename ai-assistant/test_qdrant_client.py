#!/usr/bin/env python3
"""
Qdrant 客户端测试脚本
验证 Collection 初始化和向量 CRUD 操作
"""

import sys
import logging
from qdrant_client_wrapper import QdrantClientWrapper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_qdrant_client():
    """测试 Qdrant 客户端功能"""
    
    print("=" * 60)
    print("测试 Qdrant 客户端库")
    print("=" * 60)
    
    # 1. 初始化客户端
    print("\n1. 初始化客户端...")
    client = QdrantClientWrapper(
        host="localhost",
        port=6333,
        collection_name="test_collection"
    )
    
    # 2. 健康检查
    print("\n2. 健康检查...")
    if client.health_check():
        print("✓ Qdrant 服务健康")
    else:
        print("✗ Qdrant 服务不可用")
        return False
    
    # 3. 初始化 Collection
    print("\n3. 初始化 Collection...")
    if client.initialize_collection(vector_size=384):
        print("✓ Collection 初始化成功")
    else:
        print("✗ Collection 初始化失败")
        return False
    
    # 4. 插入测试向量
    print("\n4. 插入测试向量...")
    test_vectors = [
        [0.1] * 384,  # 向量 1
        [0.2] * 384,  # 向量 2
        [0.3] * 384,  # 向量 3
    ]
    test_ids = ["doc1", "doc2", "doc3"]
    test_metadata = [
        {"file_path": "/knowledge/test1.md", "content": "测试文档 1"},
        {"file_path": "/knowledge/test2.md", "content": "测试文档 2"},
        {"file_path": "/knowledge/test3.md", "content": "测试文档 3"},
    ]
    
    if client.upsert_vectors(test_vectors, test_ids, test_metadata):
        print(f"✓ 成功插入 {len(test_vectors)} 个向量")
    else:
        print("✗ 向量插入失败")
        return False
    
    # 5. 根据 ID 检索向量
    print("\n5. 根据 ID 检索向量...")
    result = client.get_vector_by_id("doc1")
    if result:
        print(f"✓ 成功检索向量: {result['id']}")
        print(f"  元数据: {result['metadata']}")
    else:
        print("✗ 向量检索失败")
        return False
    
    # 6. 向量相似度搜索
    print("\n6. 向量相似度搜索...")
    query_vector = [0.15] * 384  # 查询向量（接近向量 1）
    search_results = client.search_vectors(
        query_vector=query_vector,
        limit=2,
        score_threshold=0.0
    )
    
    if search_results:
        print(f"✓ 找到 {len(search_results)} 个相似向量:")
        for i, result in enumerate(search_results, 1):
            print(f"  {i}. ID: {result['id']}, Score: {result['score']:.4f}")
            print(f"     文件: {result['metadata']['file_path']}")
    else:
        print("✗ 搜索失败")
        return False
    
    # 7. 获取 Collection 信息
    print("\n7. 获取 Collection 信息...")
    info = client.get_collection_info()
    if info:
        print(f"✓ Collection 信息:")
        print(f"  向量数量: {info.get('vectors_count', 'N/A')}")
        print(f"  点数量: {info.get('points_count', 'N/A')}")
    else:
        print("✗ 获取信息失败")
    
    # 8. 删除向量
    print("\n8. 删除测试向量...")
    if client.delete_vectors(["doc1", "doc2", "doc3"]):
        print("✓ 成功删除向量")
    else:
        print("✗ 删除失败")
        return False
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_qdrant_client()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        sys.exit(1)
