import subprocess
import os
from typing import List, Optional
from .state_manager import StateManager


class GitManager:
    """Git操作管理器，负责处理与Git相关的所有操作"""

    def __init__(self, directory_path: str):
        """
        初始化Git管理器

        Args:
            directory_path: Git仓库路径
        """
        self.directory_path = directory_path
        self.state_manager = StateManager(directory_path)

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
                check=True,
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
            result = self._run_git_command(["git", "rev-parse", "HEAD"])
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
            self._run_git_command(
                ["git", "cat-file", "-e", f"{last_commit}^{{commit}}"]
            )
            self._run_git_command(
                ["git", "cat-file", "-e", f"{current_commit}^{{commit}}"]
            )

            result = self._run_git_command(
                ["git", "diff", "--name-only", last_commit, current_commit]
            )

            result = result.stdout.strip()
            print(f"git diff result: {result}", end="\n")

            changed_files = result.split("\n")
            return [f for f in changed_files if f]  # 移除空行

        except Exception:
            # 如果任何一步失败，返回空列表表示无法获取变更文件
            # 这种情况下应该进行全量翻译
            return []

    def _add_files_to_git(self, files: List[str]) -> None:
        """
        将文件添加到Git中

        Args:
            files: 要添加到Git的文件列表
        """
        for file_path in files:
            try:
                relative_path = os.path.relpath(file_path, self.directory_path)
                self._run_git_command(["git", "add", relative_path])
            except Exception:
                # 如果添加失败，忽略错误
                pass

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

            # 提交文件
            self._run_git_command(["git", "commit", "-m", commit_message])

            return True

        except Exception as e:
            raise Exception(f"Git提交失败: {e}")

    def commit_state_file(self) -> None:
        """
        提交状态文件到Git仓库
        """
        state_file_path = self.state_manager.get_state_file_path()
        self.commit_files([state_file_path], "Update state file")

    def commit_cache_files(self) -> None:
        """
        提交缓存文件到Git仓库
        """
        try:
            cache_dir = os.path.join(self.directory_path, '.aitdocs_cache')
            if os.path.exists(cache_dir):
                # 添加整个缓存目录到Git
                self._run_git_command(["git", "add", ".aitdocs_cache/"])
        except Exception as e:
            # 如果提交缓存文件失败，仅打印警告，不中断主流程
            print(f"警告：提交缓存文件到Git时出错: {e}")

    def push_to_remote(self) -> None:
        """
        推送提交到远程仓库
        """
        try:
            self._run_git_command(["git", "push"])
        except Exception as e:
            raise Exception(f"Git推送失败: {e}")