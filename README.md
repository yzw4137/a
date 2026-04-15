# AI 智能体开发教学项目

## 项目概述

这是一个基于 Python 的 AI 智能体开发教学项目，演示如何使用 OpenAI 兼容的 API 访问本地或远程 LLM 模型。

## 环境配置

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install requests python-dotenv
```

### 2. 配置环境变量

复制 `env.example` 文件为 `.env` 并填写相应配置：

```bash
cp env.example .env
```

编辑 `.env` 文件：

```
# OpenAI Compatible LLM Configuration
BASE_URL=http://localhost:1234/v1  # LM Studio 本地服务器地址
MODEL=qwen3.5-4b  # 模型名称
API_KEY=lm-studio  # API 密钥
TEMPERATURE=0.7
MAX_TOKENS=1000
```

## 使用方法

### 1. 启动本地模型服务

如果使用 LM Studio：
1. 打开 LM Studio
2. 加载模型（如 qwen3.5-4b）
3. 进入 Developer > Local Server
4. 启动服务器（Status 变为 Running）

### 2. 运行聊天脚本

```bash
# 基本测试脚本
python practice01/llm_access.py

# 交互式聊天脚本（支持流式输出和历史记录）
python practice01/chat_interface.py
```

## 脚本功能

### llm_access.py
- 基本的 LLM API 访问测试
- 统计 token 消耗、响应时间和速度
- 适合作为 API 调用的示例

### chat_interface.py
- 交互式终端聊天界面
- 支持流式输出（实时显示模型响应）
- 自动管理聊天历史记录
- 循环运行直到用户按 Ctrl+C 退出

## 支持的模型部署

- **LM Studio**：本地部署，默认地址 `http://localhost:1234/v1`
- **Ollama**：本地部署，默认地址 `http://localhost:11434/v1`
- **LocalAI**：本地部署，默认地址 `http://localhost:8080/v1`
- **OpenAI**：云服务，地址 `https://api.openai.com/v1`

## 故障排查

1. **连接错误**：检查本地服务器是否运行，地址是否正确
2. **API 密钥错误**：确保 `.env` 文件中的 API_KEY 正确
3. **模型错误**：确保指定的模型已在本地加载
4. **端口占用**：如果端口被占用，修改 `.env` 文件中的端口号

## 项目结构

```
├── practice01/
│   ├── llm_access.py        # 基本 API 测试脚本
│   └── chat_interface.py    # 交互式聊天脚本
├── .env                     # 环境配置文件
├── .env.example             # 环境配置示例
├── .gitignore               # Git 忽略文件
└── README.md                # 项目说明
```