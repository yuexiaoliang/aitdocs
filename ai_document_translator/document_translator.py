import os
import re
import asyncio
import fnmatch
import json
import subprocess
import hashlib
from typing import List, Optional, Set
from pathlib import Path
from .translator import Translator


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
        incremental: bool = False
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
            
        Returns:
            已翻译文件的路径列表
        """
        # 获取所有Markdown文件
        markdown_files = self._get_markdown_files(directory_path, ignore_patterns)
        
        # 如果启用增量翻译，则只翻译变更的文件
        if incremental:
            markdown_files = self._get_changed_files_with_ignores(directory_path, markdown_files, ignore_patterns)
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
            self._save_last_commit_hash(directory_path, ignore_patterns)
                
        return translated_files
    
    def _get_markdown_files(self, directory_path: str, ignore_patterns: Optional[List[str]] = None) -> List[str]:
        """
        获取目录中的所有Markdown文件
        
        Args:
            directory_path: 目录路径
            ignore_patterns: 忽略模式列表
            
        Returns:
            Markdown文件路径列表
        """
        markdown_files = []
        ignore_patterns = ignore_patterns or []
        
        # 添加默认忽略的目录和文件
        default_ignores = ['.git', '.venv', '__pycache__', '*.py', '*.pyc', '*.pyo', '*.pyd']
        ignore_patterns.extend(default_ignores)
        
        # 读取.gitignore文件中的忽略规则
        gitignore_path = os.path.join(directory_path, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore_patterns.append(line)
        
        # 读取.aitdocsignore文件中的忽略规则
        aitdocsignore_path = os.path.join(directory_path, '.aitdocsignore')
        if os.path.exists(aitdocsignore_path):
            with open(aitdocsignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore_patterns.append(line)
        
        # 递归遍历目录
        for root, dirs, files in os.walk(directory_path):
            # 检查当前目录是否应该被忽略
            should_ignore_dir = False
            relative_root = os.path.relpath(root, directory_path)
            
            for pattern in ignore_patterns:
                # 处理目录忽略模式
                if pattern.endswith('/') or pattern.endswith('\\'):
                    dir_pattern = pattern.rstrip('/\\')
                    if fnmatch.fnmatch(relative_root, dir_pattern) or \
                       fnmatch.fnmatch(os.path.basename(root), dir_pattern):
                        should_ignore_dir = True
                        break
                # 处理通用模式
                elif fnmatch.fnmatch(relative_root, pattern):
                    should_ignore_dir = True
                    break
            
            if should_ignore_dir:
                continue
            
            # 过滤子目录
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(relative_root, d), ignore_patterns, is_dir=True)]
            
            # 查找Markdown文件
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(file_path, directory_path)
                    
                    # 检查文件是否应该被忽略
                    if not self._should_ignore(relative_file_path, ignore_patterns):
                        markdown_files.append(file_path)
                        
        return markdown_files
    
    def _should_ignore(self, path: str, ignore_patterns: List[str], is_dir: bool = False) -> bool:
        """
        判断路径是否应该被忽略
        
        Args:
            path: 路径
            ignore_patterns: 忽略模式列表
            is_dir: 是否为目录
            
        Returns:
            是否应该忽略
        """
        for pattern in ignore_patterns:
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
        chunks = self._split_markdown_content(content)
        
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
    
    def _split_markdown_content(self, content: str) -> List[str]:
        """
        将Markdown内容分割为适当的块，确保代码块和表格的完整性
        
        Args:
            content: Markdown内容
            
        Returns:
            分割后的内容块列表
        """
        chunks = []
        current_chunk = ""
        
        # 按行分割内容，便于检测代码块
        lines = content.split('\n')
        in_code_block = False
        code_block_fence = ""
        
        for line in lines:
            # 检查是否进入或退出代码块
            if line.startswith('```') or line.startswith('~~~'):
                if not in_code_block:
                    # 进入代码块
                    in_code_block = True
                    code_block_fence = line[:3]  # 记录分隔符类型 (``` 或 ~~~)
                elif line.startswith(code_block_fence):
                    # 退出代码块
                    in_code_block = False
                    code_block_fence = ""
            
            # 检查添加这行后是否会超出块大小限制
            line_length = len(line) + 1  # +1 是换行符
            
            # 如果在代码块中，必须保持代码块完整
            if in_code_block:
                if len(current_chunk) + line_length > self.chunk_size and not current_chunk.endswith('\n'):
                    current_chunk += '\n' + line
                else:
                    current_chunk += line + '\n'
            else:
                # 不在代码块中，可以正常处理
                # 如果添加这行会超出限制
                if len(current_chunk) + line_length > self.chunk_size:
                    # 保存当前块
                    if current_chunk.strip():
                        chunks.append(current_chunk.rstrip())
                    
                    # 开始新的块
                    current_chunk = line + '\n'
                else:
                    # 检查是否是标题行
                    is_header = line.startswith('#') and not line.startswith('#' * 40)  # 避免把分隔线当作标题
                    
                    # 如果是标题且当前块不为空，可以考虑在此处分割
                    if is_header and current_chunk.strip() and len(current_chunk) > self.chunk_size * 0.5:
                        chunks.append(current_chunk.rstrip())
                        current_chunk = line + '\n'
                    else:
                        current_chunk += line + '\n'
        
        # 添加最后一个块
        if current_chunk.strip():
            chunks.append(current_chunk.rstrip())
            
        # 如果某个块仍然太大，尝试按段落进一步分割（但避免分割代码块）
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # 对大块进一步分割
                sub_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
                
        return final_chunks
    
    def _split_large_chunk(self, chunk: str) -> List[str]:
        """
        分割大的内容块，尽可能保持语义完整性
        
        Args:
            chunk: 需要分割的内容块
            
        Returns:
            分割后的内容块列表
        """
        if len(chunk) <= self.chunk_size:
            return [chunk]
        
        sub_chunks = []
        current_sub_chunk = ""
        
        # 按段落分割
        paragraphs = re.split(r'(\n\s*\n)', chunk)
        
        for paragraph in paragraphs:
            # 如果添加这个段落会超出大小限制
            if len(current_sub_chunk) + len(paragraph) > self.chunk_size:
                # 保存当前子块
                if current_sub_chunk.strip():
                    sub_chunks.append(current_sub_chunk.rstrip())
                
                # 如果单个段落就超出限制
                if len(paragraph) > self.chunk_size:
                    # 强制分割长段落
                    sub_chunks.append(paragraph[:self.chunk_size])
                    remaining = paragraph[self.chunk_size:]
                    if remaining:
                        current_sub_chunk = remaining
                else:
                    current_sub_chunk = paragraph
            else:
                current_sub_chunk += paragraph
        
        # 添加最后一个子块
        if current_sub_chunk.strip():
            sub_chunks.append(current_sub_chunk.rstrip())
            
        return sub_chunks if sub_chunks else [chunk]
    
    def _get_git_commit_hash(self, directory_path: str) -> Optional[str]:
        """
        获取当前Git提交哈希
        
        Args:
            directory_path: Git仓库路径
            
        Returns:
            当前提交哈希，如果失败则返回None
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=directory_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def _get_last_state(self, directory_path: str) -> Optional[dict]:
        """
        获取上次翻译时保存的状态
        
        Args:
            directory_path: Git仓库路径
            
        Returns:
            上次翻译时的状态，如果不存在则返回None
        """
        state_file = os.path.join(directory_path, '.aitdocs_state')
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                return None
        return None
    
    def _save_last_commit_hash(self, directory_path: str, ignore_patterns: Optional[List[str]] = None) -> None:
        """
        保存当前Git提交哈希和忽略规则到状态文件
        
        Args:
            directory_path: Git仓库路径
            ignore_patterns: 忽略模式列表
        """
        commit_hash = self._get_git_commit_hash(directory_path)
        ignore_hash = self._calculate_ignore_hash(directory_path, ignore_patterns)
        
        if commit_hash:
            state_file = os.path.join(directory_path, '.aitdocs_state')
            state = {}
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                except json.JSONDecodeError:
                    pass
            
            state['last_commit_hash'] = commit_hash
            state['ignore_hash'] = ignore_hash
            try:
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
            except Exception as e:
                print(f"警告：无法保存状态文件: {e}")
    
    def _calculate_ignore_hash(self, directory_path: str, ignore_patterns: Optional[List[str]] = None) -> str:
        """
        计算忽略规则的哈希值
        
        Args:
            directory_path: 目录路径
            ignore_patterns: 命令行传入的忽略模式
            
        Returns:
            忽略规则的哈希值
        """
        ignore_patterns = ignore_patterns or []
        
        # 添加默认忽略的目录和文件
        default_ignores = ['.git', '.venv', '__pycache__', '*.py', '*.pyc', '*.pyo', '*.pyd']
        all_ignore_patterns = ignore_patterns + default_ignores
        
        # 读取.gitignore文件中的忽略规则
        gitignore_path = os.path.join(directory_path, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        all_ignore_patterns.append(line)
        
        # 读取.aitdocsignore文件中的忽略规则
        aitdocsignore_path = os.path.join(directory_path, '.aitdocsignore')
        if os.path.exists(aitdocsignore_path):
            with open(aitdocsignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        all_ignore_patterns.append(line)
        
        # 对忽略规则进行排序以确保一致性
        all_ignore_patterns.sort()
        
        # 计算哈希值
        ignore_str = '\n'.join(all_ignore_patterns)
        return hashlib.md5(ignore_str.encode('utf-8')).hexdigest()
    
    def _get_changed_files_with_ignores(self, directory_path: str, markdown_files: List[str], ignore_patterns: Optional[List[str]] = None) -> List[str]:
        """
        获取自上次翻译以来需要翻译的文件列表（考虑文件变更和忽略规则变更）
        
        Args:
            directory_path: Git仓库路径
            markdown_files: 所有Markdown文件列表
            ignore_patterns: 忽略模式列表
            
        Returns:
            需要翻译的文件列表
        """
        # 获取当前提交哈希和忽略规则哈希
        current_commit = self._get_git_commit_hash(directory_path)
        current_ignore_hash = self._calculate_ignore_hash(directory_path, ignore_patterns)
        
        if not current_commit:
            print("警告：当前目录不是Git仓库或Git命令不可用，将进行全量翻译")
            return markdown_files
        
        # 获取上次翻译时的状态
        last_state = self._get_last_state(directory_path)
        if not last_state:
            print("提示：未找到上次翻译记录，将进行全量翻译")
            return markdown_files
        
        last_commit = last_state.get('last_commit_hash')
        last_ignore_hash = last_state.get('ignore_hash')
        
        # 如果忽略规则发生了变化，则需要全量翻译
        if current_ignore_hash != last_ignore_hash:
            print("提示：忽略规则已变更，将进行全量翻译")
            return markdown_files
        
        # 如果提交哈希相同，表示没有文件变更
        if current_commit == last_commit:
            print("提示：自上次翻译以来没有文件变更")
            return []
        
        try:
            # 使用git diff获取变更的文件
            result = subprocess.run(
                ['git', 'diff', '--name-only', last_commit, current_commit],
                cwd=directory_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = result.stdout.strip().split('\n')
            changed_files = [f for f in changed_files if f]  # 移除空行
            
            # 过滤出变更的Markdown文件
            changed_markdown_files = []
            for file_path in markdown_files:
                relative_path = os.path.relpath(file_path, directory_path)
                if relative_path in changed_files:
                    changed_markdown_files.append(file_path)
            
            return changed_markdown_files
            
        except subprocess.CalledProcessError as e:
            print(f"警告：执行Git diff时出错，将进行全量翻译: {e}")
            return markdown_files