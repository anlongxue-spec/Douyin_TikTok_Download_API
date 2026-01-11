import asyncio
import httpx

async def test_api_response():
    """测试API响应格式"""
    video_url = "https://b23.tv/UzSQvAW"
    api_endpoint = "http://localhost/api/hybrid/video_data"
    
    print(f"测试链接: {video_url}")
    print(f"API端点: {api_endpoint}")
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(api_endpoint, params={"url": video_url})
            
            print(f"\nHTTP状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"\n响应内容:")
            print(response.text)
            
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_response())
