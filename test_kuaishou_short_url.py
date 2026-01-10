import asyncio
from crawlers.kuaishou.web.web_crawler import KuaiShouWebCrawler

async def test_kuaishou_short_url():
    """
    测试快手短链接处理
    """
    # 用户提供的快手短链接
    short_url = "https://v.kuaishou.com/n5T01Jd1"
    
    try:
        # 创建快手爬虫实例
        crawler = KuaiShouWebCrawler()
        
        # 从短链接获取视频数据
        print(f"正在处理短链接: {short_url}")
        video_data = await crawler.fetch_video_from_url(short_url)
        
        print("\n视频数据获取成功:")
        print(f"视频标题: {video_data.get('data', {}).get('visionVideoDetail', {}).get('photo', {}).get('caption', '')}")
        print(f"作者: {video_data.get('data', {}).get('visionVideoDetail', {}).get('author', {}).get('name', '')}")
        print(f"播放量: {video_data.get('data', {}).get('visionVideoDetail', {}).get('photo', {}).get('playCount', 0)}")
        print(f"点赞数: {video_data.get('data', {}).get('visionVideoDetail', {}).get('photo', {}).get('likeCount', 0)}")
        
    except Exception as e:
        print(f"处理失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_kuaishou_short_url())