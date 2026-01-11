import asyncio
import httpx

async def test_fix_with_problematic_url():
    """测试修复后的下载功能，使用用户提供的带有空格和反引号的URL"""
    
    # 用户提供的有问题的URL（带有前后反引号和空格）
    problematic_url = " `https://b23.tv/UzSQvAW` "
    download_endpoint = "http://localhost/api/download"
    
    print(f"测试有问题的URL: '{problematic_url}'")
    print(f"下载API: {download_endpoint}")
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            # 发送下载请求
            print("\n发送下载请求... (这可能需要几分钟)")
            response = await client.get(download_endpoint, params={
                "url": problematic_url,
                "prefix": "true",
                "with_watermark": "false"
            })
            
            print(f"\n下载请求响应:")
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                if response.headers.get('content-type') == 'video/mp4':
                    print("\n✅ 修复成功!")
                    print("✅ 现在可以处理带有空格和反引号的URL")
                    print(f"文件大小: {response.headers.get('content-length', '未知')} 字节")
                    print(f"文件名: {response.headers.get('content-disposition')}")
                else:
                    print("\n❌ 下载失败: 响应不是视频文件")
                    print(f"响应内容: {response.text[:200]}...")
            else:
                print(f"\n❌ 下载失败: {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
                
    except Exception as e:
        print(f"\n❌ 下载请求错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fix_with_problematic_url())
