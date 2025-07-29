# AITdocs

AITdocs 是一个使用阿里云大模型API进行文档翻译的工具。

## 项目结构

```
ai-document-translator/
├── ai_document_translator/
│   ├── __init__.py
│   ├── model_client.py     # 大模型交互模块
│   ├── translator.py       # 翻译模块
│   ├── document_translator.py  # 文档翻译模块
│   ├── build_manager.py    # 构建环境管理模块
│   └── build_cli.py        # 构建环境管理命令行接口
├── .env                    # 环境变量配置文件
├── .env.example            # 环境变量配置模板
├── .gitignore
├── .aitdocsignore          # AITdocs忽略规则文件
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

# 增量翻译目录（仅翻译变更的文件）
python main.py -d docs/ --incremental

# 翻译后自动提交到Git仓库
python main.py -d docs/ --auto-commit

# 自定义提交信息
python main.py -d docs/ --auto-commit --commit-message "翻译更新：用户手册"

# 自动推送翻译结果到远程仓库
python main.py -d docs/ --auto-commit --auto-push

# 使用所有自动化功能
python main.py -d docs/ --incremental --auto-commit --auto-push
```

### 构建环境管理

在文档翻译完成后，您可能需要在构建过程中使用翻译后的文件替换原始文件。为此，我们提供了构建环境管理功能：

#### 通过主程序使用

```bash
# 准备构建环境：将源文件替换为翻译后的文件
python main.py -b prepare

# 恢复构建环境：将备份的原始文件还原
python main.py -b restore

# 使用自定义备份后缀
python main.py -b prepare --backup-suffix ".backup"
```

#### 通过独立命令行工具使用

除了通过主程序使用构建环境管理功能外，您还可以直接使用独立的命令行工具：

```bash
# 准备构建环境
python -m ai_document_translator.build_cli prepare

# 恢复构建环境
python -m ai_document_translator.build_cli restore

# 指定目录和目标语言
python -m ai_document_translator.build_cli prepare -d docs/ -l zh

# 使用自定义备份后缀
python -m ai_document_translator.build_cli prepare -s ".backup"
```

构建环境管理的工作原理：
1. `prepare` 命令会备份原始文件，并用对应的翻译文件替换原始文件
2. `restore` 命令会将备份的原始文件还原，删除替换的翻译文件
3. 备份文件默认使用 `.aitdocs.bak` 后缀，可通过 `--backup-suffix` 参数自定义

使用场景示例：
```bash
# 1. 翻译文档
python main.py -d docs/ --incremental

# 2. 准备构建环境
python main.py -b prepare

# 3. 执行构建过程（如生成文档网站）
# your-build-command

# 4. 恢复构建环境
python main.py -b restore
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

# 忽略已翻译的文件（避免重复翻译）
*_zh.md
*_en.md
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

### 增量翻译模式

对于Git仓库中的文档目录，您可以使用增量翻译模式来仅翻译自上次翻译以来变更的文件。此功能通过比较Git提交历史来确定哪些文件需要重新翻译：

```bash
# 使用增量模式翻译目录
python main.py -d docs/ --incremental

# 结合其他选项使用增量模式
python main.py -d docs/ --incremental -l en -o docs-translated/
```

增量翻译模式的工作原理：
1. 首次运行时，会进行全量翻译并在目录中创建一个状态文件（.aitdocs_state）记录当前Git提交哈希和忽略规则
2. 后续运行时，会比较当前Git提交与上次记录的提交之间的差异
3. 同时检查忽略规则是否发生变化
4. 仅翻译变更过的Markdown文件
5. 更新状态文件中的提交哈希和忽略规则哈希

注意事项：
- 目标目录必须是Git仓库
- 需要系统中安装了Git命令行工具
- 如果Git命令执行失败，将自动回退到全量翻译模式
- 当忽略规则（包括命令行参数、.gitignore文件和.aitdocsignore文件）发生变化时，会自动进行全量翻译，确保之前被忽略的文件能够被正确处理

### 自动提交和推送翻译结果

翻译完成后，您可以选择将翻译结果自动提交到Git仓库并推送到远程仓库：

```bash
# 翻译后自动提交
python main.py -d docs/ --auto-commit

# 使用自定义提交信息
python main.py -d docs/ --auto-commit --commit-message "自动翻译：更新用户文档"

# 自动推送（需要同时启用自动提交）
python main.py -d docs/ --auto-commit --auto-push

# 结合增量翻译使用
python main.py -d docs/ --incremental --auto-commit --auto-push
```

自动提交功能会将所有新生成的翻译文件添加到Git暂存区并提交，自动推送功能会将提交推送到远程仓库，方便团队协作和版本管理。

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
        output_directory="docs-translated/",  # 可选的输出目录
        incremental=True,  # 启用增量翻译模式
        auto_commit=True,  # 启用自动提交
        commit_message="自动翻译：更新文档",  # 提交信息
        auto_push=True  # 启用自动推送
    )
    return translated_files

asyncio.run(translate_directory())
```

文档翻译器会自动处理大文件，将其分割为适当的块以适应模型的上下文长度限制，同时保持Markdown格式的完整性。目录翻译功能支持类似.gitignore的忽略规则。

在分割大文档时，翻译器会特别注意保护代码块的完整性，确保：
- 代码块（使用```或~~~标记的）不会被分割到不同的片段中
- 表格等复杂结构尽可能保持完整
- 标题作为分割点的自然边界

## 构建环境管理（编程接口）

除了命令行接口外，您还可以在代码中使用构建环境管理功能：

```python
from ai_document_translator.build_manager import BuildManager

# 创建构建管理器实例
build_manager = BuildManager(
    directory_path="docs/",
    target_lang="zh",
    backup_suffix=".aitdocs.bak"
)

# 准备构建环境
backed_up_files = build_manager.prepare_build_environment()

# 恢复构建环境
build_manager.restore_build_environment()
```

## 依赖说明

本项目使用以下主要依赖：

- `langchain`: 用于构建应用程序的语言模型框架
- `langchain-openai`: LangChain的OpenAI集成
- `python-dotenv`: 用于加载环境变量