import os
import json
import http.client
import ssl
from urllib.parse import urlparse
import sys
import stat     
import time
import subprocess
import re

# 读取.env文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        # 尝试从当前目录加载
        env_path = '.env'
        if not os.path.exists(env_path):
            print(f"错误：{env_path} 文件不存在，请从 env.example 复制并填写正确参数")
            exit(1)
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

# 工具函数
def list_files(directory):
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            stat_info = os.stat(item_path)
            files.append({
                "name": item,
                "path": item_path,
                "size": stat_info.st_size,
                "mode": stat.filemode(stat_info.st_mode),
                "mtime": stat_info.st_mtime
            })
        return json.dumps({"status": "success", "data": files}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def rename_file(directory, old_name, new_name):
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        return json.dumps({"status": "success", "message": f"文件已重命名为 {new_name}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def delete_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        os.remove(file_path)
        return json.dumps({"status": "success", "message": "文件已删除"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def create_file(directory, file_name, content):
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return json.dumps({"status": "success", "message": "文件已创建"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def read_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return json.dumps({"status": "success", "data": content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def fetch_webpage(url):
    try:
        url = url.strip('`')
        from urllib.parse import urlparse, quote, urlunparse
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
        
        import urllib.request
        with urllib.request.urlopen(encoded_url, timeout=30) as response:
            content = response.read().decode('utf-8', errors='replace')
        
        max_content_length = 100000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n... (内容已截断)"
        
        return json.dumps({"status": "success", "data": content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def search_chat_history(query):
    try:
        log_path = os.getenv('LOG_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log.txt'))
        if not os.path.exists(log_path):
            return json.dumps({"status": "error", "message": "聊天历史文件不存在"}, ensure_ascii=False)
        
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        search_prompt = f"用户查询: {query}\n\n聊天历史记录:\n{content}\n\n请根据聊天历史回答用户的问题。"
        
        return json.dumps({"status": "success", "data": search_prompt}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def anythingllm_query(message):
    try:
        api_key = os.getenv('ANYTHINGLLM_API_KEY')
        workspace_slug = os.getenv('ANYTHINGLLM_WORKSPACE_SLUG')
        
        if not api_key or not workspace_slug:
            return json.dumps({"status": "error", "message": "请配置ANYTHINGLLM_API_KEY和ANYTHINGLLM_WORKSPACE_SLUG"}, ensure_ascii=False)
        
        url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
        payload = json.dumps({"message": message})
        
        curl_command = [
            "curl", "-X", "POST", url,
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Content-Type: application/json",
            "-d", payload
        ]
        
        timeout_sec = int(os.getenv('ANYTHINGLLM_TIMEOUT', '300'))
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=timeout_sec
        )
        
        if result.returncode != 0:
            return json.dumps({"status": "error", "message": f"curl执行失败: {result.stderr}"}, ensure_ascii=False)
        
        try:
            response_data = json.loads(result.stdout)
            return json.dumps({"status": "success", "data": response_data}, ensure_ascii=False)
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": f"响应解析失败: {result.stdout}"}, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({"status": "error", "message": "请求超时"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def list_available_skills():
    try:
        skills_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.agents', 'skills')
        if not os.path.exists(skills_path):
            return json.dumps({"status": "error", "message": "技能目录不存在"}, ensure_ascii=False)
        
        skills = []
        for skill_dir in os.listdir(skills_path):
            skill_path = os.path.join(skills_path, skill_dir)
            if os.path.isdir(skill_path):
                skill_file = os.path.join(skill_path, 'SKILL.md')
                if os.path.exists(skill_file):
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        front_matter = match.group(1)
                        name_match = re.search(r'name:\s*(.+)', front_matter)
                        desc_match = re.search(r'description:\s*(.+)', front_matter)
                        if name_match and desc_match:
                            skills.append({
                                "name": name_match.group(1).strip(),
                                "description": desc_match.group(1).strip()
                            })
        
        return json.dumps({"status": "success", "data": skills}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def load_skill_content(skill_name):
    try:
        skills_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.agents', 'skills')
        if not os.path.exists(skills_path):
            return json.dumps({"status": "error", "message": "技能目录不存在"}, ensure_ascii=False)
        
        skill_dir = None
        for d in os.listdir(skills_path):
            d_path = os.path.join(skills_path, d)
            if os.path.isdir(d_path):
                skill_file = os.path.join(d_path, 'SKILL.md')
                if os.path.exists(skill_file):
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        front_matter = match.group(1)
                        name_match = re.search(r'name:\s*(.+)', front_matter)
                        if name_match and name_match.group(1).strip() == skill_name:
                            skill_dir = d
                            break
        
        if not skill_dir:
            return json.dumps({"status": "error", "message": f"技能 {skill_name} 不存在"}, ensure_ascii=False)
        
        skill_file = os.path.join(skills_path, skill_dir, 'SKILL.md')
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
        if match:
            skill_content = match.group(1).strip()
        else:
            skill_content = content
        
        return json.dumps({"status": "success", "data": skill_content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def search_files(directory, keyword):
    try:
        results = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if keyword in content:
                                count = content.count(keyword)
                                preview = content[:200]
                                results.append({
                                    "file": file_path,
                                    "count": count,
                                    "preview": preview
                                })
                    except Exception:
                        continue
        
        return json.dumps({"status": "success", "data": results}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 调用LLM API
def call_llm(messages, tools=None):
    base_url = os.getenv('BASE_URL')
    model = os.getenv('MODEL')
    api_key = os.getenv('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误：请配置BASE_URL、MODEL和API_KEY")
        return None
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    protocol = parsed_url.scheme
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv('TEMPERATURE', '0.7')),
        "max_tokens": int(os.getenv('MAX_TOKENS', '8192'))
    }
    
    if tools:
        data["tools"] = tools
        data["tool_choice"] = "auto"
    
    if protocol == 'https':
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = http.client.HTTPSConnection(host, context=context)
    else:
        conn = http.client.HTTPConnection(host)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', path, json.dumps(data), headers)
        response = conn.getresponse()
        response_content = response.read().decode()
        
        try:
            response_data = json.loads(response_content)
        except json.JSONDecodeError:
            if response.status == 200:
                return response_content
            else:
                print(f"API错误: {response_content}")
                return None
        
        if response.status == 200:
            return response_data
        else:
            print(f"API错误: {response_data.get('error', {}).get('message', '未知错误')}")
            return None
    finally:
        conn.close()

def stream_llm(messages):
    base_url = os.getenv('BASE_URL')
    model = os.getenv('MODEL')
    api_key = os.getenv('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误：请配置BASE_URL、MODEL和API_KEY")
        return None
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    protocol = parsed_url.scheme
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv('TEMPERATURE', '0.7')),
        "max_tokens": int(os.getenv('MAX_TOKENS', '8192')),
        "stream": True
    }
    
    if protocol == 'https':
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = http.client.HTTPSConnection(host, context=context)
    else:
        conn = http.client.HTTPConnection(host)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', path, json.dumps(data), headers)
        response = conn.getresponse()
        
        if response.status != 200:
            error_data = json.loads(response.read().decode())
            print(f"API错误: {error_data.get('error', {}).get('message', '未知错误')}")
            return None
        
        full_response = ""
        for line in response:
            line = line.decode().strip()
            if not line:
                continue
            if line.startswith('data: '):
                line = line[6:]
                if line == '[DONE]':
                    break
                try:
                    chunk = json.loads(line)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        if 'content' in delta and delta['content']:
                            print(delta['content'], end='', flush=True)
                            full_response += delta['content']
                except json.JSONDecodeError:
                    pass
        print()
        return full_response
    finally:
        conn.close()

def execute_tool_call(tool_call):
    if tool_call.get('type') == 'function':
        function = tool_call.get('function', {})
        tool_name = function.get('name')
        arguments = function.get('arguments', {})
        if isinstance(arguments, str):
            try:
                tool_args = json.loads(arguments)
            except json.JSONDecodeError:
                tool_args = {}
        else:
            tool_args = arguments
    else:
        tool_name = tool_call.get('name')
        tool_args = tool_call.get('arguments', {})
    
    print(f"执行工具: {tool_name}")
    print(f"参数: {tool_args}")
    
    # 特殊处理read_file的参数
    if tool_name == 'read_file':
        # 尝试从不同的参数格式中提取路径信息
        filepath = tool_args.get('file_path', tool_args.get('filepath', tool_args.get('path', '')))
        if filepath:
            # 如果是完整路径，分割为目录和文件名
            if '\\' in filepath:
                parts = filepath.split('\\')
                directory = '\\'.join(parts[:-1]) if len(parts) > 1 else '.'
                file_name = parts[-1]
            elif '/' in filepath:
                parts = filepath.split('/')
                directory = '/'.join(parts[:-1]) if len(parts) > 1 else '.'
                file_name = parts[-1]
            else:
                directory = '.'
                file_name = filepath
        else:
            directory = tool_args.get('directory', '.')
            file_name = tool_args.get('file_name', tool_args.get('filename', ''))
        
        result = read_file(directory, file_name)
    else:
        tool_map = {
            "list_directory": lambda: list_files(tool_args.get('directory', tool_args.get('folder_path', tool_args.get('path', '.')))),
            "rename_file": lambda: rename_file(tool_args.get('directory'), tool_args.get('old_name'), tool_args.get('new_name')),
            "delete_file": lambda: delete_file(tool_args.get('directory'), tool_args.get('file_name')),
            "create_file": lambda: create_file(tool_args.get('directory'), tool_args.get('file_name'), tool_args.get('content')),
            "fetch_webpage": lambda: fetch_webpage(tool_args.get('url')),
            "search_chat_history": lambda: search_chat_history(tool_args.get('query')),
            "anythingllm_query": lambda: anythingllm_query(tool_args.get('message')),
            "load_skill_content": lambda: load_skill_content(tool_args.get('skill_name')),
            "search_files": lambda: search_files(tool_args.get('directory', '.'), tool_args.get('keyword', tool_args.get('query', '')))
        }
        
        if tool_name in tool_map:
            result = tool_map[tool_name]()
        else:
            result = json.dumps({"status": "error", "message": f"未知工具 {tool_name}"}, ensure_ascii=False)
    
    print(f"工具执行结果: {result[:500]}..." if len(result) > 500 else f"工具执行结果: {result}")
    return result

# 链式调用上下文管理器
class ChainedCallContext:
    def __init__(self, max_iterations=10):
        self.steps = []
        self.variables = {}
        self.max_iterations = max_iterations
        self.current_iteration = 0
    
    def add_step(self, tool_name, arguments, result):
        self.steps.append({
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "iteration": self.current_iteration
        })
    
    def set_variable(self, name, value):
        self.variables[name] = value
    
    def get_variable(self, name, default=None):
        return self.variables.get(name, default)
    
    def has_more_iterations(self):
        return self.current_iteration < self.max_iterations
    
    def increment_iteration(self):
        self.current_iteration += 1

# 提取JSON内容
def extract_json(content):
    content = content.strip()
    if content.startswith('```json'):
        content = content[7:]
    if content.endswith('```'):
        content = content[:-3]
    content = content.strip()
    
    if content.startswith('{') and '}' in content:
        brace_count = 0
        json_end = 0
        for i, char in enumerate(content):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
        
        if json_end > 0:
            return content[:json_end]
    
    return content

# 解析LLM响应
def parse_llm_response(response):
    if not response:
        return {"done": False, "error": "响应为空"}
    
    try:
        response_str = ""
        
        if isinstance(response, str):
            response_str = response
        elif isinstance(response, dict):
            if 'choices' in response and len(response['choices']) > 0:
                message = response['choices'][0].get('message', {})
                if message.get('tool_calls'):
                    tool_call = message['tool_calls'][0]
                    return {"done": False, "tool_call": tool_call}
                elif 'content' in message:
                    response_str = message['content']
                else:
                    return {"done": False, "error": "无法解析响应"}
            else:
                response_str = str(response)
        else:
            response_str = str(response)
        
        if not response_str or response_str.strip() == '':
            return {"done": False, "error": "响应内容为空"}
        
        json_str = extract_json(response_str)
        
        try:
            result = json.loads(json_str)
            if 'done' in result:
                return result
            else:
                return {"done": True, "answer": response_str}
        except json.JSONDecodeError:
            # 如果JSON解析失败，检查是否有tool_calls
            if isinstance(response, dict) and 'choices' in response:
                message = response['choices'][0].get('message', {})
                if message.get('tool_calls'):
                    return {"done": False, "tool_call": message['tool_calls'][0]}
            
            # 尝试从不完整的响应中提取工具调用信息
            if 'tool_call' in response_str.lower() and 'name' in response_str:
                try:
                    # 尝试使用正则表达式提取工具名称
                    import re
                    name_match = re.search(r"'name'\s*:\s*['\"]([^'\"]+)['\"]", response_str)
                    args_match = re.search(r"'arguments'\s*:\s*({[^}]+})", response_str)
                    
                    if name_match:
                        tool_name = name_match.group(1)
                        arguments = {}
                        if args_match:
                            try:
                                arguments = json.loads(args_match.group(1).replace("'", "\""))
                            except:
                                pass
                        
                        return {"done": False, "tool_call": {
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": arguments
                            }
                        }}
                except:
                    pass
            
            # 如果JSON解析失败，尝试将响应作为最终回答
            return {"done": True, "answer": response_str.strip()}
    
    except Exception as e:
        return {"done": False, "error": str(e)}

# 构建分析提示词
def build_analysis_prompt(user_request, context):
    steps_history = ""
    if context.steps:
        steps_history = "已执行步骤：\n"
        for i, step in enumerate(context.steps, 1):
            try:
                result_json = json.loads(step['result'])
                if result_json.get('status') == 'success':
                    result_summary = f"成功"
                else:
                    result_summary = f"失败: {result_json.get('message', '')}"
            except:
                result_summary = "结果已获取"
            
            steps_history += f"{i}. {step['tool_name']}({step['arguments']}) -> {result_summary}\n"
    
    variables_desc = ""
    if context.variables:
        variables_desc = "可用变量：\n"
        for name, value in context.variables.items():
            if isinstance(value, list):
                variables_desc += f"- {name}: {len(value)}个项目\n"
            elif isinstance(value, str):
                variables_desc += f"- {name}: {len(value)}字符\n"
            else:
                variables_desc += f"- {name}: {str(value)[:30]}...\n"
    
    # 根据执行历史生成建议操作
    suggestion = ""
    if context.steps:
        last_tool = context.steps[-1]['tool_name']
        if last_tool == 'list_directory':
            suggestion = "提示：已经获取了目录列表，请读取所需的文件（如test01、test02），不要重复调用list_directory。"
        elif last_tool == 'read_file' and len([s for s in context.steps if s['tool_name'] == 'read_file']) >= 2:
            suggestion = "提示：已经读取了多个文件，请直接计算并返回结果，不需要再调用工具。"
        elif last_tool == 'search_files':
            suggestion = "提示：搜索结果已获取，请读取具体文件或直接总结，不要重复搜索。"

    prompt = f"""
用户请求：{user_request}

{steps_history}
{variables_desc}

{suggestion}

请决定下一步操作。可用工具：list_directory, read_file, fetch_webpage, search_files, create_file, load_skill_content, anythingllm_query

**重要规则：**
1. 如果已经获取了所有必要的数据，请直接计算并返回结果，不需要调用其他工具
2. 如果任务涉及简单计算（如数字相加、比较等），请直接完成计算并返回最终答案
3. 如果需要更多信息，调用适当的工具获取数据
4. 不要重复调用相同的工具，避免无效操作

如果任务完成，返回：{{"done": true, "answer": "你的回答"}}
如果需要继续，返回：{{"done": false, "tool_call": {{"name": "工具名", "arguments": {{"参数": "值"}}}}}}

只返回JSON，不要其他内容。
"""
    
    return prompt.strip()

# 链式调用执行函数
def execute_chained_tool_call(user_request, max_iterations=5):
    context = ChainedCallContext(max_iterations=max_iterations)
    
    system_prompt = """你是智能工具调用代理。严格按照JSON格式返回：
完成时：{"done": true, "answer": "回答"}
继续时：{"done": false, "tool_call": {"name": "工具名", "arguments": {"参数": "值"}}}

只返回JSON，无其他文字。"""
    
    # 追踪连续失败次数
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    while context.has_more_iterations():
        print(f"\n=== 链式调用第 {context.current_iteration + 1}/{max_iterations} 轮 ===")
        
        analysis_prompt = build_analysis_prompt(user_request, context)
        
        # 调用LLM，最多重试3次
        response = None
        response_valid = False
        for retry in range(3):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            print("分析中...")
            response = call_llm(messages)
            
            if response:
                if isinstance(response, dict):
                    choice = response.get('choices', [{}])[0]
                    message = choice.get('message', {})
                    if message.get('content') or message.get('tool_calls'):
                        response_valid = True
                        break
                elif isinstance(response, str) and response.strip():
                    response_valid = True
                    break
            
            print(f"重试 {retry + 1}/3...")
            time.sleep(1)
        
        if not response or not response_valid:
            print("LLM无响应或响应无效")
            consecutive_failures += 1
            
            if consecutive_failures >= max_consecutive_failures:
                print(f"连续失败{max_consecutive_failures}次，退出链式调用")
                break
            
            # 尝试使用默认策略：自动读取文件
            # 1. 尝试从directory_list中获取文件列表
            directory_list = context.get_variable('directory_list', [])
            if directory_list and isinstance(directory_list, list):
                # 查找test01和test02文件
                target_files = ['test01', 'test02']
                for target in target_files:
                    file_info = next((item for item in directory_list if item.get('name') == target), None)
                    if file_info:
                        file_path = file_info.get('path', '')
                        if file_path:
                            if '\\' in file_path:
                                parts = file_path.split('\\')
                                directory = '\\'.join(parts[:-1]) if len(parts) > 1 else '.'
                                file_name = parts[-1]
                            elif '/' in file_path:
                                parts = file_path.split('/')
                                directory = '/'.join(parts[:-1]) if len(parts) > 1 else '.'
                                file_name = parts[-1]
                            else:
                                directory = '.'
                                file_name = file_path
                            
                            print(f"自动读取文件: {file_path}")
                            tool_result = read_file(directory, file_name)
                            context.add_step('read_file', {'directory': directory, 'file_name': file_name}, tool_result)
                            
                            try:
                                result_data = json.loads(tool_result)
                                if result_data.get('status') == 'success':
                                    # 存储多个文件内容
                                    file_contents = context.get_variable('file_contents', [])
                                    file_contents.append({
                                        'arguments': {'path': file_path},
                                        'content': result_data.get('data')
                                    })
                                    context.set_variable('file_contents', file_contents)
                                    context.set_variable('file_content', result_data.get('data'))
                                    consecutive_failures = 0  # 重置失败计数
                            except:
                                pass
                
                context.increment_iteration()
                continue
            
            # 2. 尝试从found_files中获取文件列表
            found_files = context.get_variable('found_files')
            if found_files and isinstance(found_files, list) and found_files:
                first_file = found_files[0].get('file', '')
                if first_file:
                    if '\\' in first_file:
                        parts = first_file.split('\\')
                        directory = '\\'.join(parts[:-1])
                        file_name = parts[-1]
                    else:
                        directory = '.'
                        file_name = first_file
                    
                    print(f"读取文件: {first_file}")
                    tool_result = read_file(directory, file_name)
                    context.add_step('read_file', {'directory': directory, 'file_name': file_name}, tool_result)
                    
                    try:
                        result_data = json.loads(tool_result)
                        if result_data.get('status') == 'success':
                            context.set_variable('file_content', result_data.get('data'))
                            consecutive_failures = 0  # 重置失败计数
                    except:
                        pass
                    
                    context.increment_iteration()
                    continue
            
            # 如果没有默认策略可用，退出循环
            break
        
        consecutive_failures = 0  # 重置失败计数
        
        parsed_result = parse_llm_response(response)
        
        if parsed_result.get('error'):
            print(f"解析失败: {parsed_result['error']}")
            consecutive_failures += 1
            
            if consecutive_failures >= max_consecutive_failures:
                print(f"连续失败{max_consecutive_failures}次，退出链式调用")
                break
            
            # 尝试使用默认策略
            found_files = context.get_variable('found_files')
            if found_files and isinstance(found_files, list) and found_files:
                first_file = found_files[0].get('file', '')
                if first_file:
                    if '\\' in first_file:
                        parts = first_file.split('\\')
                        directory = '\\'.join(parts[:-1])
                        file_name = parts[-1]
                    else:
                        directory = '.'
                        file_name = first_file
                    
                    print(f"读取文件: {first_file}")
                    tool_result = read_file(directory, file_name)
                    context.add_step('read_file', {'directory': directory, 'file_name': file_name}, tool_result)
                    context.increment_iteration()
                    continue
            
            # 如果没有默认策略可用，退出循环
            break
        
        if parsed_result.get('done'):
            answer = parsed_result.get('answer', '')
            print(f"任务完成！\n回答: {answer}")
            
            # 如果用户请求涉及计算，验证LLM的答案是否正确
            if '相加' in user_request or '之和' in user_request or '和' in user_request or '计算' in user_request:
                file_contents = context.get_variable('file_contents', [])
                
                # 如果file_contents为空，尝试从步骤中提取
                if len(file_contents) < 2:
                    read_steps = [s for s in context.steps if s['tool_name'] == 'read_file']
                    for step in read_steps:
                        try:
                            result_data = json.loads(step['result'])
                            if result_data.get('status') == 'success':
                                file_contents.append({
                                    'arguments': step['arguments'],
                                    'content': result_data.get('data', '')
                                })
                        except:
                            pass
                
                # 如果有足够的文件内容，使用我们自己的计算逻辑
                if len(file_contents) >= 2:
                    try:
                        total = 0
                        content_list = []
                        all_digit = True
                        for fc in file_contents:
                            content = fc.get('content', '').strip()
                            if content.isdigit():
                                num = int(content)
                                total += num
                                content_list.append(f"{fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: {num}")
                            else:
                                all_digit = False
                        
                        if all_digit and content_list:
                            correct_answer = f"计算结果：\n"
                            correct_answer += "\n".join(content_list) + "\n"
                            correct_answer += f"总和: {total}"
                            
                            # 检查LLM的答案是否正确
                            if str(total) not in answer:
                                print(f"LLM答案不正确，使用正确计算结果: {correct_answer}")
                                return correct_answer
                    except Exception as e:
                        print(f"验证计算失败: {str(e)}")
            
            return answer
        
        tool_call = parsed_result.get('tool_call')
        if not tool_call:
            print("无工具调用")
            break
        
        try:
            tool_result = execute_tool_call(tool_call)
            
            function_info = tool_call.get('function', {})
            tool_name = function_info.get('name', tool_call.get('name'))
            arguments = function_info.get('arguments', tool_call.get('arguments', {}))
            
            context.add_step(tool_name, arguments, tool_result)
            
            try:
                result_data = json.loads(tool_result)
                if result_data.get('status') == 'success':
                    data = result_data.get('data')
                    if data:
                        if tool_name == 'search_files':
                            context.set_variable('found_files', data)
                        elif tool_name == 'read_file':
                            # 存储多个文件内容
                            file_contents = context.get_variable('file_contents', [])
                            file_contents.append({
                                'arguments': arguments,
                                'content': data
                            })
                            context.set_variable('file_contents', file_contents)
                            # 同时保存最新内容
                            context.set_variable('file_content', data)
                        elif tool_name == 'fetch_webpage':
                            context.set_variable('web_content', data)
                        elif tool_name == 'list_directory':
                            context.set_variable('directory_list', data)
                        elif tool_name == 'load_skill_content':
                            context.set_variable('skill_content', data)
            except:
                pass
            
            context.increment_iteration()
            
        except Exception as e:
            print(f"工具执行异常: {str(e)}")
            break
    
    if not context.has_more_iterations():
        print(f"达到最大迭代次数")
    
    # 检查是否需要自动计算（优先使用我们自己的计算逻辑，避免LLM计算错误）
    file_contents = context.get_variable('file_contents', [])
    if len(file_contents) >= 2 and ('相加' in user_request or '之和' in user_request or '和' in user_request or '计算' in user_request):
        print("检测到需要计算多个文件内容之和...")
        try:
            total = 0
            content_list = []
            all_digit = True
            for fc in file_contents:
                content = fc.get('content', '').strip()
                if content.isdigit():
                    num = int(content)
                    total += num
                    content_list.append(f"{fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: {num}")
                else:
                    all_digit = False
                    content_list.append(f"{fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: '{content}' (非数字)")
            
            if content_list:
                answer = f"计算结果：\n"
                answer += "\n".join(content_list) + "\n"
                if all_digit:
                    answer += f"总和: {total}"
                else:
                    answer += "（部分内容非数字，无法计算总和）"
                print(f"最终回答: {answer}")
                return answer
        except Exception as e:
            print(f"自动计算失败: {str(e)}")
    
    # 如果没有读取到足够的文件，尝试从执行步骤中提取文件内容
    if len(file_contents) < 2:
        # 从步骤中提取read_file的结果
        read_steps = [s for s in context.steps if s['tool_name'] == 'read_file']
        for step in read_steps:
            try:
                result_data = json.loads(step['result'])
                if result_data.get('status') == 'success':
                    file_contents.append({
                        'arguments': step['arguments'],
                        'content': result_data.get('data', '')
                    })
            except:
                pass
        
        # 再次尝试计算
        if len(file_contents) >= 2 and ('相加' in user_request or '之和' in user_request or '和' in user_request or '计算' in user_request):
            print("从步骤中提取文件内容后重新计算...")
            try:
                total = 0
                content_list = []
                all_digit = True
                for fc in file_contents:
                    content = fc.get('content', '').strip()
                    if content.isdigit():
                        num = int(content)
                        total += num
                        content_list.append(f"{fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: {num}")
                    else:
                        all_digit = False
                        content_list.append(f"{fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: '{content}' (非数字)")
                
                if content_list:
                    answer = f"计算结果：\n"
                    answer += "\n".join(content_list) + "\n"
                    if all_digit:
                        answer += f"总和: {total}"
                    else:
                        answer += "（部分内容非数字，无法计算总和）"
                    print(f"最终回答: {answer}")
                    return answer
            except Exception as e:
                print(f"自动计算失败: {str(e)}")
    
    # 生成最终总结
    print("生成最终总结...")
    summary_prompt = f"根据以下执行历史，总结任务完成情况：\n\n用户请求：{user_request}\n\n执行步骤：\n"
    for i, step in enumerate(context.steps, 1):
        summary_prompt += f"{i}. {step['tool_name']}({step['arguments']})\n"
    
    # 添加文件内容到总结提示
    if file_contents:
        summary_prompt += "\n获取的文件内容：\n"
        for fc in file_contents:
            summary_prompt += f"- {fc.get('arguments', {}).get('path', fc.get('arguments', {}).get('file_name', '未知文件'))}: {fc.get('content', '')[:50]}...\n"
    
    messages = [
        {"role": "system", "content": "你是总结助手，请根据执行历史总结任务结果。如果涉及数字计算，请完成计算。"},
        {"role": "user", "content": summary_prompt}
    ]
    
    response = call_llm(messages)
    if response and isinstance(response, dict):
        answer = response.get('choices', [{}])[0].get('message', {}).get('content', '任务已完成')
    else:
        answer = "任务已完成"
    
    print(f"最终回答: {answer}")
    return answer

def summarize_chat_history(chat_history):
    user_assistant_messages = [msg for msg in chat_history if msg['role'] in ['user', 'assistant']]
    
    if len(user_assistant_messages) <= 2:
        return chat_history
    
    split_point = int(len(user_assistant_messages) * 0.7)
    messages_to_summarize = user_assistant_messages[:split_point]
    messages_to_keep = user_assistant_messages[split_point:]
    
    summary_prompt = "总结以下聊天记录：\n\n"
    for msg in messages_to_summarize:
        role = "用户" if msg['role'] == 'user' else "助手"
        summary_prompt += f"{role}: {msg['content']}\n\n"
    
    summary_messages = [
        {"role": "system", "content": "你是聊天记录总结助手。"},
        {"role": "user", "content": summary_prompt}
    ]
    
    summary_response = call_llm(summary_messages)
    if summary_response and isinstance(summary_response, dict):
        summary = summary_response.get('choices', [{}])[0].get('message', {}).get('content', '')
    else:
        summary = str(summary_response) if summary_response else "总结失败"
    
    new_chat_history = [chat_history[0]]
    new_chat_history.append({"role": "assistant", "content": f"【聊天总结】: {summary}"})
    new_chat_history.extend(messages_to_keep)
    
    return new_chat_history

def extract_key_info(chat_history):
    relevant_messages = [msg for msg in chat_history if msg['role'] in ['user', 'assistant'] and not msg.get('content', '').startswith('【聊天记录总结】')]
    
    extract_prompt = "按5W规则提取以下聊天记录的关键信息：\n\n"
    for msg in relevant_messages:
        role = "用户" if msg['role'] == 'user' else "助手"
        extract_prompt += f"{role}: {msg['content']}\n\n"
    
    extract_messages = [
        {"role": "system", "content": "你是信息提取助手，按5W规则提取关键信息。"},
        {"role": "user", "content": extract_prompt}
    ]
    
    extract_response = call_llm(extract_messages)
    if extract_response and isinstance(extract_response, dict):
        key_info = extract_response.get('choices', [{}])[0].get('message', {}).get('content', '')
    else:
        key_info = str(extract_response) if extract_response else "提取失败"
    
    log_path = os.getenv('LOG_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log.txt'))
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(key_info)
        f.write("\n")
    
    return key_info

def main():
    load_env()
    
    skills_result = list_available_skills()
    skills_data = json.loads(skills_result)
    skills_list = skills_data.get('data', [])
    
    tools = [
        {"type": "function", "function": {"name": "list_directory", "description": "列出目录", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "rename_file", "description": "重命名文件", "parameters": {"type": "object", "properties": {"directory": {"type": "string"}, "old_name": {"type": "string"}, "new_name": {"type": "string"}}, "required": ["directory", "old_name", "new_name"]}}},
        {"type": "function", "function": {"name": "delete_file", "description": "删除文件", "parameters": {"type": "object", "properties": {"directory": {"type": "string"}, "file_name": {"type": "string"}}, "required": ["directory", "file_name"]}}},
        {"type": "function", "function": {"name": "create_file", "description": "创建文件", "parameters": {"type": "object", "properties": {"directory": {"type": "string"}, "file_name": {"type": "string"}, "content": {"type": "string"}}, "required": ["directory", "file_name", "content"]}}},
        {"type": "function", "function": {"name": "read_file", "description": "读取文件", "parameters": {"type": "object", "properties": {"directory": {"type": "string"}, "file_name": {"type": "string"}}, "required": ["directory", "file_name"]}}},
        {"type": "function", "function": {"name": "fetch_webpage", "description": "访问网页", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
        {"type": "function", "function": {"name": "search_chat_history", "description": "搜索聊天历史", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
        {"type": "function", "function": {"name": "anythingllm_query", "description": "访问文档仓库", "parameters": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}}},
        {"type": "function", "function": {"name": "load_skill_content", "description": "加载技能内容", "parameters": {"type": "object", "properties": {"skill_name": {"type": "string"}}, "required": ["skill_name"]}}},
        {"type": "function", "function": {"name": "search_files", "description": "搜索文件内容", "parameters": {"type": "object", "properties": {"directory": {"type": "string"}, "keyword": {"type": "string"}}, "required": ["directory", "keyword"]}}}
    ]
    
    skills_json = json.dumps({"skills": skills_list}, ensure_ascii=False, indent=2)
    
    system_prompt = f"""你是AI助手，支持文件操作、网络访问、聊天历史搜索、文档仓库访问和技能使用。

可用技能：
{skills_json}

链式调用说明：支持多步骤任务自动执行。

工具：list_directory, rename_file, delete_file, create_file, read_file, fetch_webpage, search_chat_history, anythingllm_query, load_skill_content, search_files

当用户请求包含'查找'和'总结'时，自动使用链式调用。"""
    
    chat_history = [{"role": "system", "content": system_prompt}]
    chat_rounds = 0
    
    print("=== LLM 链式工具调用客户端 ===")
    print("可用工具：list_directory, rename_file, delete_file, create_file, read_file, fetch_webpage, search_chat_history, anythingllm_query, load_skill_content, search_files")
    print("示例：查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容")
    print()
    
    try:
        while True:
            user_input = input("你: ")
            
            if user_input.startswith('/search') or '查找聊天历史' in user_input:
                query = user_input[7:].strip() if user_input.startswith('/search') else user_input
                tool_result = search_chat_history(query)
                result_data = json.loads(tool_result)
                
                if result_data.get('status') == 'success':
                    search_messages = [
                        {"role": "system", "content": "聊天历史查询助手"},
                        {"role": "user", "content": result_data.get('data', '')}
                    ]
                    print("助手: ", end='', flush=True)
                    search_response = stream_llm(search_messages)
                    if search_response:
                        chat_history.append({"role": "user", "content": user_input})
                        chat_history.append({"role": "assistant", "content": search_response})
                else:
                    print(f"助手: {result_data.get('message', '搜索失败')}")
            elif '查找' in user_input or '总结' in user_input or ('访问' in user_input and ('文件' in user_input or '.txt' in user_input)):
                print("助手: 使用链式调用处理复杂任务...")
                final_answer = execute_chained_tool_call(user_input)
                chat_history.append({"role": "user", "content": user_input})
                chat_history.append({"role": "assistant", "content": final_answer})
                print()
            else:
                chat_history.append({"role": "user", "content": user_input})
                chat_rounds += 1
                
                history_length = sum(len(msg.get('content', '')) for msg in chat_history)
                if (chat_rounds >= 5 and chat_rounds % 5 == 0) or history_length > 3000:
                    chat_history = summarize_chat_history(chat_history)
                
                if chat_rounds % 5 == 0:
                    extract_key_info(chat_history)
                
                print("助手: ", end='', flush=True)
                
                try:
                    response = call_llm(chat_history, tools)
                    
                    if not response:
                        print("请求失败")
                        continue
                except Exception as e:
                    print(f"请求异常: {str(e)}")
                    continue
                
                if isinstance(response, dict):
                    choice = response.get('choices', [{}])[0]
                    message = choice.get('message', {})
                    
                    if message.get('tool_calls'):
                        for tool_call in message.get('tool_calls', []):
                            tool_result = execute_tool_call(tool_call)
                            chat_history.append(message)
                            chat_history.append({
                                "role": "tool",
                                "tool_call_id": tool_call.get('id'),
                                "name": tool_call.get('function', {}).get('name'),
                                "content": json.dumps(tool_result, ensure_ascii=False)
                            })
                        
                        final_response = stream_llm(chat_history)
                        if final_response:
                            chat_history.append({"role": "assistant", "content": final_response})
                    else:
                        content = message.get('content', '')
                        print(content)
                        chat_history.append(message)
                else:
                    print(response)
                    chat_history.append({"role": "assistant", "content": response})
            
            print()
    except KeyboardInterrupt:
        print("\n退出")
        sys.exit(0)

if __name__ == "__main__":
    main()
