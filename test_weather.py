import os
import json
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入 practice06 的 tool_client 模块
from practice06.tool_client import fetch_webpage

# 测试天气查询
print("测试天气查询功能...")
print("=" * 50)

# 测试用例1：查询青城山天气（使用 wttr.in）
print("测试1：查询青城山天气（使用 wttr.in）")
url1 = "https://wttr.in/青城山?lang=zh&format=3"
result1 = fetch_webpage(url1)
print(f"URL: {url1}")
try:
    # 解析 JSON 结果
    data1 = json.loads(result1)
    print(f"状态: {data1.get('status')}")
    if data1.get('status') == 'success':
        content = data1.get('data', '')
        # 尝试打印内容，如果有编码错误则只打印长度
        try:
            print(f"内容: {content}")
        except UnicodeEncodeError:
            print(f"内容长度: {len(content)} 字符")
            print("内容包含 Unicode 字符，无法在当前终端显示")
except json.JSONDecodeError:
    print(f"结果: {result1}")
print()

# 测试用例2：查询北京天气（使用 wttr.in）
print("测试2：查询北京天气（使用 wttr.in）")
url2 = "https://wttr.in/北京?lang=zh&format=3"
result2 = fetch_webpage(url2)
print(f"URL: {url2}")
try:
    # 解析 JSON 结果
    data2 = json.loads(result2)
    print(f"状态: {data2.get('status')}")
    if data2.get('status') == 'success':
        content = data2.get('data', '')
        # 尝试打印内容，如果有编码错误则只打印长度
        try:
            print(f"内容: {content}")
        except UnicodeEncodeError:
            print(f"内容长度: {len(content)} 字符")
            print("内容包含 Unicode 字符，无法在当前终端显示")
except json.JSONDecodeError:
    print(f"结果: {result2}")
print()

# 测试用例3：使用中国天气网
print("测试3：使用中国天气网")
url3 = "https://www.weather.com.cn/weather/101290100.html"
result3 = fetch_webpage(url3)
print(f"URL: {url3}")
try:
    # 解析 JSON 结果
    data3 = json.loads(result3)
    print(f"状态: {data3.get('status')}")
    if data3.get('status') == 'success':
        content = data3.get('data', '')
        print(f"内容长度: {len(content)} 字符")
        print("内容预览:", content[:200] + "..." if len(content) > 200 else content)
except json.JSONDecodeError:
    print(f"结果: {result3}")
print()

print("测试完成！")
