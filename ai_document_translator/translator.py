import asyncio
from typing import Optional
from .model_client import ModelClient


class Translator:
    """翻译器类，用于调用大模型进行文本翻译"""
    
    def __init__(self):
        """初始化翻译器"""
        self.client = ModelClient()
        
    async def async_translate_text(
        self, 
        text: str, 
        source_lang: str = "auto", 
        target_lang: str = "zh",
        system_prompt: Optional[str] = None
    ) -> str:
        """
        异步翻译文本
        
        Args:
            text: 待翻译的文本
            source_lang: 源语言代码，默认为"auto"自动检测
            target_lang: 目标语言代码，默认为"zh"中文
            system_prompt: 系统提示词，可选
            
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
        return response["choices"][0]["message"]["content"]


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