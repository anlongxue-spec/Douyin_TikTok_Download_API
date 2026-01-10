import asyncio
import httpx

async def save_html():
    """保存完整的HTML内容"""
    url = "http://xhslink.com/o/9jkMBGTMmXc"
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Referer": "https://www.xiaohongshu.com/"
        }
        response = await client.get(url, headers=headers)
        
        # 保存完整的HTML内容
        with open('full_html.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"HTML内容已保存到full_html.txt，长度: {len(response.text)} 字符")
        print(f"重定向后的URL: {response.url}")

if __name__ == "__main__":
    asyncio.run(save_html())