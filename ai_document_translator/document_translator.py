import os
import re
import asyncio
from typing import List, Optional
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
        translated_chunks = [
        ]
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
        将Markdown内容分割为适当的块
        
        Args:
            content: Markdown内容
            
        Returns:
            分割后的内容块列表
        """
        # 按照标题分割内容
        sections = re.split(r'(\n#{1,6} .+?\n)', content)
        
        # 清理空字符串
        sections = [section for section in sections if section.strip()]
        
        chunks = [
        ]
        current_chunk = ""
        
        for section in sections:
            # 如果当前块加上新部分不超过限制，则添加
            if len(current_chunk) + len(section) <= self.chunk_size:
                current_chunk += section
            else:
                # 如果当前块不为空，先保存
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                # 如果单个部分就超过限制，则需要进一步分割
                if len(section) > self.chunk_size:
                    # 按段落分割
                    paragraphs = re.split(r'(\n\n)', section)
                    for paragraph in paragraphs:
                        if len(current_chunk) + len(paragraph) <= self.chunk_size:
                            current_chunk += paragraph
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = paragraph
                else:
                    current_chunk = section
                    
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks