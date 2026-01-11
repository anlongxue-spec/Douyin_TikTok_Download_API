import asyncio
from crawlers.hybrid.hybrid_crawler import HybridCrawler

HybridCrawler = HybridCrawler()

async def test_resolution_sorting():
    """测试基于分辨率的视频流排序逻辑"""
    
    # 测试链接
    test_url = "https://b23.tv/UzSQvAW"
    print(f"测试链接: {test_url}")
    
    try:
        # 获取BV号和CID
        bv_id = await HybridCrawler.get_bilibili_bv_id(test_url)
        print(f"BV号: {bv_id}")
        
        response = await HybridCrawler.BilibiliWebCrawler.fetch_one_video(bv_id)
        data = response.get('data', {})
        cid = data.get('cid')
        print(f"CID: {cid}")
        
        if cid:
            # 获取视频流数据
            playurl_data = await HybridCrawler.BilibiliWebCrawler.fetch_video_playurl(bv_id, str(cid))
            dash = playurl_data.get('data', {}).get('dash', {})
            video_list = dash.get('video', [])
            
            print(f"\n找到 {len(video_list)} 个视频流")
            
            # 展示原始视频流
            print("\n原始视频流:")
            print("-" * 50)
            for i, video in enumerate(video_list):
                resolution = video.get('width', 0) * video.get('height', 0)
                print(f"流{i+1}: 分辨率={video.get('width')}x{video.get('height')} ({resolution}px), 编码={video.get('codecs')[:20]}")
            
            # 应用修复后的排序逻辑
            print("\n修复后的排序逻辑:")
            print("-" * 50)
            # 按视频分辨率(宽*高)从高到低排序，分辨率相同则按带宽排序
            sorted_video_list = sorted(video_list, 
                                      key=lambda x: (x.get('width', 0) * x.get('height', 0), x.get('bandwidth', 0)), 
                                      reverse=True) if video_list else []
            
            # 展示排序后的视频流
            for i, video in enumerate(sorted_video_list):
                resolution = video.get('width', 0) * video.get('height', 0)
                print(f"流{i+1}: 分辨率={video.get('width')}x{video.get('height')} ({resolution}px), 编码={video.get('codecs')[:20]}")
            
            # 选择最高质量和次高质量的视频
            if sorted_video_list:
                highest_quality = sorted_video_list[0]
                second_highest = sorted_video_list[1] if len(sorted_video_list) > 1 else highest_quality
                
                print("\n选择结果:")
                print("-" * 30)
                print(f"最高质量视频:")
                print(f"  分辨率: {highest_quality.get('width')}x{highest_quality.get('height')}")
                print(f"  编码: {highest_quality.get('codecs')}")
                print(f"  链接前缀: {highest_quality.get('baseUrl')[:50]}...")
                
                if second_highest != highest_quality:
                    print(f"\n次高质量视频:")
                    print(f"  分辨率: {second_highest.get('width')}x{second_highest.get('height')}")
                    print(f"  编码: {second_highest.get('codecs')}")
                    print(f"  链接前缀: {second_highest.get('baseUrl')[:50]}...")
                
                print("\n✅ 视频流排序成功，选择了最高质量的视频")
                return True
            
        return False
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_resolution_sorting())
