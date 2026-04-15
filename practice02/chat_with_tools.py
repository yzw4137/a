import os
import json
import sys
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse
from tools import list_files, rename_file, delete_file, create_file, read_file, tools

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

# 系统提示词
system_prompt = """你是一个智能助手，能够使用工具来完成各种文件操作任务。

你可以使用以下工具：

1. list_files: 列出某个目录下的所有文件及其基本属性
   参数：directory (目录路径)

2. rename_file: 修改某个目录下某个文件的名字
   参数：directory (目录路径), old_name (旧文件名), new_name (新文件名)

3. delete_file: 删除某个目录下的某个文件
   参数：directory (目录路径), filename (文件名)

4. create_file: 在某个目录下新建1个文件，并且写入内容
   参数：directory (目录路径), filename (文件名), content (文件内容)

5. read_file: 读取某个目录下的某个文件的内容
   参数：directory (目录路径), filename (文件名)

当你需要执行文件操作时，使用工具调用的格式：

```json
{
  "toolcall": {
    "name": "工具名称",
    "params": {
      "参数1": "值1",
      "参数2": "值2"
    }
  }
}
```

例如，要列出当前目录下的文件：

```json
{
  "toolcall": {
    "name": "list_files",
    "params": {
      "directory": "."
    }
  }
}
```

当我提供工具执行结果后，你需要根据结果继续对话或提供最终答案。"""

# 初始化聊天历史
chat_history.append({"role": "system", "content": system_prompt})

# 工具映射
tool_functions = {
    "list_files": list_files,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "create_file": create_file,
    "read_file": read_file
}

def execute_tool_call(toolcall):
    """执行工具调用"""
    tool_name = toolcall.get("name")
    params = toolcall.get("params", {})
    
    if tool_name in tool_functions:
        try:
            # 执行工具函数
            result = tool_functions[tool_name](**params)
            return {
                "toolcall": toolcall,
                "result": result
            }
        except Exception as e:
            return {
                "toolcall": toolcall,
                "result": {
                    "status": "error",
                    "message": str(e)
                }
            }
    else:
        return {
            "toolcall": toolcall,
            "result": {
                "status": "error",
                "message": f"Tool {tool_name} not found"
            }
        }

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
    conn = None
    try:
        if scheme == 'https':
            conn = HTTPSConnection(host, timeout=30)
        else:
            conn = HTTPConnection(host, timeout=30)
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        
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
            
            # 检查是否有工具调用
            try:
                # 尝试解析助手响应中的工具调用
                response_text = assistant_response.strip()
                # 移除可能的代码块标记
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                if response_text.startswith('{'):
                    toolcall_data = json.loads(response_text)
                    if "toolcall" in toolcall_data:
                        print("\nExecuting tool call...")
                        # 执行工具调用
                        tool_result = execute_tool_call(toolcall_data["toolcall"])
                        print(f"Tool result: {json.dumps(tool_result['result'], indent=2, ensure_ascii=False)}")
                        
                        # 将工具执行结果添加到聊天历史
                        chat_history.append({"role": "user", "content": json.dumps(tool_result, ensure_ascii=False)})
                        
                        # 不使用递归，返回工具调用结果，让主循环处理
                        return {
                            "tool_called": True,
                            "tool_result": tool_result
                        }
            except json.JSONDecodeError as e:
                # 如果不是有效的JSON，忽略
                print(f"\nError parsing tool call: {str(e)}")
                print(f"Response text: {assistant_response}")
                pass
        else:
            print(f"\nError: {response.status} - {response.reason}")
            response_data = response.read().decode('utf-8')
            print(f"Response: {response_data}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保连接被关闭
        if conn:
            try:
                conn.close()
            except:
                pass
    
    return {"tool_called": False}

def main():
    """主函数"""
    print("=== LLM Chat Interface with Tools ===")
    print(f"Connected to: {BASE_URL}")
    print(f"Model: {MODEL}")
    print("Type your message and press Enter. Press Ctrl+C to exit.")
    print("You can ask me to perform file operations like listing files, creating files, etc.\n")
    
    try:
        while True:
            # 获取用户输入
            user_input = input("You: ")
            
            # 发送消息并获取响应
            result = send_message(user_input)
            
            # 处理工具调用结果
            while result.get("tool_called", False):
                # 发送工具执行完成的消息
                result = send_message("工具执行完成，请继续")
            
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        print(f"Total messages in history: {len(chat_history)}")

if __name__ == "__main__":
    main()