"""
文件生成器模块
负责将生成的内容写入文件系统
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from .models import GenerateOptions, GenerateResult
from .logger import logger


class FileGenerator:
    """文件生成器 - 负责将内容写入文件系统"""
    
    def __init__(self):
        """初始化文件生成器"""
        self.logger = logger
    
    def generate(
        self, 
        path: str, 
        content: str, 
        options: Optional[GenerateOptions] = None
    ) -> GenerateResult:
        """
        生成 index.md 文件
        
        Args:
            path: 目标目录路径
            content: 要写入的内容
            options: 生成选项
            
        Returns:
            GenerateResult: 生成结果
        """
        if options is None:
            options = GenerateOptions()
        
        try:
            # 验证目标目录
            if not self.validate_path(path):
                return GenerateResult(
                    success=False,
                    path=path,
                    action="failed",
                    message=f"目标目录不存在或不可访问: {path}",
                    timestamp=datetime.now()
                )
            
            index_path = Path(path) / "index.md"
            
            # 预览模式：不写入文件
            if options.dry_run:
                self.logger.info(f"[预览模式] 将生成文件: {index_path}")
                return GenerateResult(
                    success=True,
                    path=str(index_path),
                    action="preview",
                    message=f"预览模式 - 将生成文件: {index_path}",
                    timestamp=datetime.now()
                )
            
            # 检查文件是否已存在
            if index_path.exists():
                if not options.force_overwrite:
                    # 默认跳过已存在的文件
                    self.logger.info(f"跳过已存在的文件: {index_path}")
                    return GenerateResult(
                        success=True,
                        path=str(index_path),
                        action="skipped",
                        message=f"文件已存在，跳过: {index_path}",
                        timestamp=datetime.now()
                    )
                else:
                    # 强制覆盖模式：创建备份
                    if options.create_backup:
                        if not self.create_backup(str(index_path)):
                            self.logger.warning(f"无法创建备份文件: {index_path}")
                    
                    # 写入文件
                    if self.write_file(str(index_path), content):
                        self.logger.info(f"覆盖文件: {index_path}")
                        return GenerateResult(
                            success=True,
                            path=str(index_path),
                            action="overwritten",
                            message=f"成功覆盖文件: {index_path}",
                            timestamp=datetime.now()
                        )
                    else:
                        return GenerateResult(
                            success=False,
                            path=str(index_path),
                            action="failed",
                            message=f"写入文件失败: {index_path}",
                            timestamp=datetime.now()
                        )
            else:
                # 文件不存在，直接创建
                if self.write_file(str(index_path), content):
                    self.logger.info(f"创建文件: {index_path}")
                    return GenerateResult(
                        success=True,
                        path=str(index_path),
                        action="created",
                        message=f"成功创建文件: {index_path}",
                        timestamp=datetime.now()
                    )
                else:
                    return GenerateResult(
                        success=False,
                        path=str(index_path),
                        action="failed",
                        message=f"创建文件失败: {index_path}",
                        timestamp=datetime.now()
                    )
        
        except Exception as e:
            self.logger.error(f"生成文件时发生错误: {path}", e)
            return GenerateResult(
                success=False,
                path=path,
                action="failed",
                message=f"生成文件时发生错误: {str(e)}",
                timestamp=datetime.now()
            )
    
    def validate_path(self, path: str) -> bool:
        """
        验证目标目录是否存在且可写
        
        Args:
            path: 目录路径
            
        Returns:
            bool: 是否有效
        """
        try:
            dir_path = Path(path)
            
            # 检查目录是否存在
            if not dir_path.exists():
                self.logger.error(f"目录不存在: {path}")
                return False
            
            # 检查是否是目录
            if not dir_path.is_dir():
                self.logger.error(f"路径不是目录: {path}")
                return False
            
            # 检查是否可写
            if not os.access(path, os.W_OK):
                self.logger.error(f"目录不可写: {path}")
                return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"验证路径时发生错误: {path}", e)
            return False
    
    def write_file(self, path: str, content: str) -> bool:
        """
        写入文件到磁盘
        
        Args:
            path: 文件路径
            content: 文件内容
            
        Returns:
            bool: 是否成功
        """
        try:
            file_path = Path(path)
            
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"成功写入文件: {path}")
            return True
        
        except PermissionError:
            self.logger.error(f"权限不足，无法写入文件: {path}")
            return False
        
        except OSError as e:
            self.logger.error(f"文件系统错误: {path}", e)
            return False
        
        except Exception as e:
            self.logger.error(f"写入文件时发生未知错误: {path}", e)
            return False
    
    def create_backup(self, path: str) -> bool:
        """
        创建文件备份
        
        Args:
            path: 原文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在，无需备份: {path}")
                return False
            
            # 生成备份文件名（添加时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.parent / f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
            
            # 复制文件
            shutil.copy2(path, backup_path)
            
            self.logger.info(f"创建备份文件: {backup_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"创建备份文件失败: {path}", e)
            return False
