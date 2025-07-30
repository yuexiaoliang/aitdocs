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
            已处理的文件路径列表
        """
        # 获取所有Markdown文件
        markdown_files = self._get_markdown_files()
        processed_files = []

        for source_file in markdown_files:
            try:
                # 计算翻译后的文件路径
                base_name = os.path.splitext(source_file)[0]
                translated_file = f"{base_name}_{self.target_lang}.md"

                # 检查翻译后的文件是否存在
                if os.path.exists(translated_file):
                    # 删除原始文件
                    os.remove(source_file)
                    
                    # 将翻译后的文件重命名为原始文件名
                    os.rename(translated_file, source_file)
                    processed_files.append(source_file)

                    print(f"已替换文件: {source_file} <- {translated_file}")
                else:
                    print(f"警告: 翻译文件不存在: {translated_file}")
            except Exception as e:
                print(f"替换文件 {source_file} 时出错: {e}")

        print(f"构建环境准备完成，共处理了 {len(processed_files)} 个文件")
        return processed_files