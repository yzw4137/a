import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import execute_chained_tool_call

# 测试1：访问test01和test02文件，把内容数字相加
print("=== 测试1：文件内容数字相加 ===")
result = execute_chained_tool_call("请访问test01和test02两个文件，把他们的内容数字相加，把结果告诉我")
print(f"测试1结果: {result}")
print()

# 测试2：查找practice06目录下包含'def'关键词的文件并总结
print("=== 测试2：文件搜索链式调用 ===")
result = execute_chained_tool_call("请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容")
print(f"测试2结果: {result}")
