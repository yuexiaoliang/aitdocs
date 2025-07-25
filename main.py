import asyncio
import sys
import os
import argparse
from dotenv import load_dotenv
from ai_document_translator import DocumentTranslator, Translator

# 设置环境变量以确保UTF-8编码
os.environ["PYTHONIOENCODING"] = "utf-8"

# 加载.env文件中的环境变量
load_dotenv()


async def translate_text_content(content: str, source_lang: str, target_lang: str) -> str:
    """翻译文本内容"""
    translator = Translator()
    return await translator.async_translate_text(content, source_lang, target_lang)


async def translate_document(file_path: str, source_lang: str, target_lang: str, output_path: str = None) -> str:
    """翻译单个文档"""
    doc_translator = DocumentTranslator()
    return await doc_translator.translate_markdown_file(file_path, source_lang, target_lang, output_path)


async def translate_directory(
    directory_path: str, 
    source_lang: str, 
    target_lang: str, 
    ignore_patterns: list[str] = None, 
    output_directory: str = None,
    incremental: bool = False,
    auto_commit: bool = False,
    commit_message: str = "Update translated documents",
    auto_push: bool = False
) -> list[str]:
    """翻译目录中的所有Markdown文件"""
    doc_translator = DocumentTranslator()
    return await doc_translator.translate_markdown_directory(
        directory_path, source_lang, target_lang, ignore_patterns, output_directory, 
        incremental, auto_commit, commit_message, auto_push
    )


async def main():
    """主函数，处理命令行参数并执行相应操作"""
    # 确保输出使用UTF-8编码
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="AITdocs - 翻译文本、文档或目录中的Markdown文件")
    
    # 添加互斥参数组（只能选择一种操作）
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument("-t", "--text", help="要翻译的文本内容")
    operation_group.add_argument("-f", "--file", help="要翻译的Markdown文件路径")
    operation_group.add_argument("-d", "--directory", help="要翻译的目录路径")
    
    # 公共参数
    parser.add_argument("-s", "--source-lang", default="auto", help="源语言代码（默认：auto）")
    parser.add_argument("-l", "--target-lang", default="zh", help="目标语言代码（默认：zh）")
    parser.add_argument("-o", "--output", help="输出文件路径（文本/文件模式）或输出目录路径（目录模式）")
    parser.add_argument("-i", "--ignore", nargs="*", help="目录模式下的忽略规则列表")
    parser.add_argument("--incremental", action="store_true", help="启用增量翻译模式（仅翻译变更的文件）")
    parser.add_argument("--auto-commit", action="store_true", help="翻译完成后自动提交到Git仓库")
    parser.add_argument("--commit-message", default="Update translated documents", help="自动提交的提交信息")
    parser.add_argument("--auto-push", action="store_true", help="自动推送到远程仓库（需要先启用--auto-commit）")
    
    args = parser.parse_args()
    
    try:
        # 处理不同的操作类型
        if args.text:
            # 翻译文本内容
            print("正在翻译文本内容...")
            translated_text = await translate_text_content(args.text, args.source_lang, args.target_lang)
            
            if args.output:
                # 写入到输出文件
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(translated_text)
                print(f"翻译完成，结果已保存到 {args.output}")
            else:
                # 直接打印到控制台
                print("翻译结果:")
                print(translated_text)
                
        elif args.file:
            # 翻译单个文件
            if not os.path.exists(args.file):
                print(f"错误: 文件 {args.file} 不存在")
                return 1
                
            print(f"正在翻译文件 {args.file}...")
            translated_content = await translate_document(
                args.file, args.source_lang, args.target_lang, args.output
            )
            
            output_path = args.output or f"{os.path.splitext(args.file)[0]}_{args.target_lang}.md"
            print(f"翻译完成，结果已保存到 {output_path}")
            
        elif args.directory:
            # 翻译目录
            if not os.path.exists(args.directory):
                print(f"错误: 目录 {args.directory} 不存在")
                return 1
                
            print(f"正在递归翻译目录 {args.directory}...")
            translated_files = await translate_directory(
                args.directory, args.source_lang, args.target_lang, args.ignore, args.output, 
                args.incremental, args.auto_commit, args.commit_message, args.auto_push
            )
            
            print(f"目录翻译完成，共翻译了 {len(translated_files)} 个文件:")
            for file in translated_files:
                print(f"  - {file}")
                
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)