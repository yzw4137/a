import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import execute_chained_tool_call, load_env

# 加载环境变量
load_env()

print("=== 测试修复后的计算功能 ===")

# 测试：访问practice07文件夹下的test01和test02文件，将他们的内容之和计算出来返回给我
user_request = "访问practice07文件夹下的test01和test02文件，将他们的内容之和计算出来返回给我"
print(f"\n用户请求: {user_request}")
print("\n开始执行链式调用...")

result = execute_chained_tool_call(user_request, max_iterations=5)

print(f"\n最终结果: {result}")

# 验证结果是否正确
if "总和: 246" in result:
    print("\n✅ 计算正确！")
else:
    print("\n❌ 计算结果不正确，期望246")

print("\n=== 测试完成 ===")
