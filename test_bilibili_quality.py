import asyncio
import httpx
import re
import json

async def test_bilibili_video_quality():
    """测试Bilibili视频质量排序和无水印链接选择"""
    
    # 从B23短链获取BV号
    async def get_bv_id(url):
        if "b23.tv" in url:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, follow_redirects=True)
                url = str(response.url)
        
        bv_pattern = r'(?:video\/|\/)(BV[A-Za-z0-9]+)'
        match = re.search(bv_pattern, url)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"无法从URL提取BV号: {url}")
    
    # 测试链接
    test_url = "https://b23.tv/UzSQvAW"
    bv_id = await get_bv_id(test_url)
    
    print(f"BV号: {bv_id}")
    
    # 获取视频详情
    print("\n获取视频详情...")
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        # 获取视频详情API
        detail_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
        detail_response = await client.get(detail_url)
        
        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            cid = detail_data['data']['cid']
            print(f"视频CID: {cid}")
            print(f"视频标题: {detail_data['data']['title']}")
            
            # 获取视频流API
            print("\n获取视频流信息...")
            playurl_url = f"https://api.bilibili.com/x/player/wbi/playurl?bvid={bv_id}&cid={cid}&qn=0&fnval=80&fourk=1"
            
            # 设置正确的请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.bilibili.com/"
            }
            
            playurl_response = await client.get(playurl_url, headers=headers)
            
            if playurl_response.status_code == 200:
                playurl_data = playurl_response.json()
                
                # 检查视频流
                dash = playurl_data.get('data', {}).get('dash', {})
                video_list = dash.get('video', [])
                audio_list = dash.get('audio', [])
                
                print(f"\n找到 {len(video_list)} 个视频流")
                print(f"找到 {len(audio_list)} 个音频流")
                
                if video_list:
                    print("\n视频流详情:")
                    print("-" * 40)
                    
                    # 按质量排序前
                    for i, video in enumerate(video_list):
                        print(f"视频流 {i+1}:")
                        print(f"  质量: {video.get('quality')}")
                        print(f"  分辨率: {video.get('width')}x{video.get('height')}")
                        print(f"  编码: {video.get('codecs')}")
                        print(f"  带宽: {video.get('bandwidth')}")
                        print(f"  链接前缀: {video.get('baseUrl')[:50]}...")
                    
                    # 按视频质量排序 (修复后的逻辑)
                    sorted_video_list = sorted(video_list, key=lambda x: x.get('quality', 0), reverse=True)
                    sorted_audio_list = sorted(audio_list, key=lambda x: x.get('bandwidth', 0), reverse=True) if audio_list else []
                    
                    print("\n按质量排序后的视频流:")
                    print("-" * 40)
                    for i, video in enumerate(sorted_video_list):
                        print(f"视频流 {i+1} (质量: {video.get('quality')}):")
                        print(f"  分辨率: {video.get('width')}x{video.get('height')}")
                        print(f"  链接前缀: {video.get('baseUrl')[:50]}...")
                    
                    # 验证修复后的选择
                    selected_video = sorted_video_list[0].get('baseUrl')
                    nwm_video_url_HQ = sorted_video_list[1].get('baseUrl') if len(sorted_video_list) > 1 else selected_video
                    
                    print("\n修复后的链接选择:")
                    print("-" * 40)
                    print(f"无水印视频链接: {selected_video[:50]}...")
                    print(f"无水印高清链接: {nwm_video_url_HQ[:50]}...")
                    
                    if len(sorted_video_list) > 1:
                        if selected_video != nwm_video_url_HQ:
                            print("\n✅ 修复成功: 无水印链接和高清链接使用不同质量的视频流")
                        else:
                            print("\n⚠ 修复效果有限: 只有一个视频流可用")
                    else:
                        print("\n⚠ 修复效果有限: 只有一个视频流可用")
            else:
                print(f"获取视频流失败: {playurl_response.status_code}")
        else:
            print(f"获取视频详情失败: {detail_response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_bilibili_video_quality())
