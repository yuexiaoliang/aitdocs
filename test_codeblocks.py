#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试代码块处理功能
"""

import tempfile
import os
from ai_document_translator.document_translator import DocumentTranslator


def test_codeblock_splitting():
    """测试代码块分割功能"""
    # 创建测试内容，包含各种情况
    test_content = """# 文档标题

这是文档的第一段内容。

## 代码示例

下面是一些代码示例：

```python
def hello_world():
    print("Hello, World!")
    for i in range(10):
        print(f"Count: {i}")

# 这是一个很长的函数，用于测试代码块分割功能
def long_function():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    return x + y + z + a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q
```

这是代码之后的段落内容。

### 另一个代码示例

```javascript
function greet(name) {
    console.log("Hello, " + name + "!");
}

greet("World");

const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log(doubled);
```

结尾段落。
"""

    # 创建文档翻译器实例
    translator = DocumentTranslator(chunk_size=200)  # 使用较小的块大小便于测试
    
    # 分割内容
    chunks = translator._split_markdown_content(test_content)
    
    print(f"原始内容大小: {len(test_content)} 字符")
    print(f"分割为 {len(chunks)} 个块:")
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- 块 {i+1} (大小: {len(chunk)} 字符) ---")
        print(repr(chunk))
        print(chunk)
        
        # 验证代码块完整性
        code_block_count = chunk.count("```")
        if code_block_count % 2 != 0:
            print("警告: 检测到可能不完整的代码块!")
    
    # 测试更大的块大小
    print("\n" + "="*50)
    print("使用更大的块大小测试:")
    
    translator_large = DocumentTranslator(chunk_size=500)
    chunks_large = translator_large._split_markdown_content(test_content)
    
    print(f"分割为 {len(chunks_large)} 个块:")
    
    for i, chunk in enumerate(chunks_large):
        print(f"\n--- 块 {i+1} (大小: {len(chunk)} 字符) ---")
        print(chunk)
        
        # 验证代码块完整性
        code_block_count = chunk.count("```")
        if code_block_count % 2 != 0:
            print("警告: 检测到可能不完整的代码块!")


if __name__ == "__main__":
    test_codeblock_splitting()