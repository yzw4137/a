import os

# 测试环境变量加载
env_path = '.env'
if os.path.exists(env_path):
    print(f"环境变量文件存在: {env_path}")
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value
                print(f"加载: {key} = {value}")
    
    print(f"\nBASE_URL: {os.getenv('BASE_URL')}")
    print(f"MODEL: {os.getenv('MODEL')}")
    print(f"API_KEY: {os.getenv('API_KEY')}")
else:
    print(f"环境变量文件不存在: {env_path}")
