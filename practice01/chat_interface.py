import os
import json
import sys
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

# ========== 直接在这里配置（不需要 .env 文件）==========
BASE_URL = "https://openrouter.ai/api/v1"  # 改成 OpenRouter
MODEL = "qwen/qwen3-coder:free"            # 千问免费模型
API_KEY = "sk-or-v1-你的完整API_Key"        # 替换成你的真实 Key
TEMPERATURE = 0.7
MAX_TOKENS = 1000
# ====================================================

# 从.env文件加载环境变量（可选，如果存在的话）
def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 加载环境变量（会覆盖上面的配置）
load_env()

# 从环境变量获取配置（如果.env存在，会覆盖上面的值）
BASE_URL = os.getenv('BASE_URL', BASE_URL)
MODEL = os.getenv('MODEL', MODEL)
API_KEY = os.getenv('API_KEY', API_KEY)
TEMPERATURE = float(os.getenv('TEMPERATURE', str(TEMPERATURE)))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', str(MAX_TOKENS)))

# 调试信息
print(f"DEBUG: BASE_URL = {BASE_URL}")
print(f"DEBUG: MODEL = {MODEL}")
print(f"DEBUG: API_KEY starts with 'sk-or-v1-': {API_KEY.startswith('sk-or-v1-')}")
print(f"DEBUG: API_KEY length: {len(API_KEY)}")

# 检查必要的配置
if not API_KEY:
    print("Error: API_KEY is required. Please set it in .env file or directly in code.")
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
        'Authorization': f'Bearer {API_KEY}',
        'HTTP-Referer': 'http://localhost',  # 添加这个，OpenRouter 推荐
        'X-Title': 'LLM Chat Interface'       # 添加这个，OpenRouter 推荐
    }
    
    # 调试请求头（隐藏完整 Key 保护安全）
    print(f"DEBUG: Request headers (Authorization: Bearer {API_KEY[:20]}...)")
    
    try:
        # 发送POST请求
        conn.request('POST', f"{path}/chat/completions", json.dumps(request_data), headers)
        
        # 获取响应
        response = conn.getresponse()
        
        # 调试响应状态
        print(f"DEBUG: Response status: {response.status} - {response.reason}")
        
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
            if assistant_response:
                chat_history.append({"role": "assistant", "content": assistant_response})
                print()  # 换行
            else:
                print("\n[No response content received]")
            
        elif response.status == 429:
            print(f"\nError: Rate limit exceeded. Details:")
            response_data = response.read().decode('utf-8')
            try:
                error_json = json.loads(response_data)
                if 'error' in error_json:
                    print(f"  Message: {error_json['error'].get('message', 'Unknown')}")
                    if 'metadata' in error_json['error']:
                        print(f"  Details: {error_json['error']['metadata']}")
            except:
                print(f"  Response: {response_data}")
            
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