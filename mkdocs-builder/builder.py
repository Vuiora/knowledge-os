"""
MkDocs 构建器
负责执行 MkDocs 构建和管理构建状态
"""

import os
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)


class MkDocsBuilder:
    """MkDocs 构建器"""
    
    def __init__(self, repo_dir: str, site_dir: str, config_template: str):
        """
        初始化构建器
        
        Args:
            repo_dir: Git 仓库目录
            site_dir: 构建输出目录
            config_template: mkdocs.yml 模板路径
        """
        self.repo_dir = Path(repo_dir)
        self.site_dir = Path(site_dir)
        self.config_template = Path(config_template)
        self.knowledge_dir = self.repo_dir / 'knowledge'
        self.build_dir = self.repo_dir / '_build'
        self.last_build_time: Optional[datetime] = None
        self.last_build_status: str = 'never'
        self.last_commit_sha: Optional[str] = None
    
    def prepare_build_environment(self) -> bool:
        """
        准备构建环境
        
        Returns:
            bool: 准备是否成功
        """
        try:
            # 创建构建目录
            self.build_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制 mkdocs.yml 模板
            config_dest = self.build_dir / 'mkdocs.yml'
            shutil.copy(self.config_template, config_dest)
            
            # 读取配置并设置 docs_dir
            with open(config_dest, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 设置文档目录为 knowledge 目录
            config['docs_dir'] = str(self.knowledge_dir.absolute())
            config['site_dir'] = str(self.site_dir.absolute())
            
            # 写回配置
            with open(config_dest, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False)
            
            # 确保 knowledge 目录存在
            if not self.knowledge_dir.exists():
                logger.error(f"知识目录不存在: {self.knowledge_dir}")
                return False
            
            # 检查是否有 index.md，如果没有则创建默认的
            index_file = self.knowledge_dir / 'index.md'
            if not index_file.exists():
                logger.info("创建默认 index.md")
                self._create_default_index()
            
            # 复制额外的资源文件（CSS, JS）
            self._copy_extra_resources()
            
            logger.info("构建环境准备完成")
            return True
            
        except Exception as e:
            logger.error(f"准备构建环境失败: {e}")
            return False
    
    def _create_default_index(self):
        """创建默认的 index.md"""
        template_index = Path(__file__).parent / 'templates' / 'index.md'
        dest_index = self.knowledge_dir / 'index.md'
        
        if template_index.exists():
            shutil.copy(template_index, dest_index)
        else:
            # 如果模板不存在，创建一个简单的
            with open(dest_index, 'w', encoding='utf-8') as f:
                f.write("# 工程师知识库\n\n欢迎来到工程师知识库！\n")
    
    def _copy_extra_resources(self):
        """复制额外的资源文件"""
        # 复制 stylesheets
        src_stylesheets = Path(__file__).parent / 'stylesheets'
        dest_stylesheets = self.knowledge_dir / 'stylesheets'
        
        if src_stylesheets.exists():
            if dest_stylesheets.exists():
                shutil.rmtree(dest_stylesheets)
            shutil.copytree(src_stylesheets, dest_stylesheets)
        
        # 复制 javascripts
        src_javascripts = Path(__file__).parent / 'javascripts'
        dest_javascripts = self.knowledge_dir / 'javascripts'
        
        if src_javascripts.exists():
            if dest_javascripts.exists():
                shutil.rmtree(dest_javascripts)
            shutil.copytree(src_javascripts, dest_javascripts)
    
    def build(self) -> Dict[str, any]:
        """
        执行 MkDocs 构建
        
        Returns:
            dict: 构建结果
                - success: bool
                - message: str
                - duration: float (秒)
                - commit_sha: str
        """
        start_time = datetime.now()
        
        try:
            # 准备构建环境
            if not self.prepare_build_environment():
                return {
                    'success': False,
                    'message': '构建环境准备失败',
                    'duration': 0,
                    'commit_sha': None
                }
            
            # 切换到构建目录
            original_dir = os.getcwd()
            os.chdir(self.build_dir)
            
            try:
                # 执行 mkdocs build
                logger.info("开始执行 MkDocs 构建...")
                result = subprocess.run(
                    ['mkdocs', 'build', '--clean', '--strict'],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 分钟超时
                )
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if result.returncode == 0:
                    self.last_build_time = datetime.now()
                    self.last_build_status = 'success'
                    
                    # 获取提交 SHA
                    commit_sha = self._get_commit_sha()
                    self.last_commit_sha = commit_sha
                    
                    logger.info(f"MkDocs 构建成功，耗时 {duration:.2f} 秒")
                    
                    return {
                        'success': True,
                        'message': 'MkDocs 构建成功',
                        'duration': duration,
                        'commit_sha': commit_sha,
                        'build_time': self.last_build_time.isoformat()
                    }
                else:
                    self.last_build_status = 'failed'
                    error_msg = result.stderr or result.stdout
                    logger.error(f"MkDocs 构建失败: {error_msg}")
                    
                    return {
                        'success': False,
                        'message': f'MkDocs 构建失败: {error_msg}',
                        'duration': duration,
                        'commit_sha': None
                    }
                    
            finally:
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            self.last_build_status = 'timeout'
            logger.error("MkDocs 构建超时")
            
            return {
                'success': False,
                'message': 'MkDocs 构建超时',
                'duration': duration,
                'commit_sha': None
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.last_build_status = 'error'
            logger.error(f"MkDocs 构建异常: {e}")
            
            return {
                'success': False,
                'message': f'MkDocs 构建异常: {str(e)}',
                'duration': duration,
                'commit_sha': None
            }
    
    def _get_commit_sha(self) -> Optional[str]:
        """获取当前提交 SHA"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_dir), 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取提交 SHA 失败: {e}")
            return None
    
    def get_build_status(self) -> Dict[str, any]:
        """
        获取构建状态
        
        Returns:
            dict: 构建状态信息
        """
        return {
            'last_build_time': self.last_build_time.isoformat() if self.last_build_time else None,
            'last_build_status': self.last_build_status,
            'last_commit_sha': self.last_commit_sha,
            'site_exists': self.site_dir.exists() and any(self.site_dir.iterdir())
        }
    
    def clean(self) -> bool:
        """
        清理构建目录
        
        Returns:
            bool: 清理是否成功
        """
        try:
            if self.site_dir.exists():
                shutil.rmtree(self.site_dir)
                logger.info(f"清理构建目录: {self.site_dir}")
            
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                logger.info(f"清理临时目录: {self.build_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"清理目录失败: {e}")
            return False
