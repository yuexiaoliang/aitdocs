import os
import fnmatch
from typing import List, Optional
import hashlib


class IgnorePatternManager:
    """管理忽略模式的类"""
    
    def __init__(self, directory_path: str, ignore_patterns: Optional[List[str]] = None):
        """
        初始化忽略模式管理器
        
        Args:
            directory_path: 目录路径
            ignore_patterns: 命令行传入的忽略模式列表
        """
        self.directory_path = directory_path
        self.ignore_patterns = self._process_ignore_patterns(ignore_patterns or [])
        
    def _process_ignore_patterns(self, ignore_patterns: List[str]) -> List[str]:
        """
        预处理忽略模式列表，统一添加默认忽略规则和从文件读取的规则
        
        Args:
            ignore_patterns: 忽略模式列表
            
        Returns:
            处理后的忽略模式列表
        """
        # 添加默认忽略的目录和文件
        default_ignores = ['.git', '.venv', '__pycache__', '*.py', '*.pyc', '*.pyo', '*.pyd']
        processed_ignore_patterns = ignore_patterns + default_ignores
        
        # 读取.gitignore文件中的忽略规则
        gitignore_path = os.path.join(self.directory_path, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        processed_ignore_patterns.append(line)
        
        # 读取.aitdocsignore文件中的忽略规则
        aitdocsignore_path = os.path.join(self.directory_path, '.aitdocsignore')
        if os.path.exists(aitdocsignore_path):
            with open(aitdocsignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        processed_ignore_patterns.append(line)
        
        return processed_ignore_patterns
    
    def should_ignore(self, path: str, is_dir: bool = False) -> bool:
        """
        判断路径是否应该被忽略
        
        Args:
            path: 路径
            is_dir: 是否为目录
            
        Returns:
            是否应该忽略
        """
        for pattern in self.ignore_patterns:
            # 处理目录特定模式
            if pattern.endswith('/') or pattern.endswith('\\'):
                if not is_dir:
                    continue
                dir_pattern = pattern.rstrip('/\\')
                if fnmatch.fnmatch(path, dir_pattern) or \
                   fnmatch.fnmatch(os.path.basename(path), dir_pattern):
                    return True
            # 处理文件特定模式
            elif is_dir:
                # 目录不匹配文件模式
                continue
            # 处理通用模式
            elif fnmatch.fnmatch(path, pattern) or \
                 fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
        return False
    
    def get_ignore_hash(self) -> str:
        """
        计算忽略规则的哈希值
        
        Returns:
            忽略规则的哈希值
        """
        # 对忽略规则进行排序以确保一致性
        sorted_patterns = sorted(self.ignore_patterns)
        
        # 计算哈希值
        ignore_str = '\n'.join(sorted_patterns)
        return hashlib.md5(ignore_str.encode('utf-8')).hexdigest()
    
    def get_processed_patterns(self) -> List[str]:
        """
        获取处理后的忽略模式列表
        
        Returns:
            处理后的忽略模式列表
        """
        return self.ignore_patterns.copy()