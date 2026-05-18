import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import execute_tool_call, ChainedCallContext

# 测试1：测试read_file参数解析
print("=== 测试read_file参数解析 ===")
test_cases = [
    {
        "name": "使用file_path参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "file_path": "practice07/test01"
                }
            }
        }
    },
    {
        "name": "使用filepath参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "filepath": "practice07/test02"
                }
            }
        }
    }
]

for test_case in test_cases:
    print(f"\n{test_case['name']}")
    print(f"参数: {test_case['tool_call']['function']['arguments']}")
    result = execute_tool_call(test_case['tool_call'])
    print(f"结果: {result}")

# 测试2：测试list_directory参数解析
print("\n=== 测试list_directory参数解析 ===")
test_cases = [
    {
        "name": "使用folder_path参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "list_directory",
                "arguments": {
                    "folder_path": "practice07"
                }
            }
        }
    },
    {
        "name": "使用directory参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "list_directory",
                "arguments": {
                    "directory": "practice07"
                }
            }
        }
    }
]

for test_case in test_cases:
    print(f"\n{test_case['name']}")
    print(f"参数: {test_case['tool_call']['function']['arguments']}")
    result = execute_tool_call(test_case['tool_call'])
    print(f"结果: {result[:300]}..." if len(result) > 300 else f"结果: {result}")

# 测试3：测试ChainedCallContext的get_variable方法
print("\n=== 测试ChainedCallContext.get_variable方法 ===")
context = ChainedCallContext(max_iterations=10)
context.set_variable('test_key', 'test_value')

print(f"get_variable('test_key'): {context.get_variable('test_key')}")
print(f"get_variable('non_existent', 'default_value'): {context.get_variable('non_existent', 'default_value')}")
print(f"get_variable('non_existent'): {context.get_variable('non_existent')}")
