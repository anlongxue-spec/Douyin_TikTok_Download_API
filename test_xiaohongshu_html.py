#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书HTML页面爬虫测试脚本
XiaoHongShu HTML page crawler test script
"""

import asyncio
import httpx
import re
import json
from bs4 import BeautifulSoup

async def test_html_crawling():
    """
    测试从HTML页面中提取视频数据
    Test extracting video data from HTML page
    """
    print("=== 测试从HTML页面提取视频数据 ===")
    
    note_id = "67703823000000000251a047"
    html_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.xiaohongshu.com/",
        "Cookie": "",  # 可以尝试添加一个有效的Cookie
        "Content-Type": "text/html",
        "Origin": "https://www.xiaohongshu.com"
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(html_url, headers=headers)
            
            print(f"状态码: {response.status_code}")
            print(f"内容类型: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                html_content = response.text
                
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 尝试从script标签中提取JSON数据
                scripts = soup.find_all('script')
                
                json_data_found = False
                
                for i, script in enumerate(scripts):
                    script_content = script.string
                    if script_content:
                        # 尝试查找各种可能的JSON数据
                        if 'INITIAL_STATE' in script_content or 'initialState' in script_content:
                            print(f"\n✅ 脚本 {i+1} 包含初始化状态数据")
                            print(f"脚本内容前500字符: {script_content[:500]}...")
                            
                            # 尝试使用正则表达式提取JSON
                            try:
                                # 查找JSON对象的开始和结束
                                json_match = re.search(r'\{[\s\S]*\}', script_content)
                                if json_match:
                                    json_str = json_match.group(0)
                                    try:
                                        data = json.loads(json_str)
                                        print(f"✅ JSON解析成功")
                                        
                                        # 保存JSON数据到文件
                                        with open(f"xiaohongshu_data_{i}.json", "w", encoding="utf-8") as f:
                                            json.dump(data, f, ensure_ascii=False, indent=2)
                                        print(f"✅ JSON数据已保存到文件: xiaohongshu_data_{i}.json")
                                        
                                        json_data_found = True
                                    except json.JSONDecodeError:
                                        print("❌ JSON解析失败")
                            except Exception as e:
                                print(f"❌ 处理脚本 {i+1} 失败: {e}")
                        elif 'video' in script_content.lower() and 'media' in script_content.lower():
                            print(f"\n✅ 脚本 {i+1} 包含video和media数据")
                            print(f"脚本内容前1000字符: {script_content[:1000]}...")
                        elif 'note' in script_content.lower() and 'user' in script_content.lower():
                            print(f"\n✅ 脚本 {i+1} 包含note和user数据")
                            print(f"脚本内容前1000字符: {script_content[:1000]}...")
                
                if not json_data_found:
                    print("\n❌ 未找到明确的JSON数据，尝试保存部分HTML内容")
                    
                    # 保存前100行HTML内容到文件
                    with open("xiaohongshu_snippet.html", "w", encoding="utf-8") as f:
                        lines = html_content.split('\n')
                        f.write('\n'.join(lines[:100]))
                    print("✅ HTML片段已保存到文件: xiaohongshu_snippet.html")
                    
                # 如果没有找到script标签中的JSON数据，尝试查找iframe
                iframes = soup.find_all('iframe')
                if iframes:
                    print(f"\n找到 {len(iframes)} 个iframe")
                    for i, iframe in enumerate(iframes):
                        src = iframe.get('src')
                        print(f"iframe {i+1} src: {src}")
                
                # 尝试查找video标签
                videos = soup.find_all('video')
                if videos:
                    print(f"\n找到 {len(iframes)} 个video标签")
                    for i, video in enumerate(videos):
                        src = video.get('src')
                        print(f"video {i+1} src: {src}")
                        
                # 保存HTML内容到文件
                with open("xiaohongshu.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("\n✅ HTML内容已保存到文件: xiaohongshu.html")
                
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_html_crawling())
