import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import execute_chained_tool_call, load_env, ChainedCallContext, list_files, read_file

# 加载环境变量
load_env()

print("=== 测试链式调用修复 ===")

# 手动测试文件读取
print("\n1. 手动测试文件读取:")
dir_result = list_files('practice07')
print(f"目录列表: {dir_result[:500]}")

# 测试读取test01和test02
test01_content = read_file('practice07', 'test01')
test02_content = read_file('practice07', 'test02')
print(f"\ntest01内容: {test01_content}")
print(f"test02内容: {test02_content}")

# 测试自动计算逻辑
print("\n2. 测试自动计算逻辑:")
context = ChainedCallContext(max_iterations=10)

# 模拟读取两个文件的内容
file_contents = [
    {'arguments': {'path': 'practice07/test01'}, 'content': '123'},
    {'arguments': {'path': 'practice07/test02'}, 'content': '123'}
]
context.set_variable('file_contents', file_contents)

# 模拟用户请求
user_request = "访问practice07文件夹下的test01和test02文件，将他们的内容之和计算出来返回给我"

# 测试自动计算逻辑
print(f"\n用户请求: {user_request}")
print(f"file_contents长度: {len(file_contents)}")
print(f"'之和' in user_request: {'之和' in user_request}")

if len(file_contents) >= 2 and ('相加' in user_request or '之和' in user_request or '和' in user_request):
    print("检测到需要计算多个文件内容之和...")
    try:
        total = 0
        content_list = []
        for fc in file_contents:
            content = fc.get('content', '').strip()
            if content.isdigit():
                num = int(content)
                total += num
                content_list.append(f"{fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: {num}")
            else:
                content_list.append(f"{fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: '{content}' (非数字)")
        
        if content_list:
            answer = f"计算结果：\n"
            answer += "\n".join(content_list) + "\n"
            answer += f"总和: {total}"
            print(f"最终回答: {answer}")
    except Exception as e:
        print(f"自动计算失败: {str(e)}")

print("\n=== 测试完成 ===")
