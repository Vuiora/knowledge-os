"""
报告生成器模块
负责收集生成结果并生成统计报告
"""

import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .models import GenerateResult, ErrorInfo, Summary
from .logger import logger


class Reporter:
    """报告生成器 - 收集结果并生成报告"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.logger = logger
        self.results: List[GenerateResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def start(self):
        """开始记录时间"""
        self.start_time = datetime.now()
        self.results = []
        self.logger.debug("报告生成器已启动")
    
    def add_result(self, result: GenerateResult):
        """
        添加一个生成结果
        
        Args:
            result: 生成结果对象
        """
        self.results.append(result)
        self.logger.debug(f"添加结果: {result.path} - {result.action}")
    
    def stop(self):
        """停止记录时间"""
        self.end_time = datetime.now()
        self.logger.debug("报告生成器已停止")

    def generate_summary(self, total_scanned: int = 0, missing_index: int = 0) -> Summary:
        """
        生成执行摘要
        
        Args:
            total_scanned: 扫描的目录总数
            missing_index: 缺失 index.md 的目录数量
            
        Returns:
            Summary: 执行摘要对象
        """
        if self.start_time is None:
            self.start_time = datetime.now()
        
        if self.end_time is None:
            self.end_time = datetime.now()
        
        # 计算统计数据
        generated = sum(1 for r in self.results if r.success and r.action in ["created", "overwritten"])
        skipped = sum(1 for r in self.results if r.action == "skipped")
        failed = sum(1 for r in self.results if not r.success)
        
        # 收集错误信息
        errors = []
        for result in self.results:
            if not result.success:
                errors.append(ErrorInfo(
                    path=result.path,
                    error_type="generation_failed",
                    message=result.message,
                    timestamp=result.timestamp
                ))
        
        # 计算执行时长
        duration = (self.end_time - self.start_time).total_seconds()
        
        summary = Summary(
            total_scanned=total_scanned,
            missing_index=missing_index,
            generated=generated,
            skipped=skipped,
            failed=failed,
            duration=duration,
            errors=errors
        )
        
        self.logger.debug(f"生成摘要: 成功={generated}, 跳过={skipped}, 失败={failed}")
        return summary

    def print_report(self, summary: Summary, format: str = "text"):
        """
        打印报告
        
        Args:
            summary: 执行摘要
            format: 报告格式 ("text" 或 "json")
        """
        if format == "json":
            self._print_json_report(summary)
        else:
            self._print_text_report(summary)
    
    def _print_text_report(self, summary: Summary):
        """
        打印文本格式报告
        
        Args:
            summary: 执行摘要
        """
        print("\n" + "=" * 60)
        print("MkDocs Index Generator - 执行报告")
        print("=" * 60)
        print(f"\n📊 统计信息:")
        print(f"  • 扫描目录总数: {summary.total_scanned}")
        print(f"  • 缺失 index.md: {summary.missing_index}")
        print(f"  • 成功生成: {summary.generated}")
        print(f"  • 跳过: {summary.skipped}")
        print(f"  • 失败: {summary.failed}")
        print(f"  • 执行时长: {summary.duration:.2f} 秒")
        
        # 显示错误详情
        if summary.errors:
            print(f"\n❌ 错误详情 ({len(summary.errors)} 个):")
            for i, error in enumerate(summary.errors, 1):
                print(f"\n  {i}. 路径: {error.path}")
                print(f"     类型: {error.error_type}")
                print(f"     消息: {error.message}")
                print(f"     时间: {error.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "=" * 60)
        
        # 记录到日志
        self.logger.info(f"报告生成完成 - 成功: {summary.generated}, 失败: {summary.failed}")

    def _print_json_report(self, summary: Summary):
        """
        打印 JSON 格式报告
        
        Args:
            summary: 执行摘要
        """
        report = {
            "summary": {
                "total_scanned": summary.total_scanned,
                "missing_index": summary.missing_index,
                "generated": summary.generated,
                "skipped": summary.skipped,
                "failed": summary.failed,
                "duration": summary.duration
            },
            "errors": [
                {
                    "path": error.path,
                    "error_type": error.error_type,
                    "message": error.message,
                    "timestamp": error.timestamp.isoformat()
                }
                for error in summary.errors
            ],
            "results": [
                {
                    "path": result.path,
                    "action": result.action,
                    "success": result.success,
                    "message": result.message,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.results
            ]
        }
        
        print(json.dumps(report, ensure_ascii=False, indent=2))
        self.logger.info("JSON 格式报告生成完成")
    
    def save_report(self, summary: Summary, output_path: str, format: str = "json"):
        """
        保存报告到文件
        
        Args:
            summary: 执行摘要
            output_path: 输出文件路径
            format: 报告格式 ("text" 或 "json")
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "json":
                report = {
                    "summary": {
                        "total_scanned": summary.total_scanned,
                        "missing_index": summary.missing_index,
                        "generated": summary.generated,
                        "skipped": summary.skipped,
                        "failed": summary.failed,
                        "duration": summary.duration
                    },
                    "errors": [
                        {
                            "path": error.path,
                            "error_type": error.error_type,
                            "message": error.message,
                            "timestamp": error.timestamp.isoformat()
                        }
                        for error in summary.errors
                    ]
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
            else:
                # 文本格式
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("MkDocs Index Generator - 执行报告\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"统计信息:\n")
                    f.write(f"  扫描目录总数: {summary.total_scanned}\n")
                    f.write(f"  缺失 index.md: {summary.missing_index}\n")
                    f.write(f"  成功生成: {summary.generated}\n")
                    f.write(f"  跳过: {summary.skipped}\n")
                    f.write(f"  失败: {summary.failed}\n")
                    f.write(f"  执行时长: {summary.duration:.2f} 秒\n")
                    
                    if summary.errors:
                        f.write(f"\n错误详情 ({len(summary.errors)} 个):\n")
                        for i, error in enumerate(summary.errors, 1):
                            f.write(f"\n  {i}. 路径: {error.path}\n")
                            f.write(f"     类型: {error.error_type}\n")
                            f.write(f"     消息: {error.message}\n")
                            f.write(f"     时间: {error.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            self.logger.info(f"报告已保存到: {output_path}")
        
        except Exception as e:
            self.logger.error(f"保存报告失败: {output_path}", e)
