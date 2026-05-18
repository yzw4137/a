import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import load_env, call_llm

# 加载环境变量
load_env()

print("环境变量加载完成")
print(f"BASE_URL: {os.getenv('BASE_URL')}")
print(f"MODEL: {os.getenv('MODEL')}")
print(f"API_KEY: {os.getenv('API_KEY')}")

# 测试LLM调用
print("\n测试LLM调用...")
messages = [
    {"role": "system", "content": "你是测试助手"},
    {"role": "user", "content": "请返回JSON格式: {\"done\": true, \"answer\": \"测试成功\"}"}
]

response = call_llm(messages)
print(f"LLM响应: {response}")
