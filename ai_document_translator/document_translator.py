import os
from typing import List, Optional
from .translator import Translator
from .git_manager import GitManager
from .ignore_manager import IgnorePatternManager
from .markdown_splitter import MarkdownSplitter
from .state_manager import StateManager


class DocumentTranslator:
    """文档翻译器，专门用于翻译Markdown文档"""

    def __init__(self, chunk_size: int = 2000):
        """
        初始化文档翻译器

        Args:
            chunk_size: 每个文本块的最大字符数，用于处理大文件
        """
        self.translator = Translator()
        self.chunk_size = chunk_size
        self.markdown_splitter = MarkdownSplitter(chunk_size)

    async def translate_markdown_file(
        self,
        file_path: str,
        source_lang: str = "auto",
        target_lang: str = "zh",
        output_path: Optional[str] = None
    ) -> str:
        """
        翻译Markdown文件

        Args:
            file_path: Markdown文件路径
            source_lang: 源语言代码
            target_lang: 目标语言代码
            output_path: 输出文件路径，如果为None则自动生成

        Returns:
            翻译后的内容
        """
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 翻译内容
        translated_content = await self.translate_markdown_content(
            content, source_lang, target_lang
        )

        # 确定输出文件路径
        if output_path is None:
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}_{target_lang}.md"

        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated_content)

        return translated_content

    async def translate_markdown_directory(
        self,
        directory_path: str,
        source_lang: str = "auto",
        target_lang: str = "zh",
        ignore_patterns: Optional[List[str]] = None,
        output_directory: Optional[str] = None,
        incremental: bool = False,
        auto_commit: bool = False,
        commit_message: str = "Update translated documents",
        auto_push: bool = False
    ) -> List[str]:
        """
        递归翻译目录中的所有Markdown文件

        Args:
            directory_path: 要翻译的目录路径
            source_lang: 源语言代码
            target_lang: 目标语言代码
            ignore_patterns: 忽略模式列表，支持通配符
            output_directory: 输出目录路径，如果为None则在原目录生成
            incremental: 是否启用增量翻译模式
            auto_commit: 是否自动提交翻译结果到Git
            commit_message: 自动提交的提交信息
            auto_push: 是否自动推送到远程仓库

        Returns:
            已翻译文件的路径列表
        """
        # 创建忽略模式管理器
        ignore_manager = IgnorePatternManager(directory_path, ignore_patterns)

        # 获取所有Markdown文件
        markdown_files = self._get_markdown_files(directory_path, ignore_manager)

        # 如果启用增量翻译，则只翻译变更的文件
        if incremental:
            markdown_files = self._get_changed_files_with_ignores(directory_path, markdown_files, ignore_manager)
            print(f"增量翻译模式: 找到 {len(markdown_files)} 个需要翻译的文件")

        # 翻译所有文件
        translated_files = []
        for file_path in markdown_files:
            try:
                print(f"正在翻译文件: {file_path}")

                # 计算相对于源目录的路径
                relative_path = os.path.relpath(file_path, directory_path)

                # 确定输出文件路径
                if output_directory:
                    # 创建对应的输出目录结构
                    output_file_dir = os.path.join(output_directory, os.path.dirname(relative_path))
                    os.makedirs(output_file_dir, exist_ok=True)
                    output_file_path = os.path.join(output_file_dir,
                                                   f"{os.path.splitext(os.path.basename(file_path))[0]}_{target_lang}.md")
                else:
                    # 在原目录生成翻译文件
                    base_name = os.path.splitext(file_path)[0]
                    output_file_path = f"{base_name}_{target_lang}.md"

                # 翻译文件
                await self.translate_markdown_file(
                    file_path, source_lang, target_lang, output_file_path
                )
                translated_files.append(output_file_path)
                print(f"完成翻译: {file_path} -> {output_file_path}")
            except Exception as e:
                print(f"翻译文件 {file_path} 时出错: {e}")

        # 如果启用了增量翻译，保存当前的Git提交哈希和忽略规则哈希
        if incremental:
            self._save_last_commit_hash(directory_path, ignore_manager)

        # 如果启用了自动提交，则提交翻译结果
        commit_success = True
        if auto_commit and translated_files:
            commit_success = self._git_commit_translated_files(directory_path, translated_files, commit_message)

        # 如果启用了自动推送且提交成功，则推送到远程仓库
        if auto_push and commit_success and translated_files:
            self._git_push_to_remote(directory_path)

        return translated_files

    def _get_markdown_files(self, directory_path: str, ignore_manager: IgnorePatternManager) -> List[str]:
        """
        获取目录中的所有Markdown文件

        Args:
            directory_path: 目录路径
            ignore_manager: 忽略模式管理器

        Returns:
            Markdown文件路径列表
        """
        markdown_files = []

        # 递归遍历目录
        for root, dirs, files in os.walk(directory_path):
            # 检查当前目录是否应该被忽略
            should_ignore_dir = False
            relative_root = os.path.relpath(root, directory_path)

            if ignore_manager.should_ignore(relative_root, is_dir=True):
                should_ignore_dir = True

            if should_ignore_dir:
                continue

            # 过滤子目录
            dirs[:] = [d for d in dirs if not ignore_manager.should_ignore(os.path.join(relative_root, d), is_dir=True)]

            # 查找Markdown文件
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(file_path, directory_path)

                    # 检查文件是否应该被忽略
                    if not ignore_manager.should_ignore(relative_file_path):
                        markdown_files.append(file_path)

        return markdown_files

    async def translate_markdown_content(
        self,
        content: str,
        source_lang: str = "auto",
        target_lang: str = "zh"
    ) -> str:
        """
        翻译Markdown内容

        Args:
            content: Markdown内容
            source_lang: 源语言代码
            target_lang: 目标语言代码

        Returns:
            翻译后的内容
        """
        # 分割内容为块，同时保持Markdown结构的完整性
        chunks = self.markdown_splitter.split_content(content)

        # 翻译每个块
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"正在翻译第 {i+1}/{len(chunks)} 段内容...")
            translated_chunk = await self.translator.async_translate_text(
                chunk, source_lang, target_lang,
                system_prompt=f"你是一个专业的技术文档翻译助手。请将用户提供的Markdown格式文本从{source_lang}翻译成{target_lang}，"
                             f"保持原有的Markdown格式不变，包括标题、列表、代码块等。"
            )
            translated_chunks.append(translated_chunk)

        return "\n\n".join(translated_chunks)


    def _get_changed_files_with_ignores(self, directory_path: str, markdown_files: List[str], ignore_manager: IgnorePatternManager) -> List[str]:
        """
        获取自上次翻译以来需要翻译的文件列表（考虑文件变更和忽略规则变更）

        Args:
            directory_path: Git仓库路径
            markdown_files: 所有Markdown文件列表
            ignore_manager: 忽略模式管理器

        Returns:
            需要翻译的文件列表
        """
        # 创建Git管理器实例
        git_manager = GitManager(directory_path)

        # 获取当前提交哈希和忽略规则哈希
        current_commit = git_manager.get_current_commit_hash()
        current_ignore_hash = ignore_manager.get_ignore_hash()
        print(f"当前提交哈希：{current_commit}，当前忽略规则哈希：{current_ignore_hash}")

        if not current_commit:
            print("警告：当前目录不是Git仓库或Git命令不可用，将进行全量翻译")
            return markdown_files

        # 获取上次翻译时的状态
        state_manager = StateManager(directory_path)
        last_state = state_manager.get_last_state()
        if not last_state:
            print("提示：未找到上次翻译记录，将进行全量翻译")
            return markdown_files

        last_commit = last_state.get('last_commit_hash')
        last_ignore_hash = last_state.get('ignore_hash')
        print(f"上次提交哈希：{last_commit}，上次忽略规则哈希：{last_ignore_hash}")

        # 如果忽略规则发生了变化，则需要全量翻译
        if current_ignore_hash != last_ignore_hash:
            print("提示：忽略规则已变更，将进行全量翻译")
            return markdown_files

        # 如果提交哈希相同，表示没有文件变更
        if current_commit == last_commit:
            print("提示：自上次翻译以来没有文件变更")
            return []

        # 确保last_commit不为None
        if not last_commit:
            print("提示：上次提交哈希不存在，将进行全量翻译")
            return markdown_files

        try:
            # 使用git diff获取变更的文件
            changed_files = git_manager.get_changed_files(last_commit, current_commit)

            # 过滤出变更的Markdown文件
            changed_markdown_files = []
            for file_path in markdown_files:
                relative_path = os.path.relpath(file_path, directory_path)
                if relative_path in changed_files:
                    changed_markdown_files.append(file_path)

            return changed_markdown_files

        except Exception as e:
            print(f"警告：{e}，将进行全量翻译")
            return markdown_files

    def _git_commit_translated_files(self, directory_path: str, translated_files: List[str], commit_message: str) -> bool:
        """
        将翻译后的文件自动提交到Git仓库

        Args:
            directory_path: Git仓库路径
            translated_files: 翻译后的文件列表
            commit_message: 提交信息

        Returns:
            是否提交成功
        """
        git_manager = GitManager(directory_path)
        try:
            git_manager.commit_files(translated_files, commit_message)
            print(f"成功提交 {len(translated_files)} 个翻译文件到Git仓库")

            # 提交后更新状态文件中的提交哈希为最新值
            latest_commit_hash = git_manager.get_current_commit_hash()
            if latest_commit_hash:
                state_manager = StateManager(directory_path)
                last_state = state_manager.get_last_state()
                if last_state:
                    ignore_hash = last_state.get('ignore_hash', '')
                    state_manager.save_state(latest_commit_hash, ignore_hash)
                    git_manager.commit_state_file()

            return True
        except Exception as e:
            print(f"警告：{e}")
            return False

    def _git_push_to_remote(self, directory_path: str) -> None:
        """
        推送提交到远程仓库

        Args:
            directory_path: Git仓库路径
        """
        git_manager = GitManager(directory_path)
        try:
            git_manager.push_to_remote()
            print("成功推送到远程仓库")
        except Exception as e:
            print(f"警告：{e}")

    def _save_last_commit_hash(self, directory_path: str, ignore_manager: IgnorePatternManager) -> None:
        """
        保存当前Git提交哈希和忽略规则到状态文件

        Args:
            directory_path: Git仓库路径
            ignore_manager: 忽略模式管理器
        """
        git_manager = GitManager(directory_path)
        commit_hash = git_manager.get_current_commit_hash()
        ignore_hash = ignore_manager.get_ignore_hash()

        if commit_hash:
            try:
                state_manager = StateManager(directory_path)
                state_manager.save_state(commit_hash, ignore_hash)
            except Exception as e:
                print(f"警告：{e}")