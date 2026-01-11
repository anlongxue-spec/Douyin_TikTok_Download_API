import asyncio
import httpx

async def test_url_paths():
    base_url = "http://localhost"
    
    # 测试不同的路径
    paths_to_test = [
        "/download",              # 无/api前缀，应该返回404
        "/api/download",          # 有/api前缀，应该返回200
        "/",                      # 根路径，可能返回404或欢迎页
        "/api/",                  # /api根路径
        "/wrong/path"             # 不存在的路径，应该返回404
    ]
    
    print(f"测试基础URL: {base_url}")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        for path in paths_to_test:
            url = f"{base_url}{path}"
            print(f"\n测试路径: {path}")
            print(f"完整URL: {url}")
            
            try:
                # 发送简单的GET请求
                response = await client.get(url)
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 404:
                    print("✗ 404 Not Found")
                    # 打印部分响应内容
                    if len(response.text) > 100:
                        print(f"响应内容: {response.text[:100]}...")
                    else:
                        print(f"响应内容: {response.text}")
                elif response.status_code == 200:
                    print("✓ 200 OK")
                    # 对于API路径，尝试添加必要的参数
                    if path == "/api/download":
                        print("\n  尝试带参数调用API:")
                        params = {
                            "url": "https://b23.tv/UzSQvAW",
                            "prefix": "true",
                            "with_watermark": "false"
                        }
                        try:
                            api_response = await client.get(url, params=params)
                            print(f"  状态码: {api_response.status_code}")
                            if api_response.status_code == 200:
                                print("  ✓ API调用成功")
                                if 'content-disposition' in api_response.headers:
                                    print(f"  ✓ 文件下载开始")
                                else:
                                    print(f"  响应头: {dict(api_response.headers)}")
                        except Exception as e:
                            print(f"  ✗ API调用失败: {e}")
                else:
                    print(f"? 状态码: {response.status_code}")
                    print(f"  响应头: {dict(response.headers)}")
                    
            except Exception as e:
                print(f"✗ 请求失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(test_url_paths())
