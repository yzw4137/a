import os
import json
import time
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

# 从.env文件加载环境变量
def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    print(f"Loading environment from: {env_file}")
    if os.path.exists(env_file):
        print("Found .env file, loading...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"Loaded: {key.strip()} = {'***' if 'KEY' in key.upper() else value.strip()}")
    else:
        print("No .env file found, using system environment variables")

# 加载环境变量
load_env()

# 从环境变量获取配置
BASE_URL = os.getenv('BASE_URL', 'https://api.openai.com/v1')
MODEL = os.getenv('MODEL', 'gpt-3.5-turbo')
API_KEY = os.getenv('API_KEY')
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))

print("\n=== Configuration ===")
print(f"BASE_URL: {BASE_URL}")
print(f"MODEL: {MODEL}")
print(f"API_KEY: {'***' if API_KEY else 'Not set'}")
print(f"TEMPERATURE: {TEMPERATURE}")
print(f"MAX_TOKENS: {MAX_TOKENS}")

# 检查必要的配置
if not API_KEY:
    print("\nError: API_KEY is required. Please set it in .env file.")
    exit(1)

# 解析URL
parsed_url = urlparse(BASE_URL)
scheme = parsed_url.scheme
host = parsed_url.netloc
path = parsed_url.path or '/'

print(f"\n=== URL Parsing ===")
print(f"Scheme: {scheme}")
print(f"Host: {host}")
print(f"Path: {path}")

# 测试提示词
prompt = "Hello, how are you?"

# 构建请求数据
request_data = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": TEMPERATURE,
    "max_tokens": MAX_TOKENS
}

# 计算输入token数（简化计算，实际应该使用tiktoken库）
input_tokens = len(prompt.split()) * 1.3  # 粗略估算

print("\n=== LLM API Access Test ===")
print(f"Prompt: {prompt}")
print(f"Estimated input tokens: {input_tokens:.0f}")
print("\nSending request...")
print("Note: This is a test script. You need to set a valid API_KEY in .env file to make actual API calls.")

# 记录开始时间
start_time = time.time()

# 发送HTTP请求
try:
    print(f"\nConnecting to: {scheme}://{host}")
    # 根据协议选择连接类型
    if scheme == 'https':
        conn = HTTPSConnection(host)
    else:
        conn = HTTPConnection(host)
    
    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    # 发送POST请求
    conn.request('POST', f"{path}/chat/completions", json.dumps(request_data), headers)
    print("Request sent successfully")
    
    # 获取响应
    response = conn.getresponse()
    print(f"Response status: {response.status} {response.reason}")
    
    # 读取响应数据
    response_data = response.read().decode('utf-8')
    print(f"Response data length: {len(response_data)} characters")
    
    # 解析JSON响应
    response_json = json.loads(response_data)
    
    # 记录结束时间
    end_time = time.time()
    duration = end_time - start_time
    
    # 检查响应是否成功
    if response.status == 200:
        # 提取响应内容
        message = response_json['choices'][0]['message']['content']
        usage = response_json['usage']
        
        # 提取使用统计
        prompt_tokens = usage['prompt_tokens']
        completion_tokens = usage['completion_tokens']
        total_tokens = usage['total_tokens']
        
        # 计算token/速度
        tokens_per_second = total_tokens / duration
        
        print("\n=== Response ===")
        print(message)
        print("\n=== Usage Statistics ===")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Completion tokens: {completion_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Response time: {duration:.2f} seconds")
        print(f"Tokens per second: {tokens_per_second:.2f}")
    else:
        print(f"\nError: {response.status} - {response.reason}")
        print(f"Response: {response_data}")
        
except Exception as e:
    print(f"\nError: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    # 关闭连接
    if 'conn' in locals():
        conn.close()
        print("Connection closed")

print("\n=== Test Completed ===")