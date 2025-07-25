import subprocess
import json
import os
from typing import List, Optional


class GitManager:
    """Git操作管理器，负责处理与Git相关的所有操作"""
    
    def __init__(self, directory_path: str):
        """
        初始化Git管理器
        
        Args:
            directory_path: Git仓库路径
        """
        self.directory_path = directory_path
        self.state_file = os.path.join(directory_path, '.aitdocs_state')
    
    def get_current_commit_hash(self) -> Optional[str]:
        """
        获取当前Git提交哈希
        
        Returns:
            当前提交哈希，如果失败则返回None
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.directory_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def get_changed_files(self, last_commit: str, current_commit: str) -> List[str]:
        """
        获取两个提交之间变更的文件列表
        
        Args:
            last_commit: 上次提交哈希
            current_commit: 当前提交哈希
            
        Returns:
            变更的文件列表
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', last_commit, current_commit],
                cwd=self.directory_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = result.stdout.strip().split('\n')
            return [f for f in changed_files if f]  # 移除空行
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"执行Git diff时出错: {e}")
    
    def commit_files(self, files: List[str], commit_message: str) -> bool:
        """
        将文件提交到Git仓库
        
        Args:
            files: 要提交的文件列表
            commit_message: 提交信息
            
        Returns:
            是否提交成功
        """
        try:
            # 添加文件到Git暂存区
            for file_path in files:
                relative_path = os.path.relpath(file_path, self.directory_path)
                subprocess.run(
                    ['git', 'add', relative_path],
                    cwd=self.directory_path,
                    check=True,
                    capture_output=True
                )
            
            # 提交文件
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.directory_path,
                check=True,
                capture_output=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git提交失败: {e}")
    
    def push_to_remote(self) -> None:
        """
        推送提交到远程仓库
        """
        try:
            subprocess.run(
                ['git', 'push'],
                cwd=self.directory_path,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git推送失败: {e}")
    
    def get_last_state(self) -> Optional[dict]:
        """
        获取上次翻译时保存的状态
        
        Returns:
            上次翻译时的状态，如果不存在则返回None
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                return None
        return None
    
    def save_state(self, commit_hash: str, ignore_hash: str) -> None:
        """
        保存当前状态到状态文件
        
        Args:
            commit_hash: 当前提交哈希
            ignore_hash: 忽略规则哈希
        """
        state = {}
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            except json.JSONDecodeError:
                pass
        
        state['last_commit_hash'] = commit_hash
        state['ignore_hash'] = ignore_hash
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            raise Exception(f"无法保存状态文件: {e}")