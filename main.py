import asyncio
import sys
import os
from dotenv import load_dotenv
from ai_document_translator.model_client import ModelClient

# 设置环境变量以确保UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 加载.env文件中的环境变量
load_dotenv()


def main():
    """主函数，演示如何使用模型客户端"""
    # 确保输出使用UTF-8编码
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8') # type: ignore
        except Exception:
            pass

    print("AI Document Translator")
    print("======================")

    try:
        # 创建模型客户端实例
        client = ModelClient()
        print(f"成功初始化模型客户端，使用模型: {client.model_name}")

        # 示例1: 同步调用
        print("\n1. 同步调用示例:")
        messages = [{"role": "user", "content": "你好，这是一个测试消息。"}]
        try:
            response = client.chat_completions(messages)
            # 提取并打印回复内容
            content = response["choices"][0]["message"]["content"]
            print(f"回复内容: {content}")
        except Exception as e:
            print(f"同步调用失败: {e}")
            print("请检查您的API密钥是否正确配置")

        # 示例2: 异步调用
        print("\n2. 异步调用示例:")

        async def async_call():
            messages = [
                {
                    "role": "user",
                    "content": "请翻译以下英文句子: Hello, how are you today?",
                }
            ]
            try:
                response = await client.async_chat_completions(messages)
                # 提取并打印回复内容
                content = response["choices"][0]["message"]["content"]
                print(f"回复内容: {content}")
            except Exception as e:
                print(f"异步调用失败: {e}")
                print("请检查您的API密钥是否正确配置")

        asyncio.run(async_call())

    except Exception as e:
        print(f"初始化模型客户端时发生错误: {e}")
        print("请检查您的环境变量配置是否正确")


if __name__ == "__main__":
    main()
