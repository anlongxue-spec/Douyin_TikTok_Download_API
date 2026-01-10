import asyncio
import httpx

async def test_video_url_access():
    """
    直接测试快手视频URL是否可以访问
    """
    # 使用从测试中获取到的视频URL
    video_url = "https://v2-zj-bjun.kwaicdn.com/upic/2026/01/02/08/BMjAyNjAxMDIwODA5MjRfMTc0MjgyODMyOV8xODM5ODkxMDI1ODBfMV8z_b_Bfc3d4df487213824ef435cfa1ba91762.mp4?tag=1-1768048739-unknown-0-ll3nzrjryj-54ecc67fb9374bfa&provider=self&clientCacheKey=3xrdqtrtuvpsqg9_b.mp4&di=72f5d42e&bp=10004&x-ks-ptid=183989102580&kwai-not-alloc=self-cdn&kcdntag=p:Beijing;i:ChinaUnicom;ft:UNKNOWN;h:COLD;pn:kuaishouVideoProjection&Aecs=172.17.4.197&ocid=100000628&tt=b&ss=vps"
    
    print(f"Testing direct access to video URL: {video_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            # 添加快手的Referer和User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.kuaishou.com/'
            }
            
            # 只请求头部信息，不下载整个文件
            response = await client.head(video_url, headers=headers, follow_redirects=True)
            
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            print("✓ SUCCESS: Video URL is accessible")
            return True
        else:
            print(f"✗ FAILURE: Video URL returned status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAILURE: Exception occurred: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_video_url_access())