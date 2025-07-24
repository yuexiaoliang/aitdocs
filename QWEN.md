# AI Document Translator 项目总结

## 项目概述

AI Document Translator 是一个使用阿里云大模型API进行文档翻译的工具。该项目主要实现了以下功能：

1. 与阿里云大模型（如Qwen-Plus）进行交互
2. 提供异步的文本翻译功能
3. 支持多种语言之间的翻译（默认为中英文互译）
4. 支持Markdown文档的翻译，自动处理大文件上下文限制问题
5. 支持递归翻译目录中的所有Markdown文件，并支持忽略规则
6. 提供命令行接口，支持翻译文本、单个文件或整个目录

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
   - 支持单文件和目录递归翻译
   - 支持类似.gitignore的忽略规则
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

4. **目录递归翻译**:
   - 支持递归翻译整个目录中的Markdown文件
   - 支持自定义忽略规则
   - 支持读取.gitignore文件中的忽略规则
   - 可选择输出目录保持原有目录结构

5. **命令行接口**:
   - 支持翻译文本内容、单个文件或整个目录
   - 提供参数来自定义源语言、目标语言等
   - 支持指定输出文件或目录

6. **可配置性**:
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

### 命令行使用

程序支持通过命令行参数来指定要翻译的内容类型：

#### 翻译文本内容

```bash
# 翻译文本内容并输出到控制台
python main.py -t "Hello, world!"

# 翻译文本内容并保存到文件
python main.py -t "Hello, world!" -o translated.txt
```

#### 翻译单个文件

```bash
# 翻译Markdown文件，自动生成输出文件名
python main.py -f document.md

# 翻译Markdown文件并指定输出文件名
python main.py -f document.md -o translated_document.md
```

#### 翻译目录

```bash
# 递归翻译目录中的所有Markdown文件
python main.py -d docs/

# 递归翻译目录并指定输出目录
python main.py -d docs/ -o docs-translated/

# 递归翻译目录并使用忽略规则
python main.py -d docs/ -i "docs/ignore/*" "docs/temp/*"
```

#### 指定语言

所有操作都支持指定源语言和目标语言：

```bash
# 指定源语言和目标语言
python main.py -t "Bonjour le monde!" -s fr -l en
python main.py -f document.md -s en -l zh
python main.py -d docs/ -s auto -l zh
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

### 目录递归翻译

```python
import asyncio
from ai_document_translator import DocumentTranslator

# 递归翻译目录中的所有Markdown文件
async def translate_directory():
    doc_translator = DocumentTranslator()
    translated_files = await doc_translator.translate_markdown_directory(
        "docs/",  # 源目录路径
        source_lang="en",
        target_lang="zh",
        ignore_patterns=["docs/ignore/*"],  # 可选的忽略模式
        output_directory="docs-translated/"  # 可选的输出目录
    )
    return translated_files

asyncio.run(translate_directory())
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
6. 增加重试机制以提高稳定性