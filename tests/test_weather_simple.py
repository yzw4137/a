# 简单测试脚本
import os
import json
import urllib.request
from urllib.parse import urlparse, quote, urlunparse

# 测试函数
def test_weather():
    print("测试天气查询功能...")
    print("=" * 50)
    
    # 测试用例：查询青城山天气（使用 wttr.in）
    url = "https://wttr.in/青城山?lang=zh&format=3"
    print(f"查询 URL: {url}")
    
    # 解析URL并编码
    parsed_url = urlparse(url)
    path = quote(parsed_url.path) if parsed_url.path else ''
    query = quote(parsed_url.query, safe='=&') if parsed_url.query else ''
    
    encoded_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        path,
        parsed_url.params,
        query,
        parsed_url.fragment
    ))
    
    print(f"编码后 URL: {encoded_url}")
    
    # 尝试访问URL
    try:
        with urllib.request.urlopen(encoded_url, timeout=30) as response:
            content = response.read().decode('utf-8', errors='replace')
        print(f"响应内容: {content}")
        print("查询成功！")
    except Exception as e:
        print(f"查询失败: {str(e)}")

if __name__ == "__main__":
    test_weather()
