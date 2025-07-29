import os
import json
from typing import Optional, Dict


class StateManager:
    """状态管理器，负责处理 .aitdocs_state 状态文件的读写操作"""

    def __init__(self, directory_path: str):
        """
        初始化状态管理器

        Args:
            directory_path: 工作目录路径
        """
        self.directory_path = directory_path
        self.state_file = os.path.join(directory_path, ".aitdocs_state")

    def get_last_state(self) -> Optional[Dict]:
        """
        获取上次翻译时保存的状态

        Returns:
            上次翻译时的状态，如果不存在则返回None
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
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
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except json.JSONDecodeError:
                pass

        state["last_commit_hash"] = commit_hash
        state["ignore_hash"] = ignore_hash
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            raise Exception(f"无法保存状态文件: {e}")

    def get_state_file_path(self) -> str:
        """
        获取状态文件路径

        Returns:
            状态文件的完整路径
        """
        return self.state_file