import os
from typing import Dict, Any, List, Union
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

# 加载环境变量
load_dotenv()


class ModelClient:
    """阿里云大模型客户端，使用OpenAI兼容接口"""

    def __init__(self):
        """初始化模型客户端"""
        self.base_url = os.getenv(
            "ALI_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"
        )
        self.model_name = os.getenv("ALI_MODEL_NAME", "qwen-plus")
        self.api_key = os.getenv("ALI_API_KEY")

        if not self.api_key:
            raise ValueError("缺少必要的环境变量配置: ALI_API_KEY")

        # 初始化OpenAI客户端
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

        # 初始化异步OpenAI客户端
        self.async_client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    def chat_completions(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """
        调用聊天完成接口

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            模型响应
        """
        try:
            # 转换消息类型以匹配ChatCompletionMessageParam
            chat_messages: List[ChatCompletionMessageParam] = messages  # type: ignore
            response = self.client.chat.completions.create(
                model=self.model_name, messages=chat_messages, **kwargs
            )
            return response.model_dump()
        except Exception as e:
            raise Exception(f"调用大模型API失败: {str(e)}")

    async def async_chat_completions(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        异步调用聊天完成接口

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            模型响应
        """
        try:
            # 转换消息类型以匹配ChatCompletionMessageParam
            chat_messages: List[ChatCompletionMessageParam] = messages  # type: ignore
            response = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=chat_messages,
                **kwargs,
            )
            return response.model_dump()
        except Exception as e:
            raise Exception(f"调用大模型API失败: {str(e)}")
