import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.endpoints.download import fetch_data_stream, merge_bilibili_video_audio, fetch_data
from fastapi import Request
from starlette.testclient import TestClient

class MockRequest:
    """模拟 FastAPI Request 对象"""
    async def is_disconnected(self):
        return False

async def test_headers_processing():
    """测试 headers 参数处理是否正确"""
    print("测试 headers 参数处理...")
    
    # 测试 fetch_data 函数
    print("\n1. 测试 fetch_data 函数:")
    
    # 测试 1: 不传递 headers
    print("   - 测试不传递 headers:")
    try:
        result = await fetch_data("https://www.example.com")
        print("     ✓ 成功: 默认 headers 工作正常")
    except Exception as e:
        print(f"     ✗ 失败: {e}")
    
    # 测试 2: 直接传递 headers 字典
    print("   - 测试直接传递 headers 字典:")
    headers = {
        'User-Agent': 'Test Agent',
        'Test-Header': 'Test Value'
    }
    try:
        result = await fetch_data("https://www.example.com", headers=headers)
        print("     ✓ 成功: 直接传递 headers 字典工作正常")
    except Exception as e:
        print(f"     ✗ 失败: {e}")
    
    # 测试 3: 传递包含 headers 键的字典
    print("   - 测试传递包含 headers 键的字典:")
    headers_wrapper = {
        'headers': {
            'User-Agent': 'Test Agent Wrapper',
            'Test-Header-Wrapper': 'Test Value Wrapper'
        }
    }
    try:
        result = await fetch_data("https://www.example.com", headers=headers_wrapper)
        print("     ✓ 成功: 传递包含 headers 键的字典工作正常")
    except Exception as e:
        print(f"     ✗ 失败: {e}")
    
    print("\n2. 测试 fetch_data_stream 函数:")
    mock_request = MockRequest()
    
    # 创建临时测试文件
    import tempfile
    test_file = tempfile.mktemp(suffix='.txt')
    
    # 测试 1: 不传递 headers
    print("   - 测试不传递 headers:")
    try:
        result = await fetch_data_stream("https://www.example.com", mock_request, file_path=test_file)
        print(f"     ✓ 成功: 默认 headers 工作正常, 结果: {result}")
    except Exception as e:
        print(f"     ✗ 失败: {e}")
    
    # 测试 2: 直接传递 headers 字典
    print("   - 测试直接传递 headers 字典:")
    headers = {
        'User-Agent': 'Test Agent',
        'Test-Header': 'Test Value'
    }
    try:
        result = await fetch_data_stream("https://www.example.com", mock_request, headers=headers, file_path=test_file)
        print(f"     ✓ 成功: 直接传递 headers 字典工作正常, 结果: {result}")
    except Exception as e:
        print(f"     ✗ 失败: {e}")
    
    # 测试 3: 传递包含 headers 键的字典
    print("   - 测试传递包含 headers 键的字典:")
    headers_wrapper = {
        'headers': {
            'User-Agent': 'Test Agent Wrapper',
            'Test-Header-Wrapper': 'Test Value Wrapper'
        }
    }
    try:
        result = await fetch_data_stream("https://www.example.com", mock_request, headers=headers_wrapper, file_path=test_file)
        print(f"     ✓ 成功: 传递包含 headers 键的字典工作正常, 结果: {result}")
    except Exception as e:
        print(f"     ✗ 失败: {e}")
    
    # 清理临时文件
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    asyncio.run(test_headers_processing())
