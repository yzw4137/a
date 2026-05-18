import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import ChainedCallContext, parse_llm_response, extract_json, build_analysis_prompt

# 测试1：测试extract_json函数
print("=== 测试extract_json函数 ===")
test_cases = [
    '{"done": true, "answer": "test"}',
    '```json\n{"done": false, "tool_call": {"name": "read_file", "arguments": {"file": "test.txt"}}}\n```',
    '```\n{"done": true}\n```',
    'invalid json'
]

for i, test in enumerate(test_cases):
    result = extract_json(test)
    print(f"测试{i+1}: {result}")

# 测试2：测试parse_llm_response函数
print("\n=== 测试parse_llm_response函数 ===")

# 测试空响应
result = parse_llm_response(None)
print(f"空响应: {result}")

# 测试有效JSON响应
result = parse_llm_response('{"done": true, "answer": "测试完成"}')
print(f"有效JSON: {result}")

# 测试工具调用格式
result = parse_llm_response({"choices": [{"message": {"tool_calls": [{"type": "function", "function": {"name": "read_file", "arguments": {"file": "test.txt"}}}]}}]})
print(f"工具调用格式: {result}")

# 测试解析失败时作为最终回答
result = parse_llm_response('{"done": true}')
print(f"无answer字段: {result}")

# 测试非JSON响应（作为最终回答）
result = parse_llm_response('这是一个普通文本响应')
print(f"普通文本: {result}")

# 测试3：测试ChainedCallContext
print("\n=== 测试ChainedCallContext ===")
context = ChainedCallContext(max_iterations=3)
print(f"初始迭代: {context.current_iteration}")
print(f"有更多迭代: {context.has_more_iterations()}")

context.add_step('read_file', {'file': 'test.txt'}, '{"status": "success", "data": "42"}')
context.set_variable('content', '42')
context.increment_iteration()

print(f"迭代后: {context.current_iteration}")
print(f"有更多迭代: {context.has_more_iterations()}")
print(f"变量: {context.get_variable('content')}")
print(f"步骤: {len(context.steps)}")

context.increment_iteration()
context.increment_iteration()
print(f"达到最大迭代后: {context.has_more_iterations()}")

print("\n=== 测试完成 ===")
