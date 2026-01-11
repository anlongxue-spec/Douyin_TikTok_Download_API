import asyncio
from crawlers.hybrid.hybrid_crawler import HybridCrawler

async def test_bilibili_parse():
    crawler = HybridCrawler()
    data = await crawler.hybrid_parsing_single_video('https://b23.tv/UzSQvAW', minimal=True)
    print('解析结果键:', data.keys())
    print('平台:', data.get('platform'))
    print('类型:', data.get('type'))
    print('视频ID:', data.get('video_id'))
    video_data = data.get('video_data', {})
    print('视频数据键:', video_data.keys())
    print('视频URL(高清):', video_data.get('nwm_video_url_HQ'))
    print('视频URL(普通):', video_data.get('nwm_video_url'))
    print('音频URL:', video_data.get('audio_url'))
    print('有水印视频URL:', video_data.get('wm_video_url'))

if __name__ == "__main__":
    asyncio.run(test_bilibili_parse())