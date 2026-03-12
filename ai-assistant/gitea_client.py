#!/usr/bin/env python3
"""
Gitea API 客户端模块
负责与 Gitea 服务器交互，获取仓库文件列表、读取文件内容、解析 Webhook 事件

Requirements: 6.2, 8.4
"""

import os
import base64
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class GiteaClient:
    """Gitea API 客户端"""
    
    def __init__(
        self,
        base_url: str = None,
        api_token: str = None,
        repo_path: str = None,
        timeout: float = 30.0
    ):
        """
        初始化 Gitea 客户端
        
        Args:
            base_url: Gitea 服务器地址
            api_token: API 访问令牌
            repo_path: 仓库路径（格式：owner/repo）
            timeout: 请求超时时间（秒）
        """
        self.base_url = (base_url or os.getenv("GITEA_URL", "http://gitea:3000")).rstrip('/')
        self.api_token = api_token or os.getenv("GITEA_TOKEN", "")
        self.repo_path = repo_path or os.getenv("REPO_PATH", "admin/knowledge-system")
        self.timeout = timeout
        
        # 构建 API 基础 URL
        self.api_base = f"{self.base_url}/api/v1"
        
        # 设置请求头
        self.headers = {
            "Authorization": f"token {self.api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(
            f"GiteaClient initialized: {self.base_url}, repo: {self.repo_path}"
        )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        发送 HTTP 请求到 Gitea API
        
        Args:
            method: HTTP 方法（GET, POST, etc.）
            endpoint: API 端点
            **kwargs: 其他请求参数
            
        Returns:
            响应 JSON 数据，失败返回 None
        """
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    **kwargs
                )
                
                response.raise_for_status()
                
                # 某些端点可能返回空响应
                if response.status_code == 204:
                    return {}
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} for {method} {url}: "
                f"{e.response.text}"
            )
            return None
        except httpx.TimeoutException:
            logger.error(f"Request timeout for {method} {url}")
            return None
        except Exception as e:
            logger.error(f"Request failed for {method} {url}: {e}")
            return None
    
    async def get_repository_info(self) -> Optional[Dict[str, Any]]:
        """
        获取仓库信息
        
        Returns:
            仓库信息字典
        """
        endpoint = f"repos/{self.repo_path}"
        return await self._make_request("GET", endpoint)
    
    async def list_repository_files(
        self,
        path: str = "",
        ref: str = "main"
    ) -> List[Dict[str, Any]]:
        """
        列出仓库中的文件
        
        Args:
            path: 目录路径（空字符串表示根目录）
            ref: 分支或提交引用
            
        Returns:
            文件信息列表
        """
        endpoint = f"repos/{self.repo_path}/contents/{path}"
        params = {"ref": ref}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result is None:
            return []
        
        # 如果是单个文件，包装成列表
        if isinstance(result, dict):
            return [result]
        
        return result
    
    async def get_file_content(
        self,
        file_path: str,
        ref: str = "main"
    ) -> Optional[str]:
        """
        获取文件内容
        
        Args:
            file_path: 文件路径
            ref: 分支或提交引用
            
        Returns:
            文件内容（文本），失败返回 None
        """
        endpoint = f"repos/{self.repo_path}/contents/{file_path}"
        params = {"ref": ref}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result is None:
            return None
        
        # 检查是否是文件
        if result.get("type") != "file":
            logger.error(f"{file_path} is not a file")
            return None
        
        # 解码 Base64 内容
        try:
            content_base64 = result.get("content", "")
            content_bytes = base64.b64decode(content_base64)
            content_text = content_bytes.decode('utf-8')
            return content_text
        except Exception as e:
            logger.error(f"Failed to decode file content for {file_path}: {e}")
            return None
    
    async def list_markdown_files(
        self,
        directory: str = "knowledge",
        ref: str = "main",
        recursive: bool = True
    ) -> List[str]:
        """
        递归列出目录中的所有 Markdown 文件
        
        Args:
            directory: 起始目录
            ref: 分支或提交引用
            recursive: 是否递归搜索子目录
            
        Returns:
            Markdown 文件路径列表
        """
        markdown_files = []
        
        async def scan_directory(path: str):
            """递归扫描目录"""
            files = await self.list_repository_files(path, ref)
            
            for file_info in files:
                file_type = file_info.get("type")
                file_path = file_info.get("path", "")
                file_name = file_info.get("name", "")
                
                if file_type == "file":
                    # 检查是否是 Markdown 文件
                    if file_name.endswith('.md'):
                        markdown_files.append(file_path)
                
                elif file_type == "dir" and recursive:
                    # 递归扫描子目录
                    await scan_directory(file_path)
        
        await scan_directory(directory)
        
        logger.info(
            f"Found {len(markdown_files)} Markdown files in {directory}"
        )
        
        return markdown_files
    
    async def get_commit_info(
        self,
        sha: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取提交信息
        
        Args:
            sha: 提交 SHA
            
        Returns:
            提交信息字典
        """
        endpoint = f"repos/{self.repo_path}/git/commits/{sha}"
        return await self._make_request("GET", endpoint)
    
    async def list_commits(
        self,
        ref: str = "main",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        列出提交历史
        
        Args:
            ref: 分支或提交引用
            limit: 返回的提交数量
            
        Returns:
            提交信息列表
        """
        endpoint = f"repos/{self.repo_path}/commits"
        params = {
            "sha": ref,
            "limit": limit
        }
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result is None:
            return []
        
        return result
    
    def parse_webhook_event(
        self,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        解析 Webhook 事件数据
        
        Args:
            event_data: Webhook 事件 JSON 数据
            
        Returns:
            解析后的事件信息
        """
        parsed = {
            'event_type': event_data.get('event_type', 'unknown'),
            'repository': event_data.get('repository', {}).get('full_name'),
            'ref': event_data.get('ref', ''),
            'commits': [],
            'changed_files': []
        }
        
        # 解析提交信息
        commits = event_data.get('commits', [])
        for commit in commits:
            commit_info = {
                'id': commit.get('id'),
                'message': commit.get('message'),
                'author': commit.get('author', {}).get('name'),
                'timestamp': commit.get('timestamp'),
                'added': commit.get('added', []),
                'modified': commit.get('modified', []),
                'removed': commit.get('removed', [])
            }
            parsed['commits'].append(commit_info)
            
            # 收集所有变更的文件
            parsed['changed_files'].extend(commit.get('added', []))
            parsed['changed_files'].extend(commit.get('modified', []))
            parsed['changed_files'].extend(commit.get('removed', []))
        
        # 去重
        parsed['changed_files'] = list(set(parsed['changed_files']))
        
        return parsed
    
    def filter_knowledge_files(
        self,
        file_paths: List[str],
        knowledge_dir: str = "knowledge"
    ) -> List[str]:
        """
        过滤出知识目录中的 Markdown 文件
        
        Args:
            file_paths: 文件路径列表
            knowledge_dir: 知识目录名称
            
        Returns:
            过滤后的文件路径列表
        """
        filtered = []
        
        for file_path in file_paths:
            # 检查是否在知识目录中
            if file_path.startswith(f"{knowledge_dir}/"):
                # 检查是否是 Markdown 文件
                if file_path.endswith('.md'):
                    filtered.append(file_path)
        
        return filtered
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态字典
        """
        try:
            # 尝试获取仓库信息
            repo_info = await self.get_repository_info()
            
            if repo_info:
                return {
                    'healthy': True,
                    'base_url': self.base_url,
                    'repo_path': self.repo_path,
                    'repo_name': repo_info.get('name'),
                    'default_branch': repo_info.get('default_branch')
                }
            else:
                return {
                    'healthy': False,
                    'base_url': self.base_url,
                    'repo_path': self.repo_path,
                    'error': 'Failed to get repository info'
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'healthy': False,
                'base_url': self.base_url,
                'repo_path': self.repo_path,
                'error': str(e)
            }


def create_gitea_client(
    base_url: Optional[str] = None,
    api_token: Optional[str] = None,
    repo_path: Optional[str] = None
) -> GiteaClient:
    """
    创建 Gitea 客户端实例的便捷函数
    
    Args:
        base_url: Gitea 服务器地址
        api_token: API 访问令牌
        repo_path: 仓库路径
        
    Returns:
        GiteaClient 实例
    """
    return GiteaClient(
        base_url=base_url,
        api_token=api_token,
        repo_path=repo_path
    )
