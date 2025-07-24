# AI Document Translator

AI Document Translator 是一个使用阿里云大模型API进行文档翻译的工具。

## 项目结构

```
ai-document-translator/
├── ai_document_translator/
│   ├── __init__.py
│   └── model_client.py     # 大模型交互模块
├── .env                    # 环境变量配置文件
├── .env.example            # 环境变量配置模板
├── .gitignore
├── main.py                 # 主程序入口
├── pyproject.toml          # 项目配置文件
└── README.md               # 项目说明文件
```

## 环境配置

1. 复制 `.env.example` 文件为 `.env`:
   ```
   cp .env.example .env
   ```

2. 在 `.env` 文件中设置以下环境变量：
   ```
   ALI_BASE_URL=https://dashscope.aliyuncs.com/api/v1
   ALI_MODEL_NAME=qwen-plus
   ALI_API_KEY=your_api_key_here
   ```

3. 从阿里云获取API密钥：
   - 访问 [阿里云DashScope](https://dashscope.console.aliyun.com/)
   - 创建API密钥
   - 将API密钥替换到 `.env` 文件中的 `your_api_key_here`

## 安装依赖

使用 uv 安装项目依赖：

```bash
uv sync
```

## 运行程序

```bash
uv run python main.py
```

## 使用模型客户端

在代码中使用 `ModelClient` 类与大模型进行交互：

```python
from ai_document_translator.model_client import ModelClient

# 创建客户端实例
client = ModelClient()

# 同步调用
messages = [{"role": "user", "content": "你好，世界！"}]
response = client.chat_completions(messages)

# 异步调用
import asyncio
async def async_call():
    messages = [{"role": "user", "content": "你好，世界！"}]
    response = await client.async_chat_completions(messages)
    return response

asyncio.run(async_call())
```

## 依赖说明

本项目使用以下主要依赖：

- `openai`: 用于与大模型API交互的官方Python SDK
- `python-dotenv`: 用于加载环境变量