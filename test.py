print("Hello, Python!")
import os
print("Current directory:", os.getcwd())
print("Python version:", os.sys.version)

# 测试环境变量加载
def load_env():
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()
print("BASE_URL:", os.getenv('BASE_URL'))
print("MODEL:", os.getenv('MODEL'))
print("API_KEY:", os.getenv('API_KEY'))