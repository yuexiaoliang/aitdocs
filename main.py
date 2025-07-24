import asyncio
import sys
import os
from dotenv import load_dotenv
from ai_document_translator import DocumentTranslator

# 设置环境变量以确保UTF-8编码
os.environ["PYTHONIOENCODING"] = "utf-8"

# 加载.env文件中的环境变量
load_dotenv()


async def main():
    """主函数，演示如何使用文档翻译器"""
    # 确保输出使用UTF-8编码
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8") # type: ignore
        except Exception:
            pass

    try:
        # 创建文档翻译器实例
        doc_translator = DocumentTranslator()
        print("成功初始化文档翻译器")

        # 检查示例文件是否存在
        if not os.path.exists("example-doc.md"):
            # 创建示例文件
            sample_content = """# Introduction
This is a sample document for translation.

## Section 1
This section contains some example text that needs to be translated.

### Subsection
- Item 1
- Item 2
- Item 3

## Section 2
```python
print("Hello, world!")
```

Finally, this is the end of the document."""

            with open("example-doc.md", "w", encoding="utf-8") as f:
                f.write(sample_content)
            print("已创建示例文件 example-doc.md")

        # 翻译单个文档
        try:
            translated_content = await doc_translator.translate_markdown_file(
                "example-doc.md", source_lang="en", target_lang="zh"
            )
            with open("example-doc-zh.md", "w", encoding="utf-8") as f:
                f.write(translated_content)
            print("文档翻译完成，结果保存在 example-doc-zh.md")
        except Exception as e:
            print(f"文档翻译失败: {e}")

        # 递归翻译目录中的所有Markdown文件
        if os.path.exists(".test-data"):
            print("
开始递归翻译 .test-data 目录...")
            try:
                translated_files = await doc_translator.translate_markdown_directory(
                    ".test-data",
                    source_lang="en",
                    target_lang="zh",
                    ignore_patterns=[".test-data/ignore-this-dir/*"],  # 可选的忽略模式
                    output_directory=".test-data-translated"  # 输出目录
                )
                print(f"目录翻译完成，共翻译了 {len(translated_files)} 个文件")
                for file in translated_files:
                    print(f"  - {file}")
            except Exception as e:
                print(f"目录翻译失败: {e}")
        else:
            print("
.test-data 目录不存在，跳过目录翻译示例")

    except Exception as e:
        print(f"初始化文档翻译器时发生错误: {e}")
        print("请检查您的环境变量配置是否正确")


if __name__ == "__main__":
    asyncio.run(main())
