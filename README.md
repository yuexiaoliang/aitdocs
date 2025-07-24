# AITdocs

AITdocs 是一个使用阿里云大模型API进行文档翻译的工具。

## 项目结构

```
ai-document-translator/
├── ai_document_translator/
│   ├── __init__.py
│   ├── model_client.py     # 大模型交互模块
│   ├── translator.py       # 翻译模块
│   └── document_translator.py  # 文档翻译模块
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

或者使用 pip 安装：

```bash
pip install python-dotenv langchain langchain-openai
```

## 命令行使用

程序支持通过命令行参数来指定要翻译的内容类型：

### 翻译文本内容

```bash
# 翻译文本内容并输出到控制台
python main.py -t "Hello, world!"

# 翻译文本内容并保存到文件
python main.py -t "Hello, world!" -o translated.txt
```

### 翻译单个文件

```bash
# 翻译Markdown文件，自动生成输出文件名
python main.py -f document.md

# 翻译Markdown文件并指定输出文件名
python main.py -f document.md -o translated_document.md
```

### 翻译目录

```bash
# 递归翻译目录中的所有Markdown文件
python main.py -d docs/

# 递归翻译目录并指定输出目录
python main.py -d docs/ -o docs-translated/

# 递归翻译目录并使用忽略规则
python main.py -d docs/ -i "docs/ignore/*" "docs/temp/*"
```

### 使用.aitdocsignore文件

除了在命令行中指定忽略规则外，您还可以在要翻译的目录中创建一个`.aitdocsignore`文件来指定忽略规则。该文件的格式与`.gitignore`类似，每行一个忽略模式。

例如，创建一个名为`.aitdocsignore`的文件，内容如下：
```
# 忽略临时文件
temp/
*.tmp

# 忽略特定目录
ignore/
```

当您运行目录翻译命令时，程序会自动读取该文件中的忽略规则：
```bash
python main.py -d docs/
```

### 指定语言

所有操作都支持指定源语言和目标语言：

```bash
# 指定源语言和目标语言
python main.py -t "Bonjour le monde!" -s fr -l en
python main.py -f document.md -s en -l zh
python main.py -d docs/ -s auto -l zh
```

## 编程接口使用

### 使用模型客户端

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

### 使用翻译模块

项目提供了翻译模块，可以更方便地进行文本翻译（仅支持异步API）：

```python
from ai_document_translator import Translator, async_translate
import asyncio

# 方法1: 使用Translator类
async def translate_with_class():
    translator = Translator()
    result = await translator.async_translate_text("Hello, world!", source_lang="en", target_lang="zh")
    return result

# 方法2: 使用async_translate函数
async def async_translate_example():
    result = await async_translate("Hello, world!", source_lang="en", target_lang="zh")
    return result

# 运行异步函数
asyncio.run(translate_with_class())
asyncio.run(async_translate_example())
```

### 文档翻译功能

项目还提供了文档翻译功能，专门用于翻译Markdown格式的文档：

#### 翻译单个文件

```python
from ai_document_translator import DocumentTranslator
import asyncio

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

#### 递归翻译整个目录

```python
from ai_document_translator import DocumentTranslator
import asyncio

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

文档翻译器会自动处理大文件，将其分割为适当的块以适应模型的上下文长度限制，同时保持Markdown格式的完整性。目录翻译功能支持类似.gitignore的忽略规则。

## 依赖说明

本项目使用以下主要依赖：

- `langchain`: 用于构建应用程序的语言模型框架
- `langchain-openai`: LangChain的OpenAI集成
- `python-dotenv`: 用于加载环境变量