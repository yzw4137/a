import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'practice07'))

from tool_client import execute_chained_tool_call, load_env, fetch_webpage, create_file

# 加载环境变量
load_env()

print("=== 测试网页处理链式调用 ===")

# 测试：访问网页并总结页面内容，保存到practice07/summary.txt
user_request = "访问 https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html 并总结页面内容，保存到practice07/summary.txt"
print(f"\n用户请求: {user_request}")
print("\n开始执行链式调用...")

result = execute_chained_tool_call(user_request, max_iterations=5)

print(f"\n最终结果:\n{result}")

# 检查文件是否创建成功
if os.path.exists('practice07/summary.txt'):
    with open('practice07/summary.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"\n✅ 文件已创建，内容预览:\n{content[:500]}...")
else:
    print("\n❌ 文件未创建")

print("\n=== 测试完成 ===")
