import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import execute_tool_call

# 测试不同的list_directory参数格式
test_cases = [
    {
        "name": "测试1: 使用directory参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "list_directory",
                "arguments": {
                    "directory": "."
                }
            }
        }
    },
    {
        "name": "测试2: 使用path参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "list_directory",
                "arguments": {
                    "path": "."
                }
            }
        }
    },
    {
        "name": "测试3: 使用practice07目录",
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

print("=== 测试list_directory参数解析 ===")
for test_case in test_cases:
    print(f"\n{test_case['name']}")
    print(f"参数: {test_case['tool_call']['function']['arguments']}")
    result = execute_tool_call(test_case['tool_call'])
    print(f"结果: {result[:300]}..." if len(result) > 300 else f"结果: {result}")
