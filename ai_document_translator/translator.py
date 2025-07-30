import asyncio
import re
from typing import Optional
from .model_client import ModelClient


class Translator:
    """翻译器类，用于调用大模型进行文本翻译"""
    
    # 代码文件扩展名
    CODE_EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")
    
    def __init__(self):
        """初始化翻译器"""
        self.client = ModelClient()
        
    async def async_translate_text(
        self, 
        text: str, 
        source_lang: str = "auto", 
        target_lang: str = "zh",
        system_prompt: Optional[str] = None,
        file_extension: str = ""
    ) -> str:
        """
        异步翻译文本
        
        Args:
            text: 待翻译的文本
            source_lang: 源语言代码，默认为"auto"自动检测
            target_lang: 目标语言代码，默认为"zh"中文
            system_prompt: 系统提示词，可选
            file_extension: 文件扩展名，用于判断是否为代码文件
            
        Returns:
            翻译后的文本
        """
        # 构建系统提示词
        if not system_prompt:
            if source_lang == "auto":
                system_prompt = f"你是一个专业的翻译助手，请自动检测用户提供的文本的语言，并翻译成{target_lang}。"
            else:
                system_prompt = f"你是一个专业的翻译助手，请将用户提供的文本从{source_lang}翻译成{target_lang}。"
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        # 异步调用模型
        response = await self.client.async_chat_completions(messages)
        translated_content = response["choices"][0]["message"]["content"]
        
        # 如果是代码文件，尝试移除可能的代码块包装
        if file_extension in self.CODE_EXTENSIONS:
            translated_content = self._remove_code_block_wrapper(translated_content, file_extension)
            
        return translated_content
    
    def _remove_code_block_wrapper(self, content: str, file_extension: str) -> str:
        """
        移除可能的代码块包装
        
        Args:
            content: 翻译后的内容
            file_extension: 文件扩展名
            
        Returns:
            移除代码块包装后的内容
        """
        # 构造匹配模式
        extension = file_extension.lstrip('.')
        # 匹配 ```ts ... ``` 或 ```typescript ... ``` 等模式
        patterns = [
            rf"^\s*```{extension}\s*\n(.*?)\n\s*```[ \t]*$",
            rf"^\s*```{extension}\s*\n(.*?)\n\s*```[ \t]*\n*\s*$",
            rf"^\s*```\s*\n(.*?)\n\s*```[ \t]*$",
            rf"^\s*```\s*\n(.*?)\n\s*```[ \t]*\n*\s*$"
        ]
        
        # 尝试匹配各种模式
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1)
                
        # 如果没有匹配到，返回原始内容
        return content


async def async_translate(
    text: str, 
    source_lang: str = "auto", 
    target_lang: str = "zh",
    system_prompt: Optional[str] = None
) -> str:
    """
    异步翻译文本的简单函数
    
    Args:
        text: 待翻译的文本
        source_lang: 源语言代码，默认为"auto"自动检测
        target_lang: 目标语言代码，默认为"zh"中文
        system_prompt: 系统提示词，可选
        
    Returns:
        翻译后的文本
    """
    translator = Translator()
    return await translator.async_translate_text(text, source_lang, target_lang, system_prompt)