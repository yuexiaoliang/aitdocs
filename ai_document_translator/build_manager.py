import os
import shutil
from typing import List


class BuildManager:
    """构建环境管理器，用于在构建时替换和恢复文件"""

    def __init__(self, directory_path: str, target_lang: str = "zh", backup_suffix: str = ".aitdocs.bak"):
        """
        初始化构建环境管理器

        Args:
            directory_path: 目录路径
            target_lang: 目标语言代码
            backup_suffix: 备份文件后缀
        """
        self.directory_path = directory_path
        self.target_lang = target_lang
        self.backup_suffix = backup_suffix

    def _get_markdown_files(self) -> List[str]:
        """
        获取目录中的所有Markdown文件

        Returns:
            Markdown文件路径列表
        """
        markdown_files = []
        
        # 递归遍历目录
        for root, dirs, files in os.walk(self.directory_path):
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    markdown_files.append(file_path)

        return markdown_files

    def prepare_build_environment(self) -> List[str]:
        """
        准备构建环境，将源文件替换为翻译后的文件

        Returns:
            已备份的文件路径列表
        """
        # 获取所有Markdown文件
        markdown_files = self._get_markdown_files()
        backed_up_files = []

        for source_file in markdown_files:
            try:
                # 计算翻译后的文件路径
                base_name = os.path.splitext(source_file)[0]
                translated_file = f"{base_name}_{self.target_lang}.md"

                # 检查翻译后的文件是否存在
                if os.path.exists(translated_file):
                    # 备份原始文件
                    backup_file = f"{source_file}{self.backup_suffix}"
                    shutil.copy2(source_file, backup_file)
                    backed_up_files.append(source_file)

                    # 用翻译后的文件替换原始文件
                    shutil.copy2(translated_file, source_file)
                    print(f"已替换文件: {source_file} -> {translated_file}")
                else:
                    print(f"警告: 翻译文件不存在: {translated_file}")
            except Exception as e:
                print(f"替换文件 {source_file} 时出错: {e}")

        print(f"构建环境准备完成，共替换了 {len(backed_up_files)} 个文件")
        return backed_up_files

    def restore_build_environment(self) -> None:
        """
        恢复构建环境，将备份的文件还原
        """
        restored_count = 0

        # 递归遍历目录，查找所有备份文件
        for root, dirs, files in os.walk(self.directory_path):
            for file in files:
                if file.endswith(self.backup_suffix):
                    try:
                        # 构造备份文件路径和原始文件路径
                        backup_file = os.path.join(root, file)
                        original_file = backup_file[:-len(self.backup_suffix)]

                        # 恢复原始文件
                        shutil.move(backup_file, original_file)
                        restored_count += 1
                        print(f"已恢复文件: {original_file}")
                    except Exception as e:
                        print(f"恢复文件 {file} 时出错: {e}")

        print(f"构建环境恢复完成，共恢复了 {restored_count} 个文件")