"""
目录扫描器单元测试
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.scanner import DirectoryScanner
from src.models import DirectoryInfo


class TestDirectoryScanner:
    """测试目录扫描器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.scanner = DirectoryScanner()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """清理测试环境"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_scan_empty_directory(self):
        """测试扫描空目录"""
        results = self.scanner.scan(self.temp_dir, [])
        assert len(results) == 1
        assert results[0].path == self.temp_dir
        assert results[0].children == []
        assert results[0].markdown_files == []
    
    def test_scan_with_subdirectories(self):
        """测试扫描包含子目录的目录"""
        # 创建测试目录结构
        sub1 = Path(self.temp_dir) / "sub1"
        sub2 = Path(self.temp_dir) / "sub2"
        sub1.mkdir()
        sub2.mkdir()
        
        results = self.scanner.scan(self.temp_dir, [])
        assert len(results) == 3  # root + 2 subdirs
        
        # 验证根目录
        root_info = [r for r in results if r.path == self.temp_dir][0]
        assert set(root_info.children) == {"sub1", "sub2"}
    
    def test_has_index(self):
        """测试检测 index.md 文件"""
        # 创建带 index.md 的目录
        test_dir = Path(self.temp_dir) / "with_index"
        test_dir.mkdir()
        (test_dir / "index.md").write_text("# Test")
        
        assert self.scanner.has_index(str(test_dir)) is True
        assert self.scanner.has_index(self.temp_dir) is False
    
    def test_scan_with_markdown_files(self):
        """测试扫描包含 Markdown 文件的目录"""
        # 创建测试文件
        (Path(self.temp_dir) / "file1.md").write_text("# File 1")
        (Path(self.temp_dir) / "file2.md").write_text("# File 2")
        (Path(self.temp_dir) / "index.md").write_text("# Index")
        (Path(self.temp_dir) / "readme.txt").write_text("Not markdown")
        
        results = self.scanner.scan(self.temp_dir, [])
        assert len(results) == 1
        
        # index.md 不应该在 markdown_files 列表中
        assert set(results[0].markdown_files) == {"file1.md", "file2.md"}
        assert results[0].has_index is True
    
    def test_is_excluded(self):
        """测试排除目录判断"""
        excluded = ["node_modules", "_site", ".git"]
        
        assert self.scanner.is_excluded("/path/to/node_modules", excluded) is True
        assert self.scanner.is_excluded("/path/to/project/_site/build", excluded) is True
        assert self.scanner.is_excluded("/path/to/.git", excluded) is True
        assert self.scanner.is_excluded("/path/to/normal", excluded) is False
    
    def test_scan_with_excluded_directories(self):
        """测试扫描时排除指定目录"""
        # 创建目录结构
        normal = Path(self.temp_dir) / "normal"
        excluded = Path(self.temp_dir) / "_site"
        normal.mkdir()
        excluded.mkdir()
        
        # 在排除目录中创建子目录
        (excluded / "subdir").mkdir()
        
        results = self.scanner.scan(self.temp_dir, ["_site"])
        
        # 应该只扫描到 root 和 normal，不包括 _site 及其子目录
        paths = [r.path for r in results]
        assert str(normal) in paths
        assert str(excluded) not in paths
        assert str(excluded / "subdir") not in paths
    
    def test_get_directory_level(self):
        """测试获取目录层级"""
        # 不同深度的路径
        assert self.scanner.get_directory_level("/") == 1
        assert self.scanner.get_directory_level("/home") == 2
        assert self.scanner.get_directory_level("/home/user/docs") == 4
    
    def test_scan_nested_structure(self):
        """测试扫描嵌套目录结构"""
        # 创建嵌套结构
        level1 = Path(self.temp_dir) / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)
        
        results = self.scanner.scan(self.temp_dir, [])
        assert len(results) == 4  # root + 3 levels
        
        # 验证层级关系
        level3_info = [r for r in results if r.name == "level3"][0]
        assert level3_info.children == []
