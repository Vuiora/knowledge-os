"""
命令行接口模块
提供命令行工具的主要功能
"""

import sys
import argparse
from typing import Optional, List
from pathlib import Path

from .config_manager import ConfigManager
from .scanner import DirectoryScanner
from .analyzer import ContentAnalyzer
from .template_engine import TemplateEngine
from .file_generator import FileGenerator
from .reporter import Reporter
from .pipeline import ProcessingPipeline
from .logger import logger
from .models import DirectoryType, GenerateOptions


class CLI:
    """命令行接口"""
    
    def __init__(self):
        """初始化 CLI"""
        self.config_manager = ConfigManager()
        self.pipeline = None
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        运行 CLI
        
        Args:
            args: 命令行参数列表（用于测试）
            
        Returns:
            int: 退出码（0 表示成功，非 0 表示失败）
        """
        try:
            # 解析命令行参数
            parsed_args = self.parse_arguments(args)
            
            # 加载配置
            config = self.config_manager.load_config(parsed_args.config)
            
            # 配置日志系统
            logger.configure(
                log_level=config.log_level,
                log_file=config.log_file if config.log_file else None
            )
            
            # 初始化处理管道
            template_dir = parsed_args.template_dir if hasattr(parsed_args, 'template_dir') else None
            template_engine = TemplateEngine(template_dir)
            
            self.pipeline = ProcessingPipeline(
                template_engine=template_engine
            )
            
            # 执行命令
            command = parsed_args.command
            exit_code = self.execute_command(command, parsed_args)
            
            return exit_code
        
        except KeyboardInterrupt:
            logger.info("\n操作已取消")
            return 130  # 标准的 Ctrl+C 退出码
        
        except Exception as e:
            logger.error(f"执行命令时发生错误", e)
            return 1
    
    def parse_arguments(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        解析命令行参数
        
        Args:
            args: 命令行参数列表（用于测试）
            
        Returns:
            argparse.Namespace: 解析后的参数
        """
        parser = argparse.ArgumentParser(
            prog='mkdocs-index-generator',
            description='MkDocs Index Generator - 自动生成 MkDocs 文档目录的 index.md 文件',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  # 扫描目录并显示缺失的 index.md
  %(prog)s scan knowledge/
  
  # 生成所有缺失的 index.md 文件
  %(prog)s generate knowledge/
  
  # 预览将要生成的内容
  %(prog)s preview knowledge/
  
  # 使用配置文件
  %(prog)s generate knowledge/ --config config.yml
  
  # 强制覆盖已存在的文件
  %(prog)s generate knowledge/ --force
  
  # 仅生成特定类型的目录
  %(prog)s generate knowledge/ --type difficulty
"""
        )
        
        # 添加子命令
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # scan 命令
        scan_parser = subparsers.add_parser(
            'scan',
            help='扫描目录并显示缺失 index.md 的目录'
        )
        scan_parser.add_argument(
            'root_dir',
            nargs='?',
            default='knowledge',
            help='要扫描的根目录（默认: knowledge）'
        )
        scan_parser.add_argument(
            '--config',
            type=str,
            help='配置文件路径'
        )
        scan_parser.add_argument(
            '--type',
            type=str,
            choices=['main_layer', 'sub_topic', 'difficulty', 'content'],
            help='仅显示特定类型的目录'
        )
        
        # generate 命令
        generate_parser = subparsers.add_parser(
            'generate',
            help='生成缺失的 index.md 文件'
        )
        generate_parser.add_argument(
            'root_dir',
            nargs='?',
            default='knowledge',
            help='要处理的根目录（默认: knowledge）'
        )
        generate_parser.add_argument(
            '--config',
            type=str,
            help='配置文件路径'
        )
        generate_parser.add_argument(
            '--force',
            action='store_true',
            help='强制覆盖已存在的 index.md 文件'
        )
        generate_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，不实际写入文件'
        )
        generate_parser.add_argument(
            '--type',
            type=str,
            choices=['main_layer', 'sub_topic', 'difficulty', 'content'],
            help='仅生成特定类型的目录'
        )
        generate_parser.add_argument(
            '--template-dir',
            type=str,
            help='自定义模板目录路径'
        )
        
        # preview 命令
        preview_parser = subparsers.add_parser(
            'preview',
            help='预览将要生成的 index.md 内容'
        )
        preview_parser.add_argument(
            'root_dir',
            nargs='?',
            default='knowledge',
            help='要预览的根目录（默认: knowledge）'
        )
        preview_parser.add_argument(
            '--config',
            type=str,
            help='配置文件路径'
        )
        preview_parser.add_argument(
            '--type',
            type=str,
            choices=['main_layer', 'sub_topic', 'difficulty', 'content'],
            help='仅预览特定类型的目录'
        )
        preview_parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='限制预览的目录数量（默认: 5）'
        )
        preview_parser.add_argument(
            '--template-dir',
            type=str,
            help='自定义模板目录路径'
        )
        
        # validate 命令
        validate_parser = subparsers.add_parser(
            'validate',
            help='验证现有 index.md 文件的格式'
        )
        validate_parser.add_argument(
            'root_dir',
            nargs='?',
            default='knowledge',
            help='要验证的根目录（默认: knowledge）'
        )
        validate_parser.add_argument(
            '--config',
            type=str,
            help='配置文件路径'
        )
        
        # 解析参数
        if args is None:
            parsed = parser.parse_args()
        else:
            parsed = parser.parse_args(args)
        
        # 如果没有指定命令，显示帮助信息
        if not parsed.command:
            parser.print_help()
            sys.exit(0)
        
        return parsed
    
    def execute_command(self, command: str, args: argparse.Namespace) -> int:
        """
        执行命令
        
        Args:
            command: 命令名称
            args: 解析后的参数
            
        Returns:
            int: 退出码
        """
        try:
            if command == 'scan':
                return self._execute_scan(args)
            elif command == 'generate':
                return self._execute_generate(args)
            elif command == 'preview':
                return self._execute_preview(args)
            elif command == 'validate':
                return self._execute_validate(args)
            else:
                logger.error(f"未知命令: {command}")
                return 1
        
        except Exception as e:
            logger.error(f"执行命令 '{command}' 时发生错误", e)
            return 1
    
    def _execute_scan(self, args: argparse.Namespace) -> int:
        """
        执行 scan 命令
        
        Args:
            args: 命令参数
            
        Returns:
            int: 退出码
        """
        logger.info(f"开始扫描目录: {args.root_dir}")
        
        # 检查根目录是否存在
        root_path = Path(args.root_dir)
        if not root_path.exists():
            logger.error(f"目录不存在: {args.root_dir}")
            return 1
        
        # 获取配置
        config = self.config_manager.get_config()
        excluded_dirs = config.excluded_dirs if config else []
        
        # 类型过滤
        type_filter = None
        if hasattr(args, 'type') and args.type:
            type_filter = DirectoryType(args.type)
        
        # 使用管道扫描
        missing_index = self.pipeline.scan_only(
            args.root_dir,
            excluded_dirs,
            type_filter
        )
        
        # 显示结果
        print(f"\n扫描完成:")
        print(f"  缺失 index.md: {len(missing_index)}")
        
        if missing_index:
            print(f"\n缺失 index.md 的目录:")
            for dir_info in missing_index:
                metadata, _ = self.pipeline.preview_directory(dir_info)
                print(f"  • {dir_info.path} [{metadata.type.value}]")
        
        return 0
    
    def _execute_generate(self, args: argparse.Namespace) -> int:
        """
        执行 generate 命令
        
        Args:
            args: 命令参数
            
        Returns:
            int: 退出码
        """
        logger.info(f"开始生成 index.md 文件: {args.root_dir}")
        
        # 检查根目录是否存在
        root_path = Path(args.root_dir)
        if not root_path.exists():
            logger.error(f"目录不存在: {args.root_dir}")
            return 1
        
        # 获取配置
        config = self.config_manager.get_config()
        excluded_dirs = config.excluded_dirs if config else []
        
        # 准备生成选项
        options = GenerateOptions(
            force_overwrite=args.force if hasattr(args, 'force') else False,
            create_backup=config.create_backup if config else True,
            dry_run=args.dry_run if hasattr(args, 'dry_run') else False
        )
        
        # 类型过滤
        type_filter = None
        if hasattr(args, 'type') and args.type:
            type_filter = DirectoryType(args.type)
        
        # 进度回调
        def progress_callback(current, total, message):
            if current <= 4:
                # 阶段进度
                print(f"[{current}/4] {message}")
            else:
                # 文件处理进度
                print(f"处理进度: [{current}/{total}] {message}")
        
        # 使用管道处理
        summary = self.pipeline.process(
            args.root_dir,
            excluded_dirs,
            options,
            type_filter,
            progress_callback
        )
        
        # 打印报告
        self.pipeline.reporter.print_report(summary)
        
        # 返回退出码
        return 0 if summary.failed == 0 else 1
    
    def _execute_preview(self, args: argparse.Namespace) -> int:
        """
        执行 preview 命令
        
        Args:
            args: 命令参数
            
        Returns:
            int: 退出码
        """
        logger.info(f"预览 index.md 内容: {args.root_dir}")
        
        # 检查根目录是否存在
        root_path = Path(args.root_dir)
        if not root_path.exists():
            logger.error(f"目录不存在: {args.root_dir}")
            return 1
        
        # 获取配置
        config = self.config_manager.get_config()
        excluded_dirs = config.excluded_dirs if config else []
        
        # 类型过滤
        type_filter = None
        if hasattr(args, 'type') and args.type:
            type_filter = DirectoryType(args.type)
        
        # 使用管道扫描
        missing_index = self.pipeline.scan_only(
            args.root_dir,
            excluded_dirs,
            type_filter
        )
        
        if not missing_index:
            logger.warning("未找到缺失 index.md 的目录")
            return 0
        
        # 限制预览数量
        limit = args.limit if hasattr(args, 'limit') else 5
        preview_dirs = missing_index[:limit]
        
        # 显示预览
        print(f"\n预览 index.md 内容 (显示前 {len(preview_dirs)} 个):")
        print("=" * 80)
        
        for i, dir_info in enumerate(preview_dirs, 1):
            try:
                # 使用管道预览
                metadata, content = self.pipeline.preview_directory(dir_info)
                
                # 显示预览
                print(f"\n[{i}] 目录: {dir_info.path}")
                print(f"    类型: {metadata.type.value}")
                print(f"    标题: {metadata.title}")
                print("\n内容预览:")
                print("-" * 80)
                # 只显示前 20 行
                lines = content.split('\n')
                preview_lines = lines[:20]
                print('\n'.join(preview_lines))
                if len(lines) > 20:
                    print(f"\n... (还有 {len(lines) - 20} 行)")
                print("-" * 80)
                
            except Exception as e:
                logger.error(f"预览目录失败: {dir_info.path}", e)
        
        if len(missing_index) > limit:
            print(f"\n还有 {len(missing_index) - limit} 个目录未显示")
        
        return 0
    
    def _execute_validate(self, args: argparse.Namespace) -> int:
        """
        执行 validate 命令
        
        Args:
            args: 命令参数
            
        Returns:
            int: 退出码
        """
        logger.info(f"验证 index.md 文件: {args.root_dir}")
        
        # 检查根目录是否存在
        root_path = Path(args.root_dir)
        if not root_path.exists():
            logger.error(f"目录不存在: {args.root_dir}")
            return 1
        
        # 获取配置
        config = self.config_manager.get_config()
        excluded_dirs = config.excluded_dirs if config else []
        
        # 扫描所有目录（包括有 index.md 的）
        from .scanner import DirectoryScanner
        scanner = DirectoryScanner()
        directories = scanner.scan(args.root_dir, excluded_dirs)
        
        if not directories:
            logger.warning("未找到任何目录")
            return 0
        
        # 过滤有 index.md 的目录
        with_index = [d for d in directories if d.has_index]
        
        # 验证每个 index.md 文件
        valid_count = 0
        invalid_count = 0
        all_issues = []
        
        for dir_info in with_index:
            is_valid, issues = self.pipeline.validate_directory(dir_info.path)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                for issue in issues:
                    all_issues.append(f"{dir_info.path}: {issue}")
        
        # 显示结果
        print(f"\n验证完成:")
        print(f"  总文件数: {len(with_index)}")
        print(f"  有效: {valid_count}")
        print(f"  无效: {invalid_count}")
        
        if all_issues:
            print(f"\n发现的问题:")
            for issue in all_issues:
                print(f"  • {issue}")
        
        return 0 if invalid_count == 0 else 1


def main():
    """主入口函数"""
    cli = CLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
