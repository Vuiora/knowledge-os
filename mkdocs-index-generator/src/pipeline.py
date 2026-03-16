"""
处理管道模块
负责协调所有模块，实现完整的端到端处理流程
"""

from typing import List, Optional, Callable
from pathlib import Path

from .models import (
    DirectoryInfo, 
    DirectoryMetadata, 
    GenerateOptions, 
    GenerateResult,
    Summary,
    DirectoryType
)
from .scanner import DirectoryScanner
from .analyzer import ContentAnalyzer
from .template_engine import TemplateEngine
from .file_generator import FileGenerator
from .reporter import Reporter
from .logger import logger


class ProcessingPipeline:
    """
    处理管道 - 协调扫描、分析、模板渲染和文件生成的完整流程
    """
    
    def __init__(
        self,
        scanner: Optional[DirectoryScanner] = None,
        analyzer: Optional[ContentAnalyzer] = None,
        template_engine: Optional[TemplateEngine] = None,
        file_generator: Optional[FileGenerator] = None,
        reporter: Optional[Reporter] = None
    ):
        """
        初始化处理管道
        
        Args:
            scanner: 目录扫描器（可选，默认创建新实例）
            analyzer: 内容分析器（可选，默认创建新实例）
            template_engine: 模板引擎（可选，默认创建新实例）
            file_generator: 文件生成器（可选，默认创建新实例）
            reporter: 报告生成器（可选，默认创建新实例）
        """
        self.scanner = scanner or DirectoryScanner()
        self.analyzer = analyzer or ContentAnalyzer()
        self.template_engine = template_engine or TemplateEngine()
        self.file_generator = file_generator or FileGenerator()
        self.reporter = reporter or Reporter()
        
        logger.info("处理管道已初始化")
    
    def process(
        self,
        root_dir: str,
        excluded_dirs: List[str],
        options: Optional[GenerateOptions] = None,
        type_filter: Optional[DirectoryType] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        error_recovery: bool = True
    ) -> Summary:
        """
        执行完整的处理流程（批量处理）
        
        Args:
            root_dir: 根目录路径
            excluded_dirs: 排除的目录列表
            options: 生成选项
            type_filter: 目录类型过滤器（可选）
            progress_callback: 进度回调函数 (current, total, message)
            error_recovery: 是否启用错误恢复（单个失败不影响其他）
            
        Returns:
            Summary: 执行摘要
        """
        if options is None:
            options = GenerateOptions()
        
        logger.info(f"开始批量处理: {root_dir}")
        logger.info(f"错误恢复模式: {'启用' if error_recovery else '禁用'}")
        self.reporter.start()
        
        try:
            # 阶段 1: 扫描目录
            logger.info("阶段 1/4: 扫描目录结构")
            if progress_callback:
                progress_callback(1, 4, "扫描目录结构")
            
            directories = self.scanner.scan(root_dir, excluded_dirs)
            
            if not directories:
                logger.warning("未找到任何目录")
                self.reporter.stop()
                return self.reporter.generate_summary(0, 0)
            
            # 过滤缺失 index.md 的目录
            missing_index = [d for d in directories if not d.has_index]
            logger.info(f"找到 {len(directories)} 个目录，其中 {len(missing_index)} 个缺失 index.md")
            
            # 阶段 2: 分析和过滤
            logger.info("阶段 2/4: 分析目录类型")
            if progress_callback:
                progress_callback(2, 4, "分析目录类型")
            
            # 如果指定了类型过滤，进行过滤
            if type_filter:
                filtered_dirs = []
                for dir_info in missing_index:
                    try:
                        metadata = self.analyzer.analyze(dir_info)
                        if metadata.type == type_filter:
                            filtered_dirs.append(dir_info)
                    except Exception as e:
                        if error_recovery:
                            logger.warning(f"分析目录失败，跳过: {dir_info.path}", e)
                        else:
                            raise
                missing_index = filtered_dirs
                logger.info(f"类型过滤后剩余 {len(missing_index)} 个目录")
            
            # 阶段 3: 批量生成内容
            logger.info("阶段 3/4: 批量生成 index.md 内容")
            if progress_callback:
                progress_callback(3, 4, "批量生成 index.md 内容")
            
            total = len(missing_index)
            success_count = 0
            failed_count = 0
            
            for i, dir_info in enumerate(missing_index, 1):
                try:
                    # 更新进度
                    if progress_callback:
                        progress_callback(
                            i, 
                            total, 
                            f"处理 {dir_info.path} ({success_count} 成功, {failed_count} 失败)"
                        )
                    
                    # 处理单个目录
                    result = self._process_directory(dir_info, options)
                    self.reporter.add_result(result)
                    
                    if result.success:
                        success_count += 1
                    else:
                        failed_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"处理目录失败: {dir_info.path}", e)
                    
                    # 创建失败结果
                    from datetime import datetime
                    result = GenerateResult(
                        success=False,
                        path=dir_info.path,
                        action="failed",
                        message=f"处理失败: {str(e)}",
                        timestamp=datetime.now()
                    )
                    self.reporter.add_result(result)
                    
                    # 如果不启用错误恢复，立即终止
                    if not error_recovery:
                        logger.error("错误恢复已禁用，终止批量处理")
                        break
            
            # 阶段 4: 生成报告
            logger.info("阶段 4/4: 生成执行报告")
            if progress_callback:
                progress_callback(4, 4, "生成执行报告")
            
            self.reporter.stop()
            summary = self.reporter.generate_summary(
                total_scanned=len(directories),
                missing_index=len(missing_index)
            )
            
            logger.info(f"批量处理完成: 成功 {summary.generated}, 跳过 {summary.skipped}, 失败 {summary.failed}")
            return summary
        
        except Exception as e:
            logger.error("批量处理管道执行失败", e)
            self.reporter.stop()
            return self.reporter.generate_summary(0, 0)
    
    def _process_directory(
        self, 
        dir_info: DirectoryInfo, 
        options: GenerateOptions
    ) -> GenerateResult:
        """
        处理单个目录
        
        Args:
            dir_info: 目录信息
            options: 生成选项
            
        Returns:
            GenerateResult: 生成结果
        """
        logger.debug(f"处理目录: {dir_info.path}")
        
        # 1. 分析目录，提取元数据
        metadata = self.analyzer.analyze(dir_info)
        logger.debug(f"目录类型: {metadata.type.value}, 标题: {metadata.title}")
        
        # 2. 渲染模板，生成内容
        content = self.template_engine.render(metadata)
        logger.debug(f"内容已生成，长度: {len(content)} 字符")
        
        # 3. 写入文件
        result = self.file_generator.generate(dir_info.path, content, options)
        logger.debug(f"文件生成结果: {result.action}")
        
        return result
    
    def process_batch(
        self,
        directories: List[DirectoryInfo],
        options: Optional[GenerateOptions] = None,
        batch_size: int = 10,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Summary:
        """
        批量处理目录列表（支持分批处理）
        
        Args:
            directories: 要处理的目录列表
            options: 生成选项
            batch_size: 批次大小（每批处理的目录数）
            progress_callback: 进度回调函数
            
        Returns:
            Summary: 执行摘要
        """
        if options is None:
            options = GenerateOptions()
        
        logger.info(f"开始批量处理 {len(directories)} 个目录，批次大小: {batch_size}")
        self.reporter.start()
        
        total = len(directories)
        processed = 0
        
        # 分批处理
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch = directories[batch_start:batch_end]
            
            logger.info(f"处理批次 {batch_start // batch_size + 1}: 目录 {batch_start + 1}-{batch_end}")
            
            for dir_info in batch:
                processed += 1
                
                try:
                    if progress_callback:
                        progress_callback(
                            processed,
                            total,
                            f"处理 {dir_info.path}"
                        )
                    
                    result = self._process_directory(dir_info, options)
                    self.reporter.add_result(result)
                    
                except Exception as e:
                    logger.error(f"处理目录失败: {dir_info.path}", e)
                    from datetime import datetime
                    result = GenerateResult(
                        success=False,
                        path=dir_info.path,
                        action="failed",
                        message=f"处理失败: {str(e)}",
                        timestamp=datetime.now()
                    )
                    self.reporter.add_result(result)
        
        self.reporter.stop()
        summary = self.reporter.generate_summary(
            total_scanned=total,
            missing_index=total
        )
        
        logger.info(f"批量处理完成: 成功 {summary.generated}, 跳过 {summary.skipped}, 失败 {summary.failed}")
        return summary
    
    def scan_only(
        self,
        root_dir: str,
        excluded_dirs: List[str],
        type_filter: Optional[DirectoryType] = None
    ) -> List[DirectoryInfo]:
        """
        仅扫描目录，不生成文件
        
        Args:
            root_dir: 根目录路径
            excluded_dirs: 排除的目录列表
            type_filter: 目录类型过滤器（可选）
            
        Returns:
            List[DirectoryInfo]: 缺失 index.md 的目录列表
        """
        logger.info(f"扫描目录: {root_dir}")
        
        # 扫描目录
        directories = self.scanner.scan(root_dir, excluded_dirs)
        
        # 过滤缺失 index.md 的目录
        missing_index = [d for d in directories if not d.has_index]
        
        # 如果指定了类型过滤
        if type_filter:
            filtered_dirs = []
            for dir_info in missing_index:
                metadata = self.analyzer.analyze(dir_info)
                if metadata.type == type_filter:
                    filtered_dirs.append(dir_info)
            missing_index = filtered_dirs
        
        logger.info(f"找到 {len(missing_index)} 个缺失 index.md 的目录")
        return missing_index
    
    def preview_directory(
        self,
        dir_info: DirectoryInfo
    ) -> tuple[DirectoryMetadata, str]:
        """
        预览单个目录的生成内容
        
        Args:
            dir_info: 目录信息
            
        Returns:
            tuple: (元数据, 生成的内容)
        """
        logger.debug(f"预览目录: {dir_info.path}")
        
        # 分析目录
        metadata = self.analyzer.analyze(dir_info)
        
        # 渲染模板
        content = self.template_engine.render(metadata)
        
        return metadata, content
    
    def validate_directory(
        self,
        dir_path: str
    ) -> tuple[bool, List[str]]:
        """
        验证目录的 index.md 文件
        
        Args:
            dir_path: 目录路径
            
        Returns:
            tuple: (是否有效, 问题列表)
        """
        index_path = Path(dir_path) / "index.md"
        issues = []
        
        if not index_path.exists():
            issues.append("index.md 文件不存在")
            return False, issues
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查 YAML front matter
            if not content.startswith('---'):
                issues.append("缺少 YAML front matter")
            else:
                # 检查必需字段
                lines = content.split('\n')
                has_title = any('title:' in line for line in lines[:10])
                has_description = any('description:' in line for line in lines[:10])
                
                if not has_title:
                    issues.append("缺少 title 字段")
                if not has_description:
                    issues.append("缺少 description 字段")
            
            # 检查 Markdown 语法（简单检查）
            if '# ' not in content:
                issues.append("缺少主标题")
            
            is_valid = len(issues) == 0
            return is_valid, issues
        
        except Exception as e:
            issues.append(f"读取文件失败: {str(e)}")
            return False, issues
