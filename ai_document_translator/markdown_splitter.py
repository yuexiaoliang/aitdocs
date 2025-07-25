import re


class MarkdownSplitter:
    """处理Markdown内容分割的类"""
    
    def __init__(self, chunk_size: int = 2000):
        """
        初始化Markdown分割器
        
        Args:
            chunk_size: 每个文本块的最大字符数
        """
        self.chunk_size = chunk_size
    
    def split_content(self, content: str) -> list:
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
    
    def _split_large_chunk(self, chunk: str) -> list:
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