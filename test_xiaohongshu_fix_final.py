import asyncio
from crawlers.hybrid.hybrid_crawler import HybridCrawler

async def test_xiaohongshu_fix():
    """测试修复后的小红书视频解析功能"""
    url = "http://xhslink.com/o/9jkMBGTMmXc"
    print(f"测试小红书视频解析: {url}")
    
    # 初始化混合爬虫
    crawler = HybridCrawler()
    
    try:
        # 调用解析方法
        result = await crawler.hybrid_parsing_single_video(url, minimal=True)
        print("\n解析结果:")
        print(f"类型: {result.get('type')}")
        print(f"平台: {result.get('platform')}")
        print(f"视频ID: {result.get('video_id')}")
        print(f"作者ID: {result.get('author_id')}")
        print(f"作者昵称: {result.get('author_name')}")
        
        # 安全地获取并打印视频描述
        desc = result.get('desc', '')
        print(f"视频描述: {desc[:50] if desc else ''}...")
        
        print(f"有水印视频URL: {result.get('wm_video_url')}")
        print(f"无水印视频URL: {result.get('nwm_video_url')}")
        
        # 打印完整结果用于调试
        print("\n完整结果:")
        print(result)
        
        # 检查视频URL是否提取成功
        if result.get('nwm_video_url'):
            print("\n✅ 修复成功！视频URL提取成功")
        else:
            print("\n❌ 修复失败！未提取到视频URL")
            
            # 打印详细错误信息
            print("\n详细响应数据:")
            print(result)
            
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_xiaohongshu_fix())