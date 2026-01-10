#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书初始化状态数据提取脚本
XiaoHongShu initial state data extraction script
"""

import asyncio
import httpx
import re
import json

async def extract_initial_state():
    """
    提取小红书的初始化状态数据
    Extract XiaoHongShu initial state data
    """
    print("=== 提取小红书初始化状态数据 ===")
    
    note_id = "67703823000000000251a047"
    html_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.xiaohongshu.com/",
        "Cookie": "",  # 可以尝试添加一个有效的Cookie
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(html_url, headers=headers)
            
            if response.status_code == 200:
                html_content = response.text
                
                # 精确查找window.__INITIAL_STATE__
                initial_state_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});\s*window\.__FRONTEND_CDN__'  # 使用更精确的正则表达式
                
                match = re.search(initial_state_pattern, html_content, re.DOTALL)
                
                if match:
                    print("✅ 找到初始化状态数据")
                    json_str = match.group(1)
                    
                    # 尝试解析JSON
                    try:
                        data = json.loads(json_str)
                        print(f"✅ JSON解析成功！数据类型: {type(data)}")
                        print(f"数据键: {list(data.keys())}")
                        
                        # 保存完整的JSON数据
                        with open("xiaohongshu_initial_state.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print("✅ 完整JSON数据已保存到文件: xiaohongshu_initial_state.json")
                        
                        # 检查是否有note相关数据
                        if 'note' in data:
                            print("\n✅ 找到note数据")
                            note_data = data['note']
                            print(f"note数据键: {list(note_data.keys())}")
                            
                            # 检查是否有视频数据
                            if 'video' in note_data:
                                print("✅ 找到视频数据")
                                video_data = note_data['video']
                                print(f"视频数据键: {list(video_data.keys())}")
                                
                                # 检查是否有media数据
                                if 'media' in video_data:
                                    print("✅ 找到media数据")
                                    media_data = video_data['media']
                                    print(f"media数据键: {list(media_data.keys())}")
                                    
                                    # 检查是否有stream URL
                                    if 'stream' in media_data:
                                        print(f"✅ 找到视频流URL: {media_data['stream']}")
                                        return media_data['stream']
                                    else:
                                        print("❌ media数据中没有stream字段")
                                else:
                                    print("❌ 视频数据中没有media字段")
                            else:
                                print("❌ note数据中没有video字段")
                        else:
                            print("❌ 数据中没有note字段")
                            
                        # 检查是否有feed相关数据
                        if 'feed' in data:
                            print("\n✅ 找到feed数据")
                            feed_data = data['feed']
                            print(f"feed数据键: {list(feed_data.keys())}")
                            
                            # 检查是否有items数据
                            if 'items' in feed_data:
                                print(f"✅ 找到items数据，共 {len(feed_data['items'])} 项")
                                
                                # 保存items数据
                                with open("xiaohongshu_items.json", "w", encoding="utf-8") as f:
                                    json.dump(feed_data['items'], f, ensure_ascii=False, indent=2)
                                print("✅ items数据已保存到文件: xiaohongshu_items.json")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {e}")
                        print(f"JSON字符串前500字符: {json_str[:500]}...")
                        print(f"JSON字符串后500字符: {json_str[-500:]}...")
                        
                        # 尝试保存部分JSON数据
                        with open("xiaohongshu_json_partial.txt", "w", encoding="utf-8") as f:
                            f.write(json_str[:10000])  # 保存前10000字符
                        print("✅ 部分JSON数据已保存到文件: xiaohongshu_json_partial.txt")
                else:
                    print("❌ 未找到window.__INITIAL_STATE__")
                    
                    # 尝试其他方式
                    simple_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
                    match = re.search(simple_pattern, html_content, re.DOTALL)
                    
                    if match:
                        print("✅ 使用简单模式找到初始化状态数据")
                        json_str = match.group(1)
                        
                        # 保存到文件
                        with open("xiaohongshu_simple.json", "w", encoding="utf-8") as f:
                            f.write(json_str[:10000])
                        print("✅ 简单模式JSON数据已保存到文件: xiaohongshu_simple.json")
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 提取数据失败: {e}")
        import traceback
        traceback.print_exc()
    
    return None

async def main():
    video_url = await extract_initial_state()
    
    if video_url:
        print(f"\n🎉 成功提取到视频URL: {video_url}")
    else:
        print("\n❌ 未能提取到视频URL")

if __name__ == "__main__":
    asyncio.run(main())
