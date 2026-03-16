"""
内容分析器模块
负责分析目录类型，提取元数据
"""

from typing import List
from .models import DirectoryInfo, DirectoryMetadata, DirectoryType, ChildItem
from .logger import logger


class ContentAnalyzer:
    """内容分析器"""
    
    def analyze(self, dir_info: DirectoryInfo) -> DirectoryMetadata:
        """
        分析目录信息，生成元数据
        
        Args:
            dir_info: 目录信息
            
        Returns:
            目录元数据
        """
        logger.info(f"分析目录: {dir_info.path}")
        
        # 检测目录类型
        dir_type = self.detect_type(dir_info)
        
        # 提取标题
        title = self.extract_title(dir_info.name)
        
        # 生成描述
        description = self.generate_description(dir_info)
        
        # 收集子项列表
        children = self.list_children(dir_info)
        
        # 构建面包屑导航
        breadcrumb = self._build_breadcrumb(dir_info.path)
        
        # 设置难度级别指示器
        level_indicator = None
        if dir_type == DirectoryType.DIFFICULTY:
            if 'beginner' in dir_info.name.lower():
                level_indicator = '🟢'
            elif 'intermediate' in dir_info.name.lower():
                level_indicator = '🟡'
            elif 'advanced' in dir_info.name.lower():
                level_indicator = '🔴'
        
        return DirectoryMetadata(
            type=dir_type,
            title=title,
            description=description,
            children=children,
            breadcrumb=breadcrumb,
            level_indicator=level_indicator
        )
    
    def _build_breadcrumb(self, path: str) -> List[str]:
        """
        构建面包屑导航
        
        Args:
            path: 目录路径
            
        Returns:
            面包屑列表
        """
        from pathlib import Path
        
        path_obj = Path(path)
        breadcrumb = []
        
        # 从路径中提取各级目录名并转换为标题
        for part in path_obj.parts:
            if part and part != '.':
                title = self.extract_title(part)
                breadcrumb.append(title)
        
        return breadcrumb
    
    def detect_type(self, dir_info: DirectoryInfo) -> DirectoryType:
        """
        检测目录类型
        
        Args:
            dir_info: 目录信息
            
        Returns:
            目录类型
        """
        dir_name = dir_info.name.lower()
        
        # 1. 识别难度级别目录（beginner/intermediate/advanced）
        if any(level in dir_name for level in ['beginner', 'intermediate', 'advanced']):
            return DirectoryType.DIFFICULTY
        
        # 2. 识别主层级目录（XX-layer, XX-concerns）
        if dir_name.endswith('-layer') or dir_name.endswith('-concerns'):
            return DirectoryType.MAIN_LAYER
        
        # 3. 识别子主题目录（数字前缀，且不是难度级别）
        # 检查是否以数字开头（如 01-, 02-）
        import re
        if re.match(r'^\d{1,2}-', dir_name):
            return DirectoryType.SUB_TOPIC
        
        # 4. 识别内容目录（包含 .md 文件，除了 index.md）
        if dir_info.markdown_files:
            return DirectoryType.CONTENT
        
        return DirectoryType.UNKNOWN
    
    def extract_title(self, dir_name: str) -> str:
        """
        从目录名提取标题（去除前缀和连字符）
        
        Args:
            dir_name: 目录名称
            
        Returns:
            提取的标题
        """
        import re
        
        # 去除数字前缀（如 01-, 02-）
        title = re.sub(r'^\d{1,2}-', '', dir_name)
        
        # 将连字符替换为空格
        title = title.replace('-', ' ')
        
        # 首字母大写（如果是英文）
        title = title.strip()
        
        return title
    
    def generate_description(self, dir_info: DirectoryInfo) -> str:
        """
        生成目录描述
        
        Args:
            dir_info: 目录信息
            
        Returns:
            目录描述
        """
        dir_type = self.detect_type(dir_info)
        title = self.extract_title(dir_info.name)
        
        # 根据目录类型生成描述
        if dir_type == DirectoryType.MAIN_LAYER:
            return f"本部分包含 {title} 相关的核心内容和子主题。"
        elif dir_type == DirectoryType.SUB_TOPIC:
            return f"关于 {title} 的详细内容和学习资源。"
        elif dir_type == DirectoryType.DIFFICULTY:
            level_map = {
                'beginner': '入门',
                'intermediate': '进阶',
                'advanced': '高级'
            }
            level = 'beginner'
            for key in level_map.keys():
                if key in dir_info.name.lower():
                    level = key
                    break
            return f"本部分包含 {level_map[level]} 级别的学习内容。"
        elif dir_type == DirectoryType.CONTENT:
            return f"{title} 相关的文档和资料。"
        else:
            return f"{title} 相关内容。"
    
    def list_children(self, dir_info: DirectoryInfo) -> List[ChildItem]:
        """
        列出子项
        
        Args:
            dir_info: 目录信息
            
        Returns:
            子项列表
        """
        children = []
        
        # 添加子目录
        for child_name in dir_info.children:
            child_title = self.extract_title(child_name)
            children.append(ChildItem(
                name=child_name,
                title=child_title,
                path=child_name,
                type="directory"
            ))
        
        # 添加 Markdown 文件
        for md_file in dir_info.markdown_files:
            # 从文件名提取标题（去除 .md 后缀）
            file_title = self.extract_title(md_file.replace('.md', ''))
            children.append(ChildItem(
                name=md_file,
                title=file_title,
                path=md_file,
                type="file"
            ))
        
        return children
