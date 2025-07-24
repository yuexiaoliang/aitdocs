import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

# 加载环境变量
load_dotenv()


class ModelClient:
    """阿里云大模型客户端，使用LangChain实现"""
    
    def __init__(self):
        """初始化模型客户端"""
        self.base_url = os.getenv("ALI_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
        self.model_name = os.getenv("ALI_MODEL_NAME", "qwen-plus")
        self.api_key = os.getenv("ALI_API_KEY")
        
        if not self.api_key:
            raise ValueError("缺少必要的环境变量配置: ALI_API_KEY")
        
        # 初始化LangChain的ChatOpenAI客户端
        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            temperature=0.7
        )
    
    def chat_completions(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用聊天完成接口
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            模型响应
        """
        try:
            # 转换消息格式
            langchain_messages: List[BaseMessage] = []
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
            
            # 更新模型参数
            llm = self.llm.bind(temperature=temperature)
            if max_tokens:
                llm = llm.bind(max_tokens=max_tokens)
            
            # 调用模型
            response = llm.invoke(langchain_messages)
            
            # 转换响应格式以保持与之前实现的兼容性
            return {
                "id": "chatcmpl-langchain",
                "choices": [{
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": response.content,
                        "role": "assistant"
                    }
                }],
                "model": self.model_name,
                "object": "chat.completion"
            }
        except Exception as e:
            raise Exception(f"调用大模型API失败: {str(e)}")
    
    async def async_chat_completions(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        异步调用聊天完成接口
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            模型响应
        """
        try:
            # 转换消息格式
            langchain_messages: List[BaseMessage] = []
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
            
            # 更新模型参数
            llm = self.llm.bind(temperature=temperature)
            if max_tokens:
                llm = llm.bind(max_tokens=max_tokens)
            
            # 异步调用模型
            response = await llm.ainvoke(langchain_messages)
            
            # 转换响应格式以保持与之前实现的兼容性
            return {
                "id": "chatcmpl-langchain-async",
                "choices": [{
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": response.content,
                        "role": "assistant"
                    }
                }],
                "model": self.model_name,
                "object": "chat.completion"
            }
        except Exception as e:
            raise Exception(f"调用大模型API失败: {str(e)}")
