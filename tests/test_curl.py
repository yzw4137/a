from practice02.tools import curl

# 测试 curl 功能，获取青城山的天气预报
url = "https://wttr.in/青城山"
result = curl(url)

if result['status'] == 'success':
    print("获取成功！")
    print("天气预报内容：")
    print(result['content'])
else:
    print(f"获取失败：{result['message']}")
