import asyncio
import httpx
import re
from bs4 import BeautifulSoup
from crawlers.xiaohongshu.web.web_crawler import XiaoHongShuWebCrawler
from crawlers.xiaohongshu.web.utils import URLUtils, NoteIdFetcher

async def test_xiaohongshu_parsing():
    """测试小红书视频解析"""
    url = "http://xhslink.com/o/9jkMBGTMmXc"
    print(f"测试URL: {url}")
    
    # 初始化小红书爬虫
    crawler = XiaoHongShuWebCrawler()
    
    # 测试URL标准化
    normalized_url = URLUtils.normalize_url(url)
    print(f"标准化后的URL: {normalized_url}")
    
    # 测试笔记ID提取
    note_id = NoteIdFetcher.extract_note_id_from_url(normalized_url)
    print(f"提取的笔记ID: {note_id}")
    
    try:
        # 测试API调用
        response = await crawler.fetch_note_from_url(url)
        print(f"API响应状态: {'成功' if response else '失败'}")
        print(f"API响应数据类型: {type(response)}")
        if response:
            print(f"API响应数据: {response}")
            
            # 检查响应结构
            print("\n响应结构分析:")
            if 'data' in response:
                print("- 包含data字段")
                data = response['data']
                print(f"  data类型: {type(data)}")
                print(f"  data内容: {data}")
                
                if 'note' in data:
                    print("- data包含note字段")
                    note = data['note']
                    print(f"  note类型: {type(note)}")
                    print(f"  note内容: {note}")
                    
                    # 检查视频字段
                    if 'video' in note:
                        print("- note包含video字段")
                        video = note['video']
                        print(f"  video类型: {type(video)}")
                        print(f"  video内容: {video}")
                        
                        # 检查视频URL
                        if 'media' in video:
                            print("- video包含media字段")
                            media = video['media']
                            print(f"  media类型: {type(media)}")
                            print(f"  media内容: {media}")
                            
                            if 'stream' in media:
                                print(f"- media包含stream字段: {media['stream']}")
                            else:
                                print("- media不包含stream字段")
                                print(f"  media的键: {list(media.keys())}")
                        else:
                            print("- video不包含media字段")
                            print(f"  video的键: {list(video.keys())}")
                    else:
                        print("- note不包含video字段")
                        print(f"  note的键: {list(note.keys())}")
                else:
                    print("- data不包含note字段")
                    print(f"  data的键: {list(data.keys())}")
            else:
                print("- 不包含data字段")
                print(f"  响应的键: {list(response.keys())}")
    except Exception as e:
        print(f"API调用失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 尝试直接访问URL获取HTML内容
    print("\n" + "="*50)
    print("尝试直接访问URL获取HTML内容")
    print("="*50)
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Referer": "https://www.xiaohongshu.com/"
            }
            response = await client.get(url, headers=headers)
            print(f"HTML请求状态码: {response.status_code}")
            
            if response.status_code == 200:
                html_content = response.text
                print(f"HTML内容长度: {len(html_content)} 字符")
                
                # 尝试提取window.__INITIAL_STATE__
                print("\n尝试提取window.__INITIAL_STATE__")
                pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'  
                match = re.search(pattern, html_content, re.DOTALL)
                
                if match:
                    initial_state = match.group(1)
                    print(f"提取的INITIAL_STATE长度: {len(initial_state)} 字符")
                    
                    # 保存部分INITIAL_STATE用于分析
                    with open('initial_state_part.txt', 'w', encoding='utf-8') as f:
                        f.write(initial_state[:5000] + '...')  # 只保存前5000字符
                    print("已保存部分INITIAL_STATE到initial_state_part.txt")
                    
                    # 尝试解析为JSON
                    try:
                        import json
                        data = json.loads(initial_state)
                        print("INITIAL_STATE解析为JSON成功")
                        print(f"INITIAL_STATE的键: {list(data.keys())}")
                        
                        # 寻找视频数据
                        if 'note' in data:
                            print("找到note字段")
                            note = data['note']
                            print(f"note的键: {list(note.keys())}")
                            
                            if 'video' in note:
                                print("找到video字段")
                                video = note['video']
                                print(f"video的键: {list(video.keys())}")
                    except json.JSONDecodeError as e:
                        print(f"JSON解析失败: {e}")
                else:
                    print("未找到window.__INITIAL_STATE__")
                    
                # 尝试使用BeautifulSoup解析
                print("\n尝试使用BeautifulSoup解析HTML")
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 寻找script标签
                scripts = soup.find_all('script')
                print(f"找到 {len(scripts)} 个script标签")
                
                # 寻找可能包含视频信息的script标签
                for i, script in enumerate(scripts):
                    if script.string and ('video' in script.string.lower() or 'media' in script.string.lower()):
                        print(f"script[{i}] 包含视频相关信息")
                        # 保存部分内容
                        with open(f'script_{i}_part.txt', 'w', encoding='utf-8') as f:
                            f.write(script.string[:2000] + '...')
            else:
                print(f"HTML请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"HTML请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_xiaohongshu_parsing())