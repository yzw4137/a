import os
import json
import sys
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

# 从.env文件加载环境变量
def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 加载环境变量
load_env()

# 从环境变量获取配置
BASE_URL = os.getenv('BASE_URL', 'http://localhost:1234/v1')
MODEL = os.getenv('MODEL', 'qwen3.5-4b')
API_KEY = os.getenv('API_KEY', 'lm-studio')
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))

# 检查必要的配置
if not API_KEY:
    print("Error: API_KEY is required. Please set it in .env file.")
    exit(1)

# 解析URL
parsed_url = urlparse(BASE_URL)
scheme = parsed_url.scheme
host = parsed_url.netloc
path = parsed_url.path or '/'

# 聊天历史记录
chat_history = []

def send_message(message):
    """发送消息到LLM并获取响应"""
    # 添加用户消息到历史记录
    chat_history.append({"role": "user", "content": message})
    
    # 构建请求数据
    request_data = {
        "model": MODEL,
        "messages": chat_history,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": True  # 启用流式输出
    }
    
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
    
    try:
        # 发送POST请求
        conn.request('POST', f"{path}/chat/completions", json.dumps(request_data), headers)
        
        # 获取响应
        response = conn.getresponse()
        
        if response.status == 200:
            print("\nAssistant: ", end="", flush=True)
            
            # 处理流式响应
            assistant_response = ""
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        if 'choices' in chunk and chunk['choices']:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                print(content, end="", flush=True)
                                assistant_response += content
                    except json.JSONDecodeError:
                        pass
            
            # 添加助手响应到历史记录
            chat_history.append({"role": "assistant", "content": assistant_response})
            print()  # 换行
        else:
            print(f"\nError: {response.status} - {response.reason}")
            response_data = response.read().decode('utf-8')
            print(f"Response: {response_data}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("=== LLM Chat Interface ===")
    print(f"Connected to: {BASE_URL}")
    print(f"Model: {MODEL}")
    print("Type your message and press Enter. Press Ctrl+C to exit.\n")
    
    try:
        while True:
            # 获取用户输入
            user_input = input("You: ")
            
            # 发送消息并获取响应
            send_message(user_input)
            
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        print(f"Total messages in history: {len(chat_history)}")

if __name__ == "__main__":
    main()