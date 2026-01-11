import asyncio
import httpx
import json

async def test_bilibili_nwm_link():
    """测试Bilibili无水印视频链接是否准确返回"""
    
    # 测试链接
    video_url = "https://b23.tv/UzSQvAW"
    api_endpoint = "http://localhost/api/hybrid/video_data"
    
    print(f"测试链接: {video_url}")
    print(f"API端点: {api_endpoint}")
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            # 发送请求获取视频数据
            print("\n发送请求获取视频数据...")
            response = await client.get(api_endpoint, params={"url": video_url})
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nAPI响应状态: {data.get('code')}")
                
                # 检查视频数据
                video_data = data.get('data', {}).get('video_data', {})
                if video_data:
                    print("\nBilibili视频链接信息:")
                    print("-" * 40)
                    print(f"水印视频链接: {video_data.get('wm_video_url')[:50]}...")
                    print(f"水印高清链接: {video_data.get('wm_video_url_HQ')[:50]}...")
                    print(f"无水印视频链接: {video_data.get('nwm_video_url')[:50]}...")
                    print(f"无水印高清链接: {video_data.get('nwm_video_url_HQ')[:50]}...")
                    print(f"音频链接: {video_data.get('audio_url')[:50]}...")
                    
                    # 验证无水印链接是否不同
                    if video_data.get('nwm_video_url') and video_data.get('nwm_video_url_HQ'):
                        if video_data['nwm_video_url'] != video_data['nwm_video_url_HQ']:
                            print("\n✅ 无水印视频链接和无水印高清链接不同")
                        else:
                            print("\n⚠ 无水印视频链接和无水印高清链接相同")
                    
                    # 测试获取播放链接详情
                    await test_playurl_details(video_data.get('nwm_video_url'), client)
                else:
                    print("\n❌ 未获取到视频数据")
            else:
                print(f"\n❌ API请求失败: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"\n❌ 请求错误: {e}")
        import traceback
        traceback.print_exc()

async def test_playurl_details(video_url, client):
    """测试视频链接是否可访问"""
    if not video_url:
        return
        
    print("\n测试无水印视频链接可访问性...")
    try:
        # 发送HEAD请求检查链接是否有效
        response = await client.head(video_url, timeout=httpx.Timeout(10.0))
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 无水印视频链接可访问")
            if 'content-length' in response.headers:
                print(f"文件大小: {int(response.headers['content-length'])} 字节")
            if 'content-type' in response.headers:
                print(f"内容类型: {response.headers['content-type']}")
        else:
            print(f"❌ 无水印视频链接不可访问: {response.status_code}")
    except Exception as e:
        print(f"❌ 检查链接时发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_bilibili_nwm_link())
