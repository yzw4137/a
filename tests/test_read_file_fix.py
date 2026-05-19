import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import execute_tool_call

# 测试不同的read_file参数格式
test_cases = [
    {
        "name": "测试1: 使用filepath参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "filepath": "test01.txt"
                }
            }
        }
    },
    {
        "name": "测试2: 使用directory和file_name参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "directory": ".",
                    "file_name": "test01.txt"
                }
            }
        }
    },
    {
        "name": "测试3: 使用path参数",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "path": "test01.txt"
                }
            }
        }
    },
    {
        "name": "测试4: 使用完整路径",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "filepath": "./test01.txt"
                }
            }
        }
    },
    {
        "name": "测试5: 使用Windows路径格式",
        "tool_call": {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "filepath": "test01.txt"
                }
            }
        }
    }
]

print("=== 测试read_file参数解析 ===")
for test_case in test_cases:
    print(f"\n{test_case['name']}")
    print(f"参数: {test_case['tool_call']['function']['arguments']}")
    result = execute_tool_call(test_case['tool_call'])
    print(f"结果: {result[:200]}..." if len(result) > 200 else f"结果: {result}")
