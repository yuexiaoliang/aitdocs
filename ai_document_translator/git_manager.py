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
    
    def _run_git_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """
        执行Git命令
        
        Args:
            command: Git命令参数列表
            
        Returns:
            命令执行结果
        """
        try:
            return subprocess.run(
                command,
                cwd=self.directory_path,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git命令执行失败: {' '.join(command)}: {e.stderr.strip()}")
    
    def get_current_commit_hash(self) -> Optional[str]:
        """
        获取当前Git提交哈希
        
        Returns:
            当前提交哈希，如果失败则返回None
        """
        try:
            result = self._run_git_command(['git', 'rev-parse', 'HEAD'])
            return result.stdout.strip()
        except (Exception, FileNotFoundError):
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
            # 验证提交哈希是否存在
            self._run_git_command(['git', 'cat-file', '-e', f'{last_commit}^{{commit}}'])
            self._run_git_command(['git', 'cat-file', '-e', f'{current_commit}^{{commit}}'])
            
            result = self._run_git_command(['git', 'diff', '--name-only', last_commit, current_commit])
            
            changed_files = result.stdout.strip().split('\n')
            return [f for f in changed_files if f]  # 移除空行
            
        except Exception as e:
            raise Exception(f"执行Git diff时出错: {e}")
    
    def _add_files_to_git(self, files: List[str]) -> None:
        """
        将文件添加到Git中
        
        Args:
            files: 要添加到Git的文件列表
        """
        for file_path in files:
            try:
                relative_path = os.path.relpath(file_path, self.directory_path)
                self._run_git_command(['git', 'add', relative_path])
            except Exception:
                # 如果添加失败，忽略错误
                pass
    
    def _add_state_file_to_git(self) -> None:
        """
        将状态文件添加到Git中
        """
        if os.path.exists(self.state_file):
            self._add_files_to_git([self.state_file])
    
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
            self._add_files_to_git(files)
            
            # 如果状态文件存在，也将其添加到暂存区
            self._add_state_file_to_git()
            
            # 提交文件
            self._run_git_command(['git', 'commit', '-m', commit_message])
            
            return True
            
        except Exception as e:
            raise Exception(f"Git提交失败: {e}")
    
    def push_to_remote(self) -> None:
        """
        推送提交到远程仓库
        """
        try:
            self._run_git_command(['git', 'push'])
        except Exception as e:
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
                
            # 将状态文件添加到git中（如果还没有被跟踪）
            self._add_state_file_to_git()
        except Exception as e:
            raise Exception(f"无法保存状态文件: {e}")