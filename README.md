# LLM 工具调用客户端项目

本项目实现了一个基于 LLM 的工具调用客户端，支持文件操作、网络访问、聊天历史搜索和文档仓库访问等功能。

## 项目结构

```
.
├── practice01/         # 基础聊天功能
├── practice02/         # 基本工具调用功能
├── practice03/         # 聊天总结功能
├── practice04/         # 聊天历史管理和搜索功能
├── practice05/         # 文档仓库访问功能
├── practice06/         # 技能系统集成功能
├── practice07/         # 链式工具调用功能
├── chat-log/           # 聊天历史记录
├── .agents/            # 技能目录
│   └── skills/         # 技能列表
│       └── notice/      # 通知撰写技能
├── .gitignore          # Git 忽略文件
├── README.md           # 项目说明
├── env.example         # 环境变量示例
├── run_test.bat        # 测试脚本
└── test.py             # 测试文件
```

## 功能说明

### practice01
- 基础聊天功能
- 实现了与 LLM 的基本对话能力

### practice02
- 基本工具调用功能
- 支持文件操作（列出、重命名、删除、创建、读取）
- 支持网络访问（curl 工具）

### practice03
- 聊天总结功能
- 能够对聊天历史进行总结，压缩上下文

### practice04
- 聊天历史管理和搜索功能
- 支持聊天历史的存储和搜索
- 实现了关键信息提取（5W 规则）
- 支持按轮次或上下文长度自动总结聊天历史

### practice05
- 文档仓库访问功能
- 在 practice04 的基础上添加了 AnythingLLM 文档仓库访问能力
- 支持通过 API 访问本地 AnythingLLM 服务

### practice06
- 技能系统集成功能
- 在 practice05 的基础上添加了技能系统
- 支持自动读取 .agents/skills 目录下的技能
- 支持加载和使用技能执行任务
- 已集成通知撰写技能

### practice07
- 链式工具调用功能（Chained Tool Calls）
- 在 practice06 的基础上实现了链式工具调用能力
- 支持前一个工具的输出作为后一个工具的输入参数
- 实现了 ChainedCallContext 上下文管理器，记录每一步的调用和结果
- 实现了 execute_chained_tool_call 执行函数，支持自动决策和多步骤任务执行
- 设置最大迭代次数（默认10次），防止无限循环
- 支持同时处理 JSON 格式和 OpenAI tool_calls 格式的响应

## 环境配置

1. 复制 `env.example` 文件为 `.env`
2. 填写以下环境变量：
   - `BASE_URL`：LLM API 基础 URL
   - `MODEL`：使用的模型名称
   - `API_KEY`：LLM API 密钥
   - `TEMPERATURE`：生成文本的温度参数（可选，默认 0.7）
   - `MAX_TOKENS`：最大生成 tokens 数（可选，默认 8192）
   - `LOG_PATH`：聊天历史日志路径（可选，默认项目根目录）
   - `ANYTHINGLLM_API_KEY`：AnythingLLM API 密钥（practice05 需用）
   - `ANYTHINGLLM_WORKSPACE_SLUG`：AnythingLLM 工作区 slug（practice05 需用）
   - `ANYTHINGLLM_TIMEOUT`：AnythingLLM 请求超时时间（可选，默认 300 秒）

## 使用方法

### practice04 使用方法
1. 进入 practice04 目录
2. 运行 `python tool_client.py`
3. 输入消息开始聊天
4. 可用命令：
   - 列出目录内容：`列出当前目录的文件`
   - 访问网页：`访问 https://www.example.com 并总结内容`
   - 搜索聊天历史：`/search 我之前说了什么`

### practice05 使用方法
1. 确保本地运行了 AnythingLLM 服务
2. 进入 practice05 目录
3. 运行 `python tool_client.py`
4. 输入消息开始聊天
5. 当提到"文档仓库"、"文件仓库"、"仓库"时，会自动调用 AnythingLLM 文档仓库访问工具

### practice06 使用方法
1. 进入 practice06 目录
2. 运行 `python tool_client.py`
3. 输入消息开始聊天
4. 当需要撰写通知、修改通知、润色通知时，会自动调用 notice 技能
5. 示例：
   - 撰写五一节放假通知（不指定部门）：`撰写一个五一节放假的通知`
   - 撰写五一节放假通知（指定销售部）：`我是销售部的，撰写一个五一节放假的通知`

### practice07 使用方法
1. 进入 practice07 目录
2. 运行 `python tool_client.py`
3. 输入消息开始聊天
4. 当检测到复杂任务（包含"查找"和"总结"等关键词）时，会自动使用链式调用功能
5. 链式调用示例：
   - 文件搜索链式调用：`请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容`
   - 技能查询链式调用：`我想了解notice技能的详细规则`
   - 网页处理链式调用：`访问 https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html 并总结页面内容，保存到practice07/summary.txt`

## 工具列表

### practice04 工具
1. `list_directory`：列出指定目录下的所有文件和目录
2. `rename_file`：修改指定目录下的文件名称
3. `delete_file`：删除指定目录下的文件
4. `create_file`：在指定目录下创建新文件并写入内容
5. `read_file`：读取指定目录下的文件内容
6. `fetch_webpage`：访问指定 URL 的网页并返回内容
7. `search_chat_history`：搜索聊天历史记录

### practice05 工具（在 practice04 基础上添加）
8. `anythingllm_query`：访问 AnythingLLM 文档仓库

### practice06 工具（在 practice05 基础上添加）
9. `load_skill_content`：加载技能的正文内容

### practice07 工具（在 practice06 基础上添加）
10. `search_files`：搜索指定目录下包含关键字的文件

## 技能列表

### notice 技能
- **名称**：notice
- **描述**：用于撰写通知、修改通知、润色通知。通知不能以"通知"二字开头，必须冠以"XX部"的前缀，例如"采购部通知""宣传部通知"等。如果用户没有告知所在部门，就使用"XX部"代替。
- **使用场景**：当用户需要撰写通知、修改通知、润色通知时使用

## 注意事项

1. 确保 LLM API 服务正常运行
2. practice05 需要本地运行 AnythingLLM 服务
3. 聊天历史会自动保存到 `log.txt` 文件中
4. 每 5 轮对话会自动总结聊天历史并提取关键信息
5. 当上下文长度超过 3000 字符时，会自动总结聊天历史
6. practice06 会自动读取 .agents/skills 目录下的技能，无需手动配置

## 测试

运行 `run_test.bat` 脚本进行测试，或直接运行 `python test.py`。

## 实验报告

各 practice 目录下均包含对应的实验报告，详细说明功能实现和测试结果。