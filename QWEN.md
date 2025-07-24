# AI Document Translator 项目总结

## 项目概述

AI Document Translator 是一个使用阿里云大模型API进行文档翻译的工具。该项目主要实现了以下功能：

1. 与阿里云大模型（如Qwen-Plus）进行交互
2. 提供异步的文本翻译功能
3. 支持多种语言之间的翻译（默认为中英文互译）
4. 支持Markdown文档的翻译，自动处理大文件上下文限制问题

## 技术架构

### 核心组件

1. **ModelClient**: 大模型交互模块，封装了与阿里云API的通信
   - 支持同步和异步调用
   - 使用LangChain框架简化API交互

2. **Translator**: 翻译模块，提供更高级的文本翻译接口
   - 封装了翻译相关的业务逻辑
   - 支持自定义系统提示词
   - 仅支持异步调用

3. **DocumentTranslator**: 文档翻译模块，专门用于翻译Markdown文档
   - 自动处理大文件分段翻译
   - 保持Markdown格式完整性
   - 仅支持异步调用

4. **辅助函数**: 提供便捷的翻译函数
   - `async_translate()`: 异步文本翻译函数

### 技术栈

- Python 3.12+
- uv 包管理器
- LangChain 框架
- dotenv 环境变量管理

## 功能特性

1. **多语言翻译**:
   - 默认支持中英文互译
   - 可通过参数指定源语言和目标语言
   - 支持自动语言检测

2. **异步调用**:
   - 所有翻译功能都基于异步API实现
   - 提高了程序的性能和响应能力

3. **文档翻译**:
   - 专门支持Markdown文档翻译
   - 自动处理大文件分段，避免超出模型上下文长度限制
   - 保持原有Markdown格式

4. **可配置性**:
   - 通过环境变量配置API密钥和模型参数
   - 支持自定义系统提示词
   - 可调整模型温度等参数

## 使用方法

### 环境配置

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中配置阿里云API密钥:
   ```
   ALI_BASE_URL=https://dashscope.aliyuncs.com/api/v1
   ALI_MODEL_NAME=qwen-plus
   ALI_API_KEY=your_api_key_here
   ```

### 安装依赖

使用 uv 安装依赖:
```bash
uv sync
```

### 运行程序

```bash
uv run python main.py
```

## 项目结构

```
ai-document-translator/
├── ai_document_translator/
│   ├── __init__.py
│   ├── model_client.py     # 大模型交互模块
│   ├── translator.py       # 文本翻译模块（仅异步API）
│   └── document_translator.py  # 文档翻译模块
├── .env                    # 环境变量配置文件
├── .env.example            # 环境变量配置模板
├── .gitignore
├── main.py                 # 主程序入口（异步版本）
├── pyproject.toml          # 项目配置文件
└── README.md               # 项目说明文件
```

## 代码示例

### 异步文本翻译

```python
import asyncio
from ai_document_translator import Translator, async_translate

# 使用Translator类
async def translate_with_class():
    translator = Translator()
    result = await translator.async_translate_text("Hello, world!", source_lang="en", target_lang="zh")
    return result

# 使用async_translate函数
async def async_translate_example():
    result = await async_translate("Hello, world!", source_lang="en", target_lang="zh")
    return result

# 运行异步函数
asyncio.run(translate_with_class())
asyncio.run(async_translate_example())
```

### 文档翻译

```python
import asyncio
from ai_document_translator import DocumentTranslator

# 翻译Markdown文件
async def translate_document():
    doc_translator = DocumentTranslator()
    translated_content = await doc_translator.translate_markdown_file(
        "document.md",  # 源文件路径
        source_lang="en", 
        target_lang="zh"
    )
    return translated_content

asyncio.run(translate_document())
```

### 自定义系统提示词

```python
import asyncio
from ai_document_translator import Translator

async def custom_prompt_translate():
    translator = Translator()
    result = await translator.async_translate_text(
        "Hello, world!", 
        source_lang="en", 
        target_lang="zh",
        system_prompt="你是一个专业的技术文档翻译助手，请保持技术术语的准确性。"
    )
    return result

asyncio.run(custom_prompt_translate())
```

## 未来发展建议

1. 增加更多语言支持
2. 实现更多文档格式（如PDF、Word）的直接翻译功能
3. 添加翻译历史记录和缓存机制
4. 提供Web界面或API接口
5. 改进文档翻译的分段算法，更好地保持语义完整性