import asyncio
import json

from crawlers.hybrid.hybrid_crawler import HybridCrawler

HybridCrawler = HybridCrawler()

async def test_bilibili_hybrid_crawler():
    """使用HybridCrawler测试Bilibili无水印链接修复"""
    
    # 测试链接
    test_url = "https://b23.tv/UzSQvAW"
    print(f"测试链接: {test_url}")
    
    try:
        # 调用混合爬虫解析视频
        print("\n开始解析视频数据...")
        data = await HybridCrawler.hybrid_parsing_single_video(test_url, minimal=False)
        
        print(f"\n解析结果:")
        print(f"平台: {data.get('platform')}")
        print(f"类型: {data.get('type')}")
        print(f"标题: {data.get('desc')[:50]}...")
        
        # 检查视频数据
        video_data = data.get('video_data', {})
        if video_data:
            print("\nBilibili视频链接信息:")
            print("-" * 50)
            
            # 打印所有视频链接
            links_info = [
                ("水印视频链接", "wm_video_url"),
                ("水印高清链接", "wm_video_url_HQ"),
                ("无水印视频链接", "nwm_video_url"),
                ("无水印高清链接", "nwm_video_url_HQ"),
                ("音频链接", "audio_url")
            ]
            
            for link_name, link_key in links_info:
                link_value = video_data.get(link_key)
                if link_value:
                    # 只显示前100个字符，避免输出过长
                    print(f"{link_name}: {link_value[:100]}...")
                else:
                    print(f"{link_name}: 无")
            
            # 验证修复效果
            print("\n修复验证:")
            print("-" * 50)
            
            # 检查无水印链接是否存在
            if video_data.get('nwm_video_url'):
                print("✅ 无水印视频链接已返回")
            else:
                print("❌ 无水印视频链接未返回")
            
            if video_data.get('nwm_video_url_HQ'):
                print("✅ 无水印高清链接已返回")
            else:
                print("❌ 无水印高清链接未返回")
            
            # 检查链接是否有区别
            if video_data.get('nwm_video_url') and video_data.get('nwm_video_url_HQ'):
                if video_data['nwm_video_url'] != video_data['nwm_video_url_HQ']:
                    print("✅ 无水印链接和无水印高清链接不同，质量选择逻辑生效")
                else:
                    print("⚠ 无水印链接和无水印高清链接相同，可能是因为只有一个质量的视频流可用")
            
            # 检查音频链接
            if video_data.get('audio_url'):
                print("✅ 音频链接已返回，准备合并")
            else:
                print("❌ 音频链接未返回")
                
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bilibili_hybrid_crawler())
