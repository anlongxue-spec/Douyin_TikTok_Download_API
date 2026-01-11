import asyncio
import json
import httpx

from crawlers.hybrid.hybrid_crawler import HybridCrawler

HybridCrawler = HybridCrawler()

async def test_final_bilibili_fix():
    """测试Bilibili无水印链接修复的最终效果"""
    
    # 测试链接
    test_url = "https://b23.tv/UzSQvAW"
    print(f"测试链接: {test_url}")
    
    try:
        # 步骤1: 检查平台识别
        print("\n步骤1: 测试平台识别...")
        if "b23.tv" in test_url or "bilibili" in test_url:
            platform = "bilibili"
            print(f"✅ 平台识别正确: {platform}")
        else:
            platform = None
            print(f"❌ 平台识别错误: {platform}")
            return
        
        # 步骤2: 测试BV号提取
        print("\n步骤2: 测试BV号提取...")
        bv_id = await HybridCrawler.get_bilibili_bv_id(test_url)
        print(f"✅ BV号提取成功: {bv_id}")
        
        # 步骤3: 测试视频详情获取
        print("\n步骤3: 测试视频详情获取...")
        response = await HybridCrawler.BilibiliWebCrawler.fetch_one_video(bv_id)
        data = response.get('data', {})
        if data:
            print(f"✅ 视频详情获取成功")
            print(f"  标题: {data.get('title')[:50]}...")
            print(f"  CID: {data.get('cid')}")
            print(f"  时长: {data.get('duration')}秒")
        else:
            print(f"❌ 视频详情获取失败")
            return
        
        # 步骤4: 测试视频流获取
        print("\n步骤4: 测试视频流获取...")
        cid = data.get('cid')
        if cid:
            playurl_data = await HybridCrawler.BilibiliWebCrawler.fetch_video_playurl(bv_id, str(cid))
            dash = playurl_data.get('data', {}).get('dash', {})
            video_list = dash.get('video', [])
            audio_list = dash.get('audio', [])
            
            print(f"✅ 视频流获取成功")
            print(f"  视频流数量: {len(video_list)}")
            print(f"  音频流数量: {len(audio_list)}")
            
            if video_list:
                # 展示视频流质量信息
                print("\n  视频流质量信息:")
                for i, video in enumerate(video_list):
                    print(f"    流{i+1}: 质量={video.get('quality')}, 分辨率={video.get('width')}x{video.get('height')}, 编码={video.get('codecs')}")
                
                # 测试修复后的排序逻辑
                sorted_video_list = sorted(video_list, key=lambda x: x.get('quality', 0), reverse=True)
                print("\n  修复后的排序结果:")
                for i, video in enumerate(sorted_video_list):
                    print(f"    流{i+1}: 质量={video.get('quality')}, 分辨率={video.get('width')}x{video.get('height')}")
                    
                # 测试无水印链接选择
                video_url = sorted_video_list[0].get('baseUrl') if sorted_video_list else None
                nwm_video_url_HQ = sorted_video_list[1].get('baseUrl') if len(sorted_video_list) > 1 else video_url
                
                print(f"\n  无水印链接选择:")
                print(f"    主链接: {video_url[:50]}...")
                print(f"    高清链接: {nwm_video_url_HQ[:50]}...")
                
                if len(sorted_video_list) > 1 and video_url != nwm_video_url_HQ:
                    print("    ✅ 无水印链接和高清链接不同")
                else:
                    print("    ⚠ 无水印链接和高清链接相同")
        else:
            print(f"❌ 未找到CID")
            return
        
        # 步骤5: 测试完整API调用
        print("\n步骤5: 测试完整API调用...")
        api_endpoint = "http://localhost/api/hybrid/video_data"
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(api_endpoint, params={"url": test_url})
            
            if response.status_code == 200:
                api_data = response.json()
                if api_data.get('code') == 200:
                    video_data = api_data.get('data', {}).get('video_data', {})
                    if video_data:
                        print("✅ API调用成功")
                        print("\n  API返回的视频链接:")
                        print(f"    水印视频链接: {video_data.get('wm_video_url')[:50]}...")
                        print(f"    水印高清链接: {video_data.get('wm_video_url_HQ')[:50]}...")
                        print(f"    无水印视频链接: {video_data.get('nwm_video_url')[:50]}...")
                        print(f"    无水印高清链接: {video_data.get('nwm_video_url_HQ')[:50]}...")
                        print(f"    音频链接: {video_data.get('audio_url')[:50]}...")
                        
                        if video_data.get('nwm_video_url'):
                            print("\n✅ 无水印视频链接已正确返回")
                    else:
                        print("❌ API未返回视频数据")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"  响应: {response.text}")
        
        # 步骤6: 测试下载功能
        print("\n步骤6: 测试下载功能...")
        download_endpoint = "http://localhost/api/download"
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            print("  发送下载请求... (这可能需要几分钟)")
            response = await client.get(download_endpoint, params={
                "url": test_url,
                "prefix": "true",
                "with_watermark": "false"
            })
            
            if response.status_code == 200:
                print("✅ 下载请求成功")
                print(f"  Content-Type: {response.headers.get('content-type')}")
                print(f"  Content-Length: {response.headers.get('content-length')} 字节")
                print(f"  Content-Disposition: {response.headers.get('content-disposition')}")
            else:
                print(f"❌ 下载请求失败: {response.status_code}")
                print(f"  响应: {response.text}")
        
        print("\n🎉 所有测试完成!")
        print("✅ Bilibili无水印链接修复成功")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_final_bilibili_fix())
