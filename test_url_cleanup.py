import asyncio
import re

from crawlers.hybrid.hybrid_crawler import HybridCrawler

HybridCrawler = HybridCrawler()

async def test_url_cleanup():
    """测试URL清理功能"""
    
    # 原始有问题的URL
    problematic_url = " `https://b23.tv/UzSQvAW` "
    print(f"原始URL: '{problematic_url}'")
    print(f"URL长度: {len(problematic_url)}")
    
    # 测试平台识别
    if "bilibili" in problematic_url or "b23.tv" in problematic_url:
        print("✅ 平台条件匹配成功")
    else:
        print("❌ 平台条件匹配失败")
    
    # 清理URL
    cleaned_url = problematic_url.strip()  # 去除首尾空格
    cleaned_url = re.sub(r'^`|`$', '', cleaned_url)  # 去除首尾反引号
    print(f"\n清理后的URL: '{cleaned_url}'")
    print(f"清理后长度: {len(cleaned_url)}")
    
    # 测试清理后的平台识别
    if "bilibili" in cleaned_url or "b23.tv" in cleaned_url:
        print("✅ 清理后平台条件匹配成功")
    else:
        print("❌ 清理后平台条件匹配失败")
    
    # 测试BV号提取
    print("\n测试BV号提取:")
    try:
        bv_id = await HybridCrawler.get_bilibili_bv_id(cleaned_url)
        print(f"✅ BV号提取成功: {bv_id}")
    except Exception as e:
        print(f"❌ BV号提取失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_url_cleanup())
