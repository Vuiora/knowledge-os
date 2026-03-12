"""
Gitea API 客户端
用于从 Gitea 仓库克隆和拉取内容
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class GiteaClient:
    """Gitea 仓库客户端"""
    
    def __init__(self, gitea_url: str, token: str, repo_path: str):
        """
        初始化 Gitea 客户端
        
        Args:
            gitea_url: Gitea 服务器 URL (如 http://gitea:3000)
            token: Gitea API token
            repo_path: 仓库路径 (如 admin/knowledge-system)
        """
        self.gitea_url = gitea_url.rstrip('/')
        self.token = token
        self.repo_path = repo_path
        self.repo_url = self._build_repo_url()
    
    def _build_repo_url(self) -> str:
        """构建带认证的仓库 URL"""
        # 从 URL 中提取主机和端口
        url_parts = self.gitea_url.replace('http://', '').replace('https://', '')
        protocol = 'https' if 'https' in self.gitea_url else 'http'
        
        # 构建带 token 的 URL: http://token@host:port/repo
        return f"{protocol}://{self.token}@{url_parts}/{self.repo_path}.git"
    
    def clone_or_pull(self, target_dir: str, branch: str = 'main') -> bool:
        """
        克隆或拉取仓库
        
        Args:
            target_dir: 目标目录
            branch: 分支名称
            
        Returns:
            bool: 操作是否成功
        """
        target_path = Path(target_dir)
        
        try:
            if target_path.exists() and (target_path / '.git').exists():
                # 仓库已存在，执行 pull
                logger.info(f"仓库已存在，执行 git pull: {target_dir}")
                return self._git_pull(target_dir, branch)
            else:
                # 仓库不存在，执行 clone
                logger.info(f"克隆仓库到: {target_dir}")
                return self._git_clone(target_dir, branch)
        except Exception as e:
            logger.error(f"Git 操作失败: {e}")
            return False
    
    def _git_clone(self, target_dir: str, branch: str) -> bool:
        """克隆仓库"""
        try:
            # 确保父目录存在
            Path(target_dir).parent.mkdir(parents=True, exist_ok=True)
            
            # 执行 git clone
            result = subprocess.run(
                ['git', 'clone', '--branch', branch, '--depth', '1', self.repo_url, target_dir],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"仓库克隆成功: {target_dir}")
                return True
            else:
                logger.error(f"Git clone 失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Git clone 超时")
            return False
        except Exception as e:
            logger.error(f"Git clone 异常: {e}")
            return False
    
    def _git_pull(self, target_dir: str, branch: str) -> bool:
        """拉取最新更改"""
        try:
            # 切换到目标目录
            original_dir = os.getcwd()
            os.chdir(target_dir)
            
            try:
                # 执行 git pull
                result = subprocess.run(
                    ['git', 'pull', 'origin', branch],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    logger.info(f"仓库更新成功: {target_dir}")
                    return True
                else:
                    logger.error(f"Git pull 失败: {result.stderr}")
                    return False
                    
            finally:
                # 恢复原始目录
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            logger.error("Git pull 超时")
            return False
        except Exception as e:
            logger.error(f"Git pull 异常: {e}")
            return False
    
    def get_latest_commit(self, repo_dir: str) -> Optional[str]:
        """
        获取最新提交的 SHA
        
        Args:
            repo_dir: 仓库目录
            
        Returns:
            str: 提交 SHA，失败返回 None
        """
        try:
            original_dir = os.getcwd()
            os.chdir(repo_dir)
            
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return None
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            logger.error(f"获取提交 SHA 失败: {e}")
            return None
