import requests

# 测试错误的URL（没有/api前缀）
print("测试1: 访问错误的URL路径 /download")
try:
    response = requests.get("http://localhost:80/download?url=https://b23.tv/UzSQvAW&with_watermark=false")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:100]}...")
except Exception as e:
    print(f"请求失败: {e}")

# 测试正确的URL（有/api前缀）
print("\n测试2: 访问正确的URL路径 /api/download")
try:
    response = requests.get("http://localhost:80/api/download?url=https://b23.tv/UzSQvAW&with_watermark=false")
    print(f"状态码: {response.status_code}")
    print(f"响应内容长度: {len(response.content)} 字节")
    print(f"响应头: {dict(response.headers)[:5]}")
except Exception as e:
    print(f"请求失败: {e}")
