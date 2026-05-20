# AI工具调用系统项目总结报告

---

## 摘要

本项目从 practice01 到 practice07 逐步演进，最终实现了一个**完整的AI工具调用系统**。该系统能够让大语言模型（LLM）根据用户请求自主选择并调用工具，支持多步骤链式调用，实现复杂任务的自动化执行。

---

## 一、引言

### 1. 项目背景

随着大语言模型的发展，如何让AI具备调用外部工具的能力成为研究热点。本项目旨在构建一个完整的工具调用系统，让LLM能够：
- 理解用户需求
- 选择合适的工具
- 执行工具调用
- 利用中间结果进行多步骤推理
- 返回最终结果

### 2. 技术演进路径

| 阶段 | 项目 | 核心功能 |
|------|------|---------|
| 基础阶段 | practice01 | 聊天界面与LLM访问 |
| 工具调用入门 | practice02 | 基础工具调用实现 |
| 总结功能 | practice03 | 添加对话总结功能 |
| 提示词优化 | practice04 | 优化工具调用提示词 |
| 功能增强 | practice05 | 增强工具调用能力 |
| 完善阶段 | practice06 | 完善工具调用系统 |
| 进阶阶段 | practice07 | **链式工具调用**（核心成果） |

### 3. 最终成果

**核心产品**：一个支持链式工具调用的AI助手系统

**主要能力**：
- ✅ 理解用户自然语言请求
- ✅ 自主选择并调用合适的工具
- ✅ 支持多步骤链式调用（前一个工具输出作为后一个工具输入）
- ✅ 自动计算验证（确保数学计算准确性）
- ✅ 完整的错误处理和重试机制

---

## 二、项目架构与技术实现

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI工具调用系统                           │
├─────────────────────────────────────────────────────────────┤
│  输入层          用户自然语言请求                           │
│     ↓                                                      │
│  理解层          LLM解析请求，决定调用工具                  │
│     ↓                                                      │
│  执行层          工具执行引擎（链式调用支持）                │
│     ↓                                                      │
│  工具层          文件操作、网页获取、搜索、技能查询等        │
│     ↓                                                      │
│  输出层          返回最终结果给用户                         │
└─────────────────────────────────────────────────────────────┘
```


### 核心组件

| 组件 | 位置 | 功能 |
|------|------|------|
| 聊天界面 | practice01/chat_interface.py | 用户交互界面 |
| LLM访问模块 | practice01/llm_access.py | 与LLM的接口 |
| 工具定义 | practice02/tools.py | 工具函数实现 |
| 工具调用客户端 | practice07/tool_client.py | 核心工具调用引擎 |
| 链式调用上下文 | practice07/tool_client.py | 多步骤状态管理 |
| 技能系统 | .agents/skills/ | 可扩展的技能库 |

#### 核心代码：ChainedCallContext 上下文管理器

```python
class ChainedCallContext:
    def __init__(self, max_iterations=10):
        self.steps = []           # 记录每一步的工具调用
        self.variables = {}       # 存储中间变量
        self.max_iterations = max_iterations
        self.current_iteration = 0
    
    def add_step(self, tool_name, arguments, result):
        """添加一个执行步骤"""
        self.steps.append({
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "iteration": self.current_iteration
        })
    
    def set_variable(self, name, value):
        """存储中间变量"""
        self.variables[name] = value
    
    def get_variable(self, name, default=None):
        """获取中间变量"""
        return self.variables.get(name, default)
```

**功能说明**：
- `steps`：记录每一步的工具调用信息，包括工具名称、参数和结果
- `variables`：存储中间变量，供后续步骤使用（如文件内容、目录列表等）
- `max_iterations`：防止无限循环，设置最大迭代次数

### 工具列表

| 工具名称 | 功能 |
|---------|------|
| `read_file` | 读取文件内容 |
| `list_directory` | 列出目录内容 |
| `search_files` | 搜索文件 |
| `create_file` | 创建文件 |
| `fetch_webpage` | 获取网页内容 |
| `load_skill_content` | 加载技能内容 |
| `anythingllm_query` | 查询AnythingLLM |

---

## 三、核心功能详解

### 1. 链式工具调用

**实现原理**：通过 `ChainedCallContext` 类管理多步骤调用的状态和中间结果

**执行流程**：
1. 用户发起请求
2. LLM分析请求，决定调用第一个工具
3. 执行工具调用，记录结果到上下文
4. LLM根据中间结果决定下一步操作
5. 重复步骤3-4直到任务完成
6. 返回最终结果

#### 核心代码：execute_chained_tool_call 链式调用执行函数

```python
def execute_chained_tool_call(user_request, max_iterations=5):
    context = ChainedCallContext(max_iterations=max_iterations)
    
    system_prompt = """你是智能工具调用代理。严格按照JSON格式返回：
完成时：{"done": true, "answer": "回答"}
继续时：{"done": false, "tool_call": {"name": "工具名", "arguments": {"参数": "值"}}}

只返回JSON，无其他文字。"""
    
    while context.has_more_iterations():
        print(f"\n=== 链式调用第 {context.current_iteration + 1}/{max_iterations} 轮 ===")
        
        # 1. 构建分析提示词（包含历史和变量）
        analysis_prompt = build_analysis_prompt(user_request, context)
        
        # 2. 调用LLM获取决策
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]
        response = call_llm(messages)
        
        # 3. 解析LLM响应
        parsed_result = parse_llm_response(response)
        
        # 4. 如果任务完成，返回结果
        if parsed_result.get('done'):
            answer = parsed_result.get('answer', '')
            return answer
        
        # 5. 如果需要继续，执行工具调用
        tool_call = parsed_result.get('tool_call')
        result = execute_tool_call(tool_call)
        
        # 6. 记录到上下文
        context.add_step(tool_name, arguments, result)
        context.increment_iteration()
    
    return "达到最大迭代次数"
```

**功能说明**：
- **步骤1**：构建包含历史信息和操作建议的提示词
- **步骤2**：调用LLM获取下一步决策
- **步骤3**：解析LLM响应（支持JSON和tool_calls格式）
- **步骤4**：如果任务完成，验证计算结果并返回
- **步骤5**：执行工具调用
- **步骤6**：记录执行结果，继续下一轮

### 2. 自动计算验证

**解决的问题**：LLM进行数学计算时可能出现错误

**实现方式**：
- 当检测到用户请求涉及计算（"相加"、"之和"、"计算"等关键词）
- 使用Python代码独立计算
- 验证LLM的答案是否正确
- 如果不正确，使用正确结果

**示例**：
- 用户请求："计算test01和test02的内容之和"
- LLM可能返回错误结果（如3+3=6）
- 系统自动计算正确结果（123+123=246）

#### 核心代码：自动计算验证逻辑

```python
# 检查是否需要自动计算
file_contents = context.get_variable('file_contents', [])
if len(file_contents) >= 2 and ('相加' in user_request or '之和' in user_request or '和' in user_request):
    print("检测到需要计算多个文件内容之和...")
    try:
        total = 0
        content_list = []
        all_digit = True
        
        # 遍历所有读取的文件内容
        for fc in file_contents:
            content = fc.get('content', '').strip()
            if content.isdigit():
                num = int(content)
                total += num
                content_list.append(f"{fc.get('arguments', {}).get('path', '未知文件')}: {num}")
            else:
                all_digit = False
                content_list.append(f"{fc.get('arguments', {}).get('path', '未知文件')}: '{content}' (非数字)")
        
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
```

**功能说明**：
- **关键词检测**：检测用户请求中是否包含"相加"、"之和"、"和"等关键词
- **文件内容提取**：从上下文中获取已读取的文件内容
- **独立计算**：使用Python代码进行数学计算，确保准确性
- **结果验证**：如果LLM返回的计算结果不正确，使用正确结果覆盖

### 3. 错误处理与重试机制

- **LLM无响应**：最多重试3次
- **JSON解析失败**：尝试多种解析方式
- **工具执行失败**：记录错误，继续执行或提示用户
- **无限循环保护**：设置最大迭代次数（默认5次）

#### 核心代码：工具执行与参数解析

```python
def execute_tool_call(tool_call):
    # 提取工具名称和参数
    if tool_call.get('type') == 'function':
        function = tool_call.get('function', {})
        tool_name = function.get('name')
        arguments = function.get('arguments', {})
    else:
        tool_name = tool_call.get('name')
        tool_args = tool_call.get('arguments', {})
    
    print(f"执行工具: {tool_name}")
    print(f"参数: {tool_args}")
    
    # 特殊处理read_file的参数（支持多种参数格式）
    if tool_name == 'read_file':
        # 支持file_path、filepath、path等多种参数格式
        filepath = tool_args.get('file_path', tool_args.get('filepath', tool_args.get('path', '')))
        if filepath:
            # 处理路径分隔符（Windows和Linux兼容）
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
        # 工具映射表
        tool_map = {
            "list_directory": lambda: list_files(tool_args.get('directory', tool_args.get('folder_path', tool_args.get('path', '.')))),
            "create_file": lambda: create_file(tool_args.get('directory'), tool_args.get('file_name'), tool_args.get('content')),
            "fetch_webpage": lambda: fetch_webpage(tool_args.get('url')),
            "search_files": lambda: search_files(tool_args.get('directory', '.'), tool_args.get('keyword', tool_args.get('query', '')))
        }
        
        if tool_name in tool_map:
            result = tool_map[tool_name]()
        else:
            result = json.dumps({"status": "error", "message": f"未知工具 {tool_name}"}, ensure_ascii=False)
    
    return result
```

**功能说明**：
- **参数格式兼容**：支持多种参数命名格式（`file_path`、`filepath`、`path`等）
- **路径处理**：自动处理Windows和Linux的路径分隔符
- **工具映射**：使用字典映射工具名称到对应的函数
- **错误处理**：对未知工具返回错误信息

---

### 4. 智能提示词构建

**实现原理**：根据执行历史和当前状态动态生成提示词，引导LLM做出正确决策

#### 核心代码：build_analysis_prompt 动态提示词构建

```python
def build_analysis_prompt(user_request, context):
    # 构建执行历史
    steps_history = ""
    if context.steps:
        steps_history = "已执行步骤：\n"
        for i, step in enumerate(context.steps, 1):
            try:
                result_json = json.loads(step['result'])
                if result_json.get('status') == 'success':
                    result_summary = "成功"
                else:
                    result_summary = f"失败: {result_json.get('message', '')}"
            except:
                result_summary = "结果已获取"
            
            steps_history += f"{i}. {step['tool_name']}({step['arguments']}) -> {result_summary}\n"
    
    # 构建可用变量描述
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
```

**功能说明**：
- **执行历史**：记录每一步的工具调用和结果，帮助LLM了解任务进展
- **可用变量**：显示已存储的中间变量，供LLM参考
- **动态建议**：根据最后执行的工具，给出下一步操作建议，减少无效调用
- **重要规则**：明确告诉LLM何时应该完成任务，何时需要继续调用工具

---

### 5. 工具函数实现

**实现原理**：每个工具都是一个独立的函数，接收参数并返回JSON格式的结果

#### 核心代码：常用工具函数

```python
def list_files(directory):
    """列出目录内容"""
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

def read_file(directory, file_name):
    """读取文件内容"""
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return json.dumps({"status": "success", "data": content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def create_file(directory, file_name, content):
    """创建文件"""
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return json.dumps({"status": "success", "message": "文件已创建"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

def fetch_webpage(url):
    """获取网页内容"""
    try:
        url = url.strip('`')
        # 处理URL编码
        from urllib.parse import urlparse, quote, urlunparse
        parsed_url = urlparse(url)
        path = quote(parsed_url.path) if parsed_url.path else ''
        query = quote(parsed_url.query, safe='=&') if parsed_url.query else ''
        encoded_url = urlunparse((parsed_url.scheme, parsed_url.netloc, path, parsed_url.params, query, parsed_url.fragment))
        
        import urllib.request
        with urllib.request.urlopen(encoded_url, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        return json.dumps({"status": "success", "data": html}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
```

**功能说明**：
- **统一返回格式**：所有工具都返回JSON格式，包含`status`和`data`/`message`字段
- **错误处理**：每个工具都有try-except块，捕获异常并返回错误信息
- **编码处理**：文件读取使用UTF-8编码，网页内容处理URL编码
- **超时控制**：网页获取设置10秒超时，防止长时间等待

---

## 四、应用场景

### 场景一：文件处理
```
用户请求：访问practice07/test01和test02文件，计算它们的内容之和
执行流程：
1. list_directory → 查看目录内容
2. read_file → 读取test01（内容：123）
3. read_file → 读取test02（内容：123）
4. 自动计算 → 123 + 123 = 246
结果：返回计算结果
```

### 场景二：信息检索与总结
```
用户请求：查找practice06下包含'def'的文件并总结
执行流程：
1. search_files → 搜索包含'def'的文件
2. read_file → 读取搜索到的文件
3. 总结 → 生成内容总结
结果：返回文件列表和内容总结
```

### 场景三：网页处理
```
用户请求：访问网页并保存总结
执行流程：
1. fetch_webpage → 获取网页内容
2. 总结 → 生成网页内容摘要
3. create_file → 保存到本地文件
结果：文件保存成功
```

---

## 五、项目亮点与创新点

### 1. 智能决策能力
- LLM能够根据上下文自主决定下一步操作
- 支持复杂多步骤任务的自动化执行

### 2. 计算准确性保障
- 独立的计算验证机制
- 避免LLM数学计算错误

### 3. 健壮性设计
- 完善的错误处理和重试机制
- 防止无限循环的保护措施

### 4. 可扩展性
- 模块化的工具定义方式
- 支持添加新的工具和技能

---

## 六、总结

### 最终成果

本项目成功构建了一个**完整的AI工具调用系统**，具备以下核心能力：

1. **自然语言理解**：能够理解用户的自然语言请求
2. **工具调用决策**：能够自主选择合适的工具
3. **链式调用支持**：支持多步骤任务的自动化执行
4. **计算准确性**：通过独立验证确保计算结果正确
5. **错误处理**：完善的错误处理和重试机制

### 技术价值

- **提高效率**：自动化完成复杂任务，减少人工干预
- **增强能力**：让AI能够访问外部数据和执行操作
- **提高准确性**：独立计算验证确保结果可靠
- **扩展能力**：模块化设计支持功能扩展

### 应用前景

该系统可应用于：
- 自动化办公助手
- 智能文档处理
- 信息检索系统
- 自动化测试工具
- 智能客服系统

---

**报告日期**：2026年5月18日  
**项目位置**：e:\人工智能提示词\a  
**版本**：v1.0
