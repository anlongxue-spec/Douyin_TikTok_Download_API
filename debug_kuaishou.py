import sys
import os
import asyncio
import httpx
import re
from crawlers.kuaishou.web.utils import URLUtils, PhotoIdFetcher

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_url_processing():
    print("调试快手URL处理...")
    url = "https://v.kuaishou.com/n5T01Jd1"
    
    print(f"原始URL: {url}")
    
    # 测试URL标准化
    normalized_url = URLUtils.normalize_url(url)
    print(f"标准化后URL: {normalized_url}")
    
    # 测试是否为短链接
    is_short = URLUtils.is_short_url(normalized_url)
    print(f"是否为短链接: {is_short}")
    
    # 获取完整URL
    if is_short:
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(normalized_url)
                full_url = str(response.url)
                print(f"短链接跳转后URL: {full_url}")
                
                # 测试photoId提取
                photo_id = PhotoIdFetcher.extract_photo_id_from_url(full_url)
                print(f"提取到的photoId: {photo_id}")
                
                # 查看完整的响应内容
                print("\n响应内容前500字符:")
                print(response.text[:500])
        except Exception as e:
            print(f"短链接跳转失败: {type(e).__name__}: {e}")
    
    # 手动测试一些正则表达式
    print("\n手动测试正则表达式:")
    patterns = [
        r"short-video/([a-zA-Z0-9]+)",
        r"fw/photo/([a-zA-Z0-9]+)",
        r"photoId=([a-zA-Z0-9]+)"
    ]
    
    # 假设我们有一个示例URL
    sample_full_urls = [
        "https://www.kuaishou.com/short-video/xxxxxx",
        "https://www.kuaishou.com/fw/photo/yyyyyy",
        "https://www.kuaishou.com/graphql?photoId=zzzzzz"
    ]
    
    for sample_url in sample_full_urls:
        print(f"\n测试URL: {sample_url}")
        for pattern in patterns:
            match = re.search(pattern, sample_url)
            if match:
                print(f"  正则 {pattern}: 匹配到 {match.group(1)}")

if __name__ == "__main__":
    asyncio.run(debug_url_processing())