import argparse
import sys
import os
from .build_manager import BuildManager


def main():
    """构建环境管理命令行工具"""
    parser = argparse.ArgumentParser(description="构建环境管理工具")
    parser.add_argument("action", choices=["prepare", "restore"], help="操作类型: prepare(准备) 或 restore(恢复)")
    parser.add_argument("-d", "--directory", default=".", help="目录路径 (默认: 当前目录)")
    parser.add_argument("-l", "--target-lang", default="zh", help="目标语言代码 (默认: zh)")
    parser.add_argument("-s", "--backup-suffix", default=".aitdocs.bak", help="备份文件后缀 (默认: .aitdocs.bak)")

    args = parser.parse_args()

    try:
        # 创建构建管理器
        build_manager = BuildManager(
            directory_path=args.directory,
            target_lang=args.target_lang,
            backup_suffix=args.backup_suffix
        )

        if args.action == "prepare":
            print(f"正在准备构建环境: {args.directory}")
            backed_up_files = build_manager.prepare_build_environment()
            print(f"准备完成，共处理 {len(backed_up_files)} 个文件")
            
        elif args.action == "restore":
            print(f"正在恢复构建环境: {args.directory}")
            build_manager.restore_build_environment()
            print("恢复完成")

    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())