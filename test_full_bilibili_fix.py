import asyncio
import httpx
import json

async def test_bilibili_download():
    # 测试链接
    video_url = "https://b23.tv/UzSQvAW"
    api_endpoint = "http://localhost/api/download"
    
    # 请求参数
    params = {
        "url": video_url,
        "prefix": "true",
        "with_watermark": "false"
    }
    
    print(f"测试链接: {video_url}")
    print(f"API端点: {api_endpoint}")
    print(f"请求参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
    
    try:
        # 创建HTTP客户端
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            # 发送请求
            print("\n发送请求...")
            response = await client.get(api_endpoint, params=params)
            
            print(f"\n响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 检查响应头
                print(f"响应头: {dict(response.headers)}")
                
                # 如果是文件下载，检查Content-Disposition
                if 'content-disposition' in response.headers:
                    print(f"\n✓ 文件下载成功")
                    print(f"文件名: {response.headers['content-disposition']}")
                    print(f"文件大小: {response.headers.get('content-length', '未知')} 字节")
                else:
                    # 如果不是文件，打印响应内容
                    try:
                        content = response.json()
                        print(f"\n响应内容: {json.dumps(content, ensure_ascii=False, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"\n响应内容(文本): {response.text}")
            else:
                print(f"\n✗ 请求失败")
                try:
                    content = response.json()
                    print(f"错误信息: {json.dumps(content, ensure_ascii=False, indent=2)}")
                except json.JSONDecodeError:
                    print(f"响应内容: {response.text}")
                    
    except httpx.TimeoutException:
        print(f"\n✗ 请求超时")
    except Exception as e:
        print(f"\n✗ 发生错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bilibili_download())
