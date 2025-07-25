#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增量翻译功能测试脚本
"""

import os
import tempfile
import shutil
import subprocess
from pathlib import Path


def test_incremental_translation():
    """测试增量翻译功能"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")

        # 初始化Git仓库
        subprocess.run(['git', 'init'], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, check=True, capture_output=True)

        # 创建测试文件
        docs_dir = Path(temp_dir) / "docs"
        docs_dir.mkdir()

        # 创建第一个文档
        doc1 = docs_dir / "doc1.md"
        doc1.write_text("# Document 1\n\nThis is the first document.", encoding='utf-8')

        # 提交初始版本
        subprocess.run(['git', 'add', '.'], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir, check=True, capture_output=True)

        # 运行第一次翻译（全量）
        print("第一次翻译（全量）...")
        result = subprocess.run([
            'uv', 'run', 'main.py',
            '-d', str(docs_dir),
            '--incremental'
        ], cwd=os.getcwd(), capture_output=True, text=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)

        # 检查翻译结果
        translated_doc1 = docs_dir / "doc1_zh.md"
        if translated_doc1.exists():
            print("第一次翻译成功")
            print("翻译内容:", translated_doc1.read_text(encoding='utf-8'))
        else:
            print("第一次翻译失败")

        # 修改文档并添加新文档
        doc1.write_text("# Document 1\n\nThis is the updated first document.", encoding='utf-8')

        doc2 = docs_dir / "doc2.md"
        doc2.write_text("# Document 2\n\nThis is the second document.", encoding='utf-8')

        # 提交更改
        subprocess.run(['git', 'add', '.'], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Update docs'], cwd=temp_dir, check=True, capture_output=True)

        # 运行第二次翻译（增量）
        print("\n第二次翻译（增量）...")
        result = subprocess.run([
            'uv', 'run', 'main.py',
            '-d', str(docs_dir),
            '--incremental'
        ], cwd=os.getcwd(), capture_output=True, text=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)

        # 检查翻译结果
        if translated_doc1.exists():
            print("doc1翻译成功")
            print("翻译内容:", translated_doc1.read_text(encoding='utf-8'))

        translated_doc2 = docs_dir / "doc2_zh.md"
        if translated_doc2.exists():
            print("doc2翻译成功")
            print("翻译内容:", translated_doc2.read_text(encoding='utf-8'))
        else:
            print("doc2翻译失败")


if __name__ == "__main__":
    test_incremental_translation()