import os
import json
from datetime import datetime

def list_files(directory):
    """
    列出某个目录下的所有文件及其基本属性
    
    Args:
        directory (str): 目录路径
    
    Returns:
        dict: 包含文件列表和每个文件的属性
    """
    try:
        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    "name": filename,
                    "size": stat.st_size,  # 文件大小（字节）
                    "mtime": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),  # 修改时间
                    "mode": stat.st_mode  # 文件权限模式
                })
        return {
            "status": "success",
            "files": files
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def rename_file(directory, old_name, new_name):
    """
    修改某个目录下某个文件的名字
    
    Args:
        directory (str): 目录路径
        old_name (str): 旧文件名
        new_name (str): 新文件名
    
    Returns:
        dict: 操作结果
    """
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if not os.path.exists(old_path):
            return {
                "status": "error",
                "message": f"File {old_name} does not exist"
            }
        
        os.rename(old_path, new_path)
        return {
            "status": "success",
            "message": f"File renamed from {old_name} to {new_name}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def delete_file(directory, filename):
    """
    删除某个目录下的某个文件
    
    Args:
        directory (str): 目录路径
        filename (str): 文件名
    
    Returns:
        dict: 操作结果
    """
    try:
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": f"File {filename} does not exist"
            }
        
        os.remove(filepath)
        return {
            "status": "success",
            "message": f"File {filename} deleted successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def create_file(directory, filename, content):
    """
    在某个目录下新建1个文件，并且写入内容
    
    Args:
        directory (str): 目录路径
        filename (str): 文件名
        content (str): 文件内容
    
    Returns:
        dict: 操作结果
    """
    try:
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"File {filename} created successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def read_file(directory, filename):
    """
    读取某个目录下的某个文件的内容
    
    Args:
        directory (str): 目录路径
        filename (str): 文件名
    
    Returns:
        dict: 包含文件内容的结果
    """
    try:
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": f"File {filename} does not exist"
            }
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "content": content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# 工具列表，用于系统提示词
tools = [
    {
        "name": "list_files",
        "description": "列出某个目录下的所有文件及其基本属性",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                }
            },
            "required": ["directory"]
        }
    },
    {
        "name": "rename_file",
        "description": "修改某个目录下某个文件的名字",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "old_name": {
                    "type": "string",
                    "description": "旧文件名"
                },
                "new_name": {
                    "type": "string",
                    "description": "新文件名"
                }
            },
            "required": ["directory", "old_name", "new_name"]
        }
    },
    {
        "name": "delete_file",
        "description": "删除某个目录下的某个文件",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "filename": {
                    "type": "string",
                    "description": "文件名"
                }
            },
            "required": ["directory", "filename"]
        }
    },
    {
        "name": "create_file",
        "description": "在某个目录下新建1个文件，并且写入内容",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "filename": {
                    "type": "string",
                    "description": "文件名"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容"
                }
            },
            "required": ["directory", "filename", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "读取某个目录下的某个文件的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "filename": {
                    "type": "string",
                    "description": "文件名"
                }
            },
            "required": ["directory", "filename"]
        }
    }
]