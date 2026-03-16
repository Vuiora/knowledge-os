"""
模板引擎模块
负责根据模板和元数据生成 Markdown 内容
"""

from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
from .models import DirectoryMetadata, DirectoryType, ChildItem
from .logger import logger


class TemplateEngine:
    """模板引擎"""
    
    # 默认模板定义
    DEFAULT_TEMPLATES = {
        DirectoryType.MAIN_LAYER: """---
title: {{title}}
description: {{description}}
---

# {{title}}

{{description}}

## 📚 子主题

{{children}}

## 🎯 学习路径

根据难度级别选择合适的学习内容：
- 🟢 beginner - 入门基础
- 🟡 intermediate - 进阶提升  
- 🔴 advanced - 高级实战

---
*最后更新：{{date}}*
""",
        
        DirectoryType.SUB_TOPIC: """---
title: {{title}}
description: {{description}}
---

# {{title}}

{{description}}

## 📖 内容导航

{{children}}

## 🎓 难度级别

本主题包含不同难度级别的学习内容，请根据自己的水平选择：

{{difficulty_nav}}

---
*最后更新：{{date}}*
""",
        
        DirectoryType.DIFFICULTY: """---
title: {{title}}
description: {{description}}
---

# {{level_indicator}} {{title}}

{{description}}

## 📖 文档列表

{{children}}

## 💡 学习建议

{{learning_tips}}

---
*最后更新：{{date}}*
""",
        
        DirectoryType.CONTENT: """---
title: {{title}}
description: {{description}}
---

# {{title}}

{{description}}

## 文档资源

{{children}}

---
*最后更新：{{date}}*
"""
    }
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化模板引擎
        
        Args:
            template_dir: 自定义模板目录路径（可选）
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self._template_cache: Dict[DirectoryType, str] = {}
        logger.info(f"模板引擎初始化，模板目录: {self.template_dir}")

    
    def load_template(self, template_type: DirectoryType) -> str:
        """
        加载模板内容
        
        优先级：
        1. 缓存中的模板
        2. 自定义模板文件
        3. 默认模板
        
        Args:
            template_type: 模板类型
            
        Returns:
            模板内容字符串
        """
        # 1. 检查缓存
        if template_type in self._template_cache:
            logger.debug(f"从缓存加载模板: {template_type.value}")
            return self._template_cache[template_type]
        
        # 2. 尝试加载自定义模板
        if self.template_dir:
            custom_template = self._load_custom_template(template_type)
            if custom_template:
                self._template_cache[template_type] = custom_template
                return custom_template
        
        # 3. 使用默认模板
        default_template = self.get_default_template(template_type)
        self._template_cache[template_type] = default_template
        return default_template
    
    def _load_custom_template(self, template_type: DirectoryType) -> Optional[str]:
        """
        加载自定义模板文件
        
        Args:
            template_type: 模板类型
            
        Returns:
            模板内容，如果加载失败返回 None
        """
        if not self.template_dir:
            return None
        
        # 构建模板文件路径
        template_filename = f"{template_type.value}.md"
        template_path = self.template_dir / template_filename
        
        try:
            if template_path.exists() and template_path.is_file():
                logger.info(f"加载自定义模板: {template_path}")
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.debug(f"自定义模板不存在: {template_path}")
                return None
        except Exception as e:
            logger.warning(f"加载自定义模板失败: {template_path}, 错误: {e}")
            return None
    
    def get_default_template(self, template_type: DirectoryType) -> str:
        """
        获取默认模板
        
        Args:
            template_type: 模板类型
            
        Returns:
            默认模板内容
        """
        if template_type in self.DEFAULT_TEMPLATES:
            logger.debug(f"使用默认模板: {template_type.value}")
            return self.DEFAULT_TEMPLATES[template_type]
        
        # 如果没有对应的默认模板，返回通用模板
        logger.warning(f"未找到模板类型 {template_type.value} 的默认模板，使用通用模板")
        return """---
title: {{title}}
description: {{description}}
---

# {{title}}

{{description}}

{{children}}

---
*最后更新：{{date}}*
"""
    
    def render(self, metadata: DirectoryMetadata) -> str:
        """
        渲染模板，生成最终的 Markdown 内容
        
        Args:
            metadata: 目录元数据
            
        Returns:
            渲染后的 Markdown 内容
        """
        logger.info(f"渲染模板，类型: {metadata.type.value}, 标题: {metadata.title}")
        
        # 加载模板
        template = self.load_template(metadata.type)
        
        # 准备变量字典
        variables = self._prepare_variables(metadata)
        
        # 执行变量替换
        content = self._substitute_variables(template, variables)
        
        return content
    
    def _prepare_variables(self, metadata: DirectoryMetadata) -> Dict[str, str]:
        """
        准备模板变量
        
        Args:
            metadata: 目录元数据
            
        Returns:
            变量字典
        """
        # 确定难度级别文本
        level_text = ''
        if metadata.type == DirectoryType.DIFFICULTY:
            if 'beginner' in metadata.title.lower():
                level_text = '入门'
            elif 'intermediate' in metadata.title.lower():
                level_text = '进阶'
            elif 'advanced' in metadata.title.lower():
                level_text = '高级'
        
        variables = {
            'title': metadata.title,
            'description': metadata.description,
            'children': self._format_children(metadata.children),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'level_indicator': metadata.level_indicator or '',
            'level': level_text,
            'breadcrumb': ' > '.join(metadata.breadcrumb) if metadata.breadcrumb else '',
        }
        
        # 为不同类型添加特定变量
        if metadata.type == DirectoryType.SUB_TOPIC:
            variables['difficulty_nav'] = self._generate_difficulty_nav(metadata.children)
        
        if metadata.type == DirectoryType.DIFFICULTY:
            variables['learning_tips'] = self._generate_learning_tips(metadata)
        
        return variables
    
    def _substitute_variables(self, template: str, variables: Dict[str, str]) -> str:
        """
        执行变量替换
        
        Args:
            template: 模板字符串
            variables: 变量字典
            
        Returns:
            替换后的字符串
        """
        content = template
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, value)
        
        return content
    
    def _format_children(self, children: list[ChildItem]) -> str:
        """
        格式化子项列表为 Markdown
        
        Args:
            children: 子项列表
            
        Returns:
            格式化后的 Markdown 字符串
        """
        if not children:
            return "*暂无内容*"
        
        lines = []
        for child in children:
            if child.type == "directory":
                # 目录使用文件夹图标
                lines.append(f"- [{child.title}]({child.path}/)")
            else:
                # 文件使用文档图标
                lines.append(f"- [{child.title}]({child.path})")
        
        return '\n'.join(lines)
    
    def _generate_difficulty_nav(self, children: list[ChildItem]) -> str:
        """
        生成难度级别导航
        
        Args:
            children: 子项列表
            
        Returns:
            难度导航 Markdown
        """
        difficulty_map = {
            'beginner': ('🟢', '入门'),
            'intermediate': ('🟡', '进阶'),
            'advanced': ('🔴', '高级')
        }
        
        lines = []
        for level, (icon, label) in difficulty_map.items():
            # 查找对应难度的子目录
            found = False
            for child in children:
                if child.type == "directory" and level in child.name.lower():
                    lines.append(f"- {icon} **{label}**: [{child.title}]({child.path}/)")
                    found = True
                    break
            
            if not found:
                lines.append(f"- {icon} **{label}**: 暂无内容")
        
        return '\n'.join(lines) if lines else "*暂无难度分级*"
    
    def _generate_learning_tips(self, metadata: DirectoryMetadata) -> str:
        """
        生成学习建议
        
        Args:
            metadata: 目录元数据
            
        Returns:
            学习建议文本
        """
        tips_map = {
            'beginner': """
- 建议从基础概念开始学习
- 注重理解核心原理
- 多做练习巩固知识
- 不要急于求成，打好基础很重要
""",
            'intermediate': """
- 在掌握基础的前提下深入学习
- 注重实践和项目经验
- 学习最佳实践和设计模式
- 关注性能优化和代码质量
""",
            'advanced': """
- 深入理解底层原理和实现机制
- 研究源码和高级特性
- 关注架构设计和系统优化
- 积累实战经验，解决复杂问题
"""
        }
        
        # 根据元数据中的难度级别返回对应建议
        for level, tips in tips_map.items():
            if metadata.level_indicator:
                if level in metadata.title.lower():
                    return tips.strip()
        
        return "根据自己的学习进度，循序渐进地掌握相关知识。"
    
    def render_string(self, template_string: str, variables: Dict[str, str]) -> str:
        """
        渲染字符串模板（用于测试和自定义场景）
        
        Args:
            template_string: 模板字符串
            variables: 变量字典
            
        Returns:
            渲染后的字符串
        """
        return self._substitute_variables(template_string, variables)
