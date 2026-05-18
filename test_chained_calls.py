import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入 practice07 的 tool_client 模块
from practice07.tool_client import execute_chained_tool_call, load_env

def main():
    # 加载环境变量
    load_env()
    
    print("=== 链式工具调用测试 ===")
    print("=" * 50)
    
    # 测试1：文件搜索链式调用
    print("测试1：文件搜索链式调用")
    print("请求：请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容")
    print("-" * 50)
    try:
        result1 = execute_chained_tool_call("请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容")
        print(f"结果: {result1}")
    except Exception as e:
        print(f"测试1失败: {str(e)}")
    print()
    
    # 测试2：技能查询链式调用
    print("测试2：技能查询链式调用")
    print("请求：我想了解notice技能的详细规则")
    print("-" * 50)
    try:
        result2 = execute_chained_tool_call("我想了解notice技能的详细规则")
        print(f"结果: {result2}")
    except Exception as e:
        print(f"测试2失败: {str(e)}")
    print()
    
    # 测试3：网页处理链式调用
    print("测试3：网页处理链式调用")
    print("请求：访问 https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html 并总结页面内容，保存到practice07/summary.txt")
    print("-" * 50)
    try:
        result3 = execute_chained_tool_call("访问 https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html 并总结页面内容，保存到practice07/summary.txt")
        print(f"结果: {result3}")
        
        # 检查是否创建了文件
        summary_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'practice07', 'summary.txt')
        if os.path.exists(summary_file):
            print(f"总结文件已创建: {summary_file}")
            with open(summary_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"文件内容预览: {content[:300]}...")
        else:
            print("总结文件未创建")
    except Exception as e:
        print(f"测试3失败: {str(e)}")
    print()
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main()
