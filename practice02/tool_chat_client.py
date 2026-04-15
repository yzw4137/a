import os
import json
import urllib.request
import urllib.error

def curl(url):
    """
    通过 curl 访问网页并返回网页内容
    
    Args:
        url (str): 要访问的网页 URL
    
    Returns:
        dict: 包含网页内容的结果
    """
    try:
        # 对 URL 进行编码，确保中文字符被正确处理
        import urllib.parse
        parsed_url = urllib.parse.urlparse(url)
        encoded_url = urllib.parse.urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            urllib.parse.quote(parsed_url.path),
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))
        
        with urllib.request.urlopen(encoded_url, timeout=30) as response:
            content = response.read().decode('utf-8')
        return {
            "status": "success",
            "content": content
        }
    except urllib.error.URLError as e:
        return {
            "status": "error",
            "message": f"URL error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# 工具列表，用于系统提示词
tools = [
    {
        "name": "curl",
        "description": "通过 curl 访问网页并返回网页内容",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要访问的网页 URL"
                }
            },
            "required": ["url"]
        }
    }
]
