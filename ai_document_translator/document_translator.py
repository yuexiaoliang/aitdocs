import os
import asyncio
from typing import List, Optional
from .translator import Translator
from .git_manager import GitManager
from .ignore_manager import IgnorePatternManager
from .markdown_splitter import MarkdownSplitter
from .state_manager import StateManager
from .cache_manager import CacheManager


class DocumentTranslator:
    """文档翻译器，专门用于翻译Markdown文档"""

    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = (".md", ".markdown", ".js", ".jsx", ".ts", ".tsx", ".mdx")
    
    # 代码文件扩展名
    CODE_EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")

    def __init__(
        self,
        chunk_size: int = 10000,
        source_lang: str = "auto",
        target_lang: str = "zh",
        incremental: bool = False,
        auto_commit: bool = False,
        auto_push: bool = False,
        commit_message: str = "Update translated documents [aitdocs]",
        directory_path: str = ".",
        ignore_patterns: Optional[List[str]] = None,
        output_directory: Optional[str] = None,
        max_concurrent: int = 5,  # 添加最大并发数参数
    ):
        """
        初始化文档翻译器

        Args:
            chunk_size: 每个文本块的最大字符数，用于处理大文件
            source_lang: 源语言代码
            target_lang: 目标语言代码
            incremental: 是否启用增量翻译模式
            auto_commit: 是否自动提交翻译结果到Git
            auto_push: 是否自动推送到远程仓库
            commit_message: 自动提交的提交信息
            directory_path: 要翻译的目录路径
            ignore_patterns: 忽略模式列表，支持通配符
            output_directory: 输出目录路径，如果为None则在原目录生成
            max_concurrent: 最大并发翻译任务数
        """
        self.translator = Translator()
        self.chunk_size = chunk_size
        self.markdown_splitter = MarkdownSplitter(chunk_size)
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.incremental = incremental
        self.auto_commit = auto_commit
        self.auto_push = auto_push
        self.commit_message = commit_message
        self.directory_path = directory_path
        self.ignore_patterns = ignore_patterns
        self.output_directory = output_directory
        self.max_concurrent = max_concurrent  # 保存最大并发数

        # 初始化管理器
        self.git_manager = GitManager(self.directory_path)
        self.ignore_manager = IgnorePatternManager(
            self.directory_path, self.ignore_patterns
        )
        self.state_manager = StateManager(self.directory_path)

        # 初始化缓存管理器
        cache_directory = os.path.join(self.directory_path, '.aitdocs_cache')
        self.cache_manager = CacheManager(cache_directory)

    async def translate_markdown_file(
        self,
        file_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        翻译Markdown文件

        Args:
            file_path: Markdown文件路径
            output_path: 输出文件路径，如果为None则自动生成

        Returns:
            翻译后的内容
        """
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查缓存中是否有翻译结果
        cached_content = None
        if self.incremental:
            cached_content = self.cache_manager.get_from_cache(content)

        if cached_content:
            translated_content = cached_content
            print(f"从缓存中获取翻译结果: {file_path}")
        else:
            # 翻译内容
            translated_content = await self.translate_markdown_content(content, file_path)
            # 将翻译结果保存到缓存
            if self.incremental:
                self.cache_manager.save_to_cache(content, translated_content)

        # 确定输出文件路径
        if output_path is None:
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            output_path = f"{base_name}_{self.target_lang}{ext}"

        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated_content)

        return translated_content

    async def translate_markdown_directory(self) -> List[str]:
        """
        递归翻译目录中的所有Markdown文件

        Returns:
            已翻译文件的路径列表
        """
        # 获取所有Markdown文件
        markdown_files = self._get_markdown_files()

        # 如果启用增量翻译，则只翻译变更的文件
        if self.incremental:
            markdown_files = self._get_changed_files_with_ignores(markdown_files)
            print(f"增量翻译模式: 找到 {len(markdown_files)} 个需要翻译的文件")

        # 翻译所有文件（使用并发）
        translated_files = []
        if markdown_files:
            # 使用信号量控制最大并发数
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def translate_with_semaphore(file_path):
                async with semaphore:
                    return await self._translate_single_file(file_path)
            
            # 创建所有翻译任务
            tasks = [translate_with_semaphore(file_path) for file_path in markdown_files]
            
            # 并发执行所有翻译任务
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(results):
                file_path = markdown_files[i]
                if isinstance(result, Exception):
                    print(f"翻译文件 {file_path} 时出错: {result}")
                else:
                    translated_files.append(result)
                    print(f"完成翻译: {file_path} -> {result}")

        # 如果启用了增量翻译，保存当前的Git提交哈希和忽略规则哈希
        if self.incremental:
            self._save_last_commit_hash()

        # 如果启用了自动提交，则提交翻译结果
        commit_success = True
        if self.auto_commit and translated_files:
            commit_success = self._git_commit_translated_files(translated_files)

        # 如果启用了自动推送且提交成功，则推送到远程仓库
        if self.auto_push and commit_success and translated_files:
            self._git_push_to_remote()

        return translated_files

    async def _translate_single_file(self, file_path: str) -> str:
        """
        翻译单个文件的内部方法

        Args:
            file_path: 要翻译的文件路径

        Returns:
            翻译后文件的路径
        """
        # 计算相对于源目录的路径
        relative_path = os.path.relpath(file_path, self.directory_path)

        # 确定输出文件路径
        if self.output_directory:
            # 创建对应的输出目录结构
            output_file_dir = os.path.join(
                self.output_directory, os.path.dirname(relative_path)
            )
            os.makedirs(output_file_dir, exist_ok=True)
            output_file_path = os.path.join(
                output_file_dir,
                f"{os.path.splitext(os.path.basename(file_path))[0]}_{self.target_lang}{os.path.splitext(file_path)[1]}",
            )
        else:
            # 在原目录生成翻译文件
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            output_file_path = f"{base_name}_{self.target_lang}{ext}"

        print(f"正在翻译文件: {file_path} (并发任务数: {self.max_concurrent})")
        # 翻译文件
        await self.translate_markdown_file(file_path, output_file_path)
        print(f"完成翻译: {file_path} -> {output_file_path}")
        return output_file_path

    def _get_markdown_files(self) -> List[str]:
        """
        获取目录中的所有Markdown文件

        Returns:
            Markdown文件路径列表
        """
        markdown_files = []

        # 递归遍历目录
        for root, dirs, files in os.walk(self.directory_path):
            # 检查当前目录是否应该被忽略
            should_ignore_dir = False
            relative_root = os.path.relpath(root, self.directory_path)

            if self.ignore_manager.should_ignore(relative_root, is_dir=True):
                should_ignore_dir = True

            if should_ignore_dir:
                continue

            # 过滤子目录
            dirs[:] = [
                d
                for d in dirs
                if not self.ignore_manager.should_ignore(
                    os.path.join(relative_root, d), is_dir=True
                )
            ]

            # 查找支持的文件类型
            for file in files:
                if file.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(file_path, self.directory_path)

                    # 检查文件是否应该被忽略
                    if not self.ignore_manager.should_ignore(relative_file_path):
                        markdown_files.append(file_path)

        return markdown_files

    async def translate_markdown_content(self, content: str, file_path: str = "") -> str:
        """
        翻译Markdown内容

        Args:
            content: Markdown内容
            file_path: 文件路径，用于确定内容类型

        Returns:
            翻译后的内容
        """
        # 根据文件扩展名确定内容类型
        system_prompt = f"你是一个专业的技术文档翻译助手。请将用户提供的文本从{self.source_lang}翻译成{self.target_lang}。"
        file_extension = ""
        
        if file_path:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension in (".md", ".markdown", ".mdx"):
                system_prompt = f"你是一个专业的技术文档翻译助手。请将用户提供的Markdown格式文本从{self.source_lang}翻译成{self.target_lang}，" \
                               f"保持原有的Markdown格式不变，包括标题、列表、代码块等。"
            elif file_extension in (".js", ".jsx", ".ts", ".tsx"):
                system_prompt = f"你是一个专业的程序员翻译助手。请将用户提供的代码注释或文档字符串从{self.source_lang}翻译成{self.target_lang}，" \
                               f"保持代码结构不变，只翻译注释部分。"
        
        # 对于代码文件，我们不分割内容，直接翻译整个文件
        if file_path and os.path.splitext(file_path)[1].lower() in self.CODE_EXTENSIONS:
            print(f"正在翻译代码文件: {file_path}")
            translated_content = await self.translator.async_translate_text(
                content,
                self.source_lang,
                self.target_lang,
                system_prompt=system_prompt,
                file_extension=file_extension
            )
            return translated_content
        
        # 对于Markdown文件，使用原有的分割方式
        # 分割内容为块，同时保持Markdown结构的完整性
        chunks = self.markdown_splitter.split_content(content)

        # 翻译每个块
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"正在翻译第 {i+1}/{len(chunks)} 段内容...")
            translated_chunk = await self.translator.async_translate_text(
                chunk,
                self.source_lang,
                self.target_lang,
                system_prompt=system_prompt,
                file_extension=file_extension  # 对于Markdown文件也传递扩展名
            )
            translated_chunks.append(translated_chunk)

        return "\n\n".join(translated_chunks)


    def _get_changed_files_with_ignores(self, markdown_files: List[str]) -> List[str]:
        """
        获取自上次翻译以来需要翻译的文件列表（考虑文件变更和忽略规则变更）

        Args:
            markdown_files: 所有Markdown文件列表

        Returns:
            需要翻译的文件列表
        """
        # 获取当前提交哈希和忽略规则哈希
        current_commit = self.git_manager.get_current_commit_hash()
        current_ignore_hash = self.ignore_manager.get_ignore_hash()
        print(
            f"当前提交哈希：{current_commit}，当前忽略规则哈希：{current_ignore_hash}"
        )

        if not current_commit:
            print("警告：当前目录不是Git仓库或Git命令不可用，将进行全量翻译")
            return markdown_files

        # 获取上次翻译时的状态
        last_state = self.state_manager.get_last_state()
        if not last_state:
            print("提示：未找到上次翻译记录，将进行全量翻译")
            return markdown_files

        last_commit = last_state.get("last_commit_hash")
        last_ignore_hash = last_state.get("ignore_hash")
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
            changed_files = self.git_manager.get_changed_files(
                last_commit, current_commit
            )

            # 过滤出变更的Markdown文件
            changed_markdown_files = []
            for file_path in markdown_files:
                relative_path = os.path.relpath(file_path, self.directory_path)
                if relative_path in changed_files:
                    changed_markdown_files.append(file_path)

            return changed_markdown_files

        except Exception as e:
            print(f"警告：{e}，将进行全量翻译")
            return markdown_files

    def _git_commit_translated_files(self, translated_files: List[str]) -> bool:
        """
        将翻译后的文件自动提交到Git仓库

        Args:
            translated_files: 翻译后的文件列表

        Returns:
            是否提交成功
        """
        try:
            self.git_manager.commit_files(translated_files, self.commit_message)
            print(f"成功提交 {len(translated_files)} 个翻译文件到Git仓库")

            # 提交后更新状态文件中的提交哈希为最新值
            latest_commit_hash = self.git_manager.get_current_commit_hash()
            if latest_commit_hash:
                ignore_hash = self.ignore_manager.get_ignore_hash()
                self.state_manager.save_state(latest_commit_hash, ignore_hash)
                self.git_manager.commit_state_file()

            return True
        except Exception as e:
            print(f"警告：{e}")
            return False

    def _git_push_to_remote(self) -> None:
        """
        推送提交到远程仓库
        """
        try:
            # 在推送前先提交缓存文件
            self.git_manager.commit_cache_files()
            self.git_manager.push_to_remote()
            print("成功推送到远程仓库")
        except Exception as e:
            print(f"警告：{e}")

    def _save_last_commit_hash(self) -> None:
        """
        保存当前Git提交哈希和忽略规则到状态文件

        Args:
            ignore_manager: 忽略模式管理器
        """
        commit_hash = self.git_manager.get_current_commit_hash()
        ignore_hash = self.ignore_manager.get_ignore_hash()

        if commit_hash:
            try:
                self.state_manager.save_state(commit_hash, ignore_hash)
            except Exception as e:
                print(f"警告：{e}")