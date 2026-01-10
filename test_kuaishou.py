import sys
import os
import asyncio
from crawlers.hybrid.hybrid_crawler import HybridCrawler

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_kuaishou_parse():
    print("测试快手视频解析...")
    hybrid_crawler = HybridCrawler()
    url = "https://v.kuaishou.com/n5T01Jd1"
    
    try:
        # 测试精简模式输出
        result = await hybrid_crawler.hybrid_parsing_single_video(url, minimal=True)
        print("精简模式解析结果:", result)
    except Exception as e:
        print(f"解析失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kuaishou_parse())