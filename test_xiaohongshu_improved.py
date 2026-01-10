import asyncio
import httpx
import re
import json
from crawlers.xiaohongshu.web.utils import URLUtils, NoteIdFetcher

async def test_xiaohongshu_improved():
    """改进的小红书视频解析测试"""
    url = "http://xhslink.com/o/9jkMBGTMmXc"
    print(f"测试URL: {url}")
    
    # 1. 测试URL重定向
    print("\n1. 测试URL重定向")
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Referer": "https://www.xiaohongshu.com/"
        }
        response = await client.get(url, headers=headers)
        print(f"重定向后的URL: {response.url}")
        print(f"状态码: {response.status_code}")
        
        # 2. 提取笔记ID
        print("\n2. 提取笔记ID")
        final_url = str(response.url)
        print(f"最终URL: {final_url}")
        
        # 尝试提取note_id
        note_id_patterns = [
            r"note/([a-zA-Z0-9-]+)",  # 新格式
            r"explore/([a-zA-Z0-9-]+)",  # 旧格式
            r"([a-zA-Z0-9-]{32})"  # 直接匹配32位字符
        ]
        
        note_id = None
        for pattern in note_id_patterns:
            match = re.search(pattern, final_url)
            if match:
                note_id = match.group(1)
                print(f"提取的笔记ID: {note_id}")
                break
        
        if not note_id:
            print("无法提取笔记ID，尝试其他方法")
        
        # 3. 提取INITIAL_STATE
        print("\n3. 提取INITIAL_STATE")
        html_content = response.text
        
        # 使用更精确的正则表达式
        pattern = r'window\.__INITIAL_STATE__\s*=\s*(.+?);\s*window\.__INITIAL_STATE__'  
        match = re.search(pattern, html_content)
        
        if not match:
            # 尝试另一种格式
            pattern = r'window\.__INITIAL_STATE__\s*=\s*(.+?);\s*\(function\('  
            match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            # 尝试更宽泛的匹配
            pattern = r'window\.__INITIAL_STATE__\s*=\s*([^;]+);'  
            match = re.search(pattern, html_content)
        
        if match:
            initial_state_str = match.group(1)
            print(f"提取的INITIAL_STATE长度: {len(initial_state_str)} 字符")
            
            # 保存完整的INITIAL_STATE用于分析
            with open('initial_state_full.txt', 'w', encoding='utf-8') as f:
                f.write(initial_state_str)
            print("已保存完整INITIAL_STATE到initial_state_full.txt")
            
            try:
                # 解析为JSON
                initial_state = json.loads(initial_state_str)
                print("INITIAL_STATE解析为JSON成功")
                print(f"INITIAL_STATE的键: {list(initial_state.keys())}")
                
                # 4. 寻找视频数据
                print("\n4. 寻找视频数据")
                
                # 遍历INITIAL_STATE的键
                for key in initial_state.keys():
                    print(f"检查键: {key}")
                    value = initial_state[key]
                    
                    # 寻找包含note或video的结构
                    if isinstance(value, dict):
                        if 'note' in value:
                            print(f"在{key}中找到note字段")
                            note_data = value['note']
                            
                            if isinstance(note_data, dict):
                                print(f"note的键: {list(note_data.keys())}")
                                
                                if 'video' in note_data:
                                    print("找到video字段")
                                    video_data = note_data['video']
                                    print(f"video的键: {list(video_data.keys())}")
                                    
                                    # 寻找视频URL
                                    if 'media' in video_data:
                                        print("找到media字段")
                                        media = video_data['media']
                                        print(f"media的键: {list(media.keys())}")
                                        
                                        # 尝试各种可能的视频URL字段
                                        possible_video_fields = ['stream', 'url', 'urls', 'playUrl', 'play_url']
                                        for field in possible_video_fields:
                                            if field in media:
                                                print(f"找到视频URL: {media[field]}")
                                                break
                    
                    # 特殊处理可能包含笔记数据的键
                    if key in ['noteDetailMap', 'noteMap', 'notes', 'note']:
                        print(f"深入检查{key}...")
                        
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if 'video' in str(sub_value).lower():
                                    print(f"在{key}.{sub_key}中找到视频相关信息")
                                    
                                    if isinstance(sub_value, dict) and 'video' in sub_value:
                                        print(f"video的键: {list(sub_value['video'].keys())}")
                                        
                                        if 'media' in sub_value['video']:
                                            media = sub_value['video']['media']
                                            print(f"media的键: {list(media.keys())}")
                                            
                                            # 尝试各种可能的视频URL字段
                                            possible_video_fields = ['stream', 'url', 'urls', 'playUrl', 'play_url']
                                            for field in possible_video_fields:
                                                if field in media:
                                                    print(f"找到视频URL: {media[field]}")
                                                    break
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                # 保存失败的JSON用于分析
                with open('broken_json.txt', 'w', encoding='utf-8') as f:
                    f.write(initial_state_str[:1000] + '...')
        else:
            print("未找到window.__INITIAL_STATE__")
            
            # 尝试提取所有script标签内容
            print("\n4. 提取所有script标签内容")
            script_pattern = r'<script[^>]*>(.*?)</script>'
            scripts = re.findall(script_pattern, html_content, re.DOTALL)
            
            # 寻找包含video的script
            video_scripts = []
            for i, script in enumerate(scripts):
                if 'video' in script.lower() and len(script) > 1000:
                    video_scripts.append((i, script))
                    
            print(f"找到 {len(video_scripts)} 个包含video的长script标签")
            
            # 分析这些script标签
            for i, script in video_scripts:
                print(f"\n分析script[{i}]:")
                
                # 尝试提取JSON数据
                json_pattern = r'\{.*\}'
                json_matches = re.findall(json_pattern, script, re.DOTALL)
                
                for j, json_match in enumerate(json_matches):
                    if len(json_match) > 500:
                        print(f"  找到可能的JSON数据块{j}，长度: {len(json_match)}")
                        
                        try:
                            data = json.loads(json_match)
                            print(f"  JSON解析成功，键: {list(data.keys())}")
                            
                            # 寻找视频URL
                            if isinstance(data, dict) and 'video' in data:
                                print("  找到video字段")
                                print(f"  video的键: {list(data['video'].keys())}")
                        except json.JSONDecodeError:
                            pass

if __name__ == "__main__":
    asyncio.run(test_xiaohongshu_improved())