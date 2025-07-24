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

        # 翻译文档
        try:
            await doc_translator.translate_markdown_file(
                ".test-data/reference/chroma-reference.md", source_lang="en", target_lang="zh"
            )
            print("文档翻译完成，结果保存在 example-doc-zh.md")
        except Exception as e:
            print(f"文档翻译失败: {e}")

    except Exception as e:
        print(f"初始化文档翻译器时发生错误: {e}")
        print("请检查您的环境变量配置是否正确")


if __name__ == "__main__":
    asyncio.run(main())
