"""
目录扫描器模块
负责递归扫描目录结构，识别缺失 index.md 的目录
"""

from typing import List
from pathlib import Path
from .models import DirectoryInfo
from .logger import logger


class DirectoryScanner:
    """目录扫描器"""
    
    def scan(self, root_path: str, excluded: List[str]) -> List[DirectoryInfo]:
        """
        扫描目录结构
        
        Args:
            root_path: 根目录路径
            excluded: 排除的目录列表
            
        Returns:
            目录信息列表
        """
        logger.info(f"扫描目录: {root_path}")
        
        root = Path(root_path)
        if not root.exists():
            logger.error(f"目录不存在: {root_path}")
            return []
        
        if not root.is_dir():
            logger.error(f"路径不是目录: {root_path}")
            return []
        
        results = []
        self._scan_recursive(root, root, excluded, results)
        
        logger.info(f"扫描完成，共找到 {len(results)} 个目录")
        return results
    
    def _scan_recursive(self, root: Path, current: Path, excluded: List[str], 
                       results: List[DirectoryInfo]) -> None:
        """
        递归扫描目录
        
        Args:
            root: 根目录路径
            current: 当前目录路径
            excluded: 排除的目录列表
            results: 结果列表
        """
        # 检查是否应该排除当前目录
        if self.is_excluded(str(current), excluded):
            logger.debug(f"跳过排除目录: {current}")
            return
        
        try:
            # 收集子目录和 Markdown 文件
            children = []
            markdown_files = []
            
            for item in current.iterdir():
                if item.is_dir():
                    children.append(item.name)
                elif item.is_file() and item.suffix == '.md' and item.name != 'index.md':
                    markdown_files.append(item.name)
            
            # 创建目录信息
            dir_info = DirectoryInfo(
                path=str(current),
                name=current.name,
                level=self.get_directory_level(str(current)),
                has_index=self.has_index(str(current)),
                children=sorted(children),
                markdown_files=sorted(markdown_files),
                parent=str(current.parent) if current != root else None
            )
            
            results.append(dir_info)
            logger.debug(f"扫描目录: {current}, 子目录: {len(children)}, MD文件: {len(markdown_files)}")
            
            # 递归扫描子目录
            for child_name in children:
                child_path = current / child_name
                self._scan_recursive(root, child_path, excluded, results)
                
        except PermissionError:
            logger.warning(f"无权限访问目录: {current}")
        except Exception as e:
            logger.error(f"扫描目录时出错 {current}: {e}")
    
    def is_excluded(self, path: str, excluded: List[str]) -> bool:
        """
        判断目录是否应该被排除
        
        Args:
            path: 目录路径
            excluded: 排除的目录列表
            
        Returns:
            是否排除
        """
        path_obj = Path(path)
        
        # 检查路径中的任何部分是否在排除列表中
        for part in path_obj.parts:
            if part in excluded:
                return True
        
        # 检查目录名是否在排除列表中
        if path_obj.name in excluded:
            return True
        
        return False
    
    def has_index(self, path: str) -> bool:
        """
        判断目录是否包含 index.md
        
        Args:
            path: 目录路径
            
        Returns:
            是否包含 index.md
        """
        index_path = Path(path) / "index.md"
        return index_path.exists() and index_path.is_file()
    
    def get_directory_level(self, path: str) -> int:
        """
        获取目录层级（相对于根目录的深度）
        
        Args:
            path: 目录路径
            
        Returns:
            目录层级
        """
        return len(Path(path).parts)
