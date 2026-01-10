import asyncio
import httpx
import re
import json

async def test_xiaohongshu_json():
    """精确提取和解析小红书的INITIAL_STATE"""
    url = "http://xhslink.com/o/9jkMBGTMmXc"
    print(f"测试URL: {url}")
    
    # 1. 获取HTML内容
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Referer": "https://www.xiaohongshu.com/"
        }
        response = await client.get(url, headers=headers)
        html_content = response.text
        
    # 2. 提取INITIAL_STATE
    print("\n提取INITIAL_STATE")
    pattern = r'window\.__INITIAL_STATE__\s*=\s*(.*?)\s*;\s*\(function\('  
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        initial_state_str = match.group(1)
        print(f"提取的INITIAL_STATE长度: {len(initial_state_str)} 字符")
        
        # 保存完整的INITIAL_STATE
        with open('initial_state_complete.txt', 'w', encoding='utf-8') as f:
            f.write(initial_state_str)
        print("已保存完整INITIAL_STATE到initial_state_complete.txt")
        
        # 3. 解析JSON
        print("\n解析JSON")
        try:
            initial_state = json.loads(initial_state_str)
            print("JSON解析成功")
            
            # 4. 寻找视频数据
            print("\n寻找视频数据")
            
            # 递归查找视频URL
            def find_video_url(data, path=""):
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # 检查是否是视频URL
                        if isinstance(value, str) and ('http' in value and ('.mp4' in value.lower() or 'stream' in key.lower())):
                            print(f"找到视频URL: {value}")
                            print(f"路径: {current_path}")
                            return value, current_path
                        
                        # 递归搜索
                        result = find_video_url(value, current_path)
                        if result:
                            return result
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        current_path = f"{path}[{i}]" if path else f"[{i}]"
                        result = find_video_url(item, current_path)
                        if result:
                            return result
                return None
            
            # 寻找note相关数据
            def find_note_data(data, path=""):
                if isinstance(data, dict):
                    # 检查是否包含note相关字段
                    if 'note' in data or 'noteDetail' in data or any('note' in key.lower() for key in data.keys()):
                        print(f"在{path}找到note相关数据")
                        return data, path
                    
                    # 递归搜索
                    for key, value in data.items():
                        current_path = f"{path}.{key}" if path else key
                        result = find_note_data(value, current_path)
                        if result:
                            return result
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        current_path = f"{path}[{i}]" if path else f"[{i}]"
                        result = find_note_data(item, current_path)
                        if result:
                            return result
                return None
            
            # 先寻找note数据
            note_data, note_path = find_note_data(initial_state) or (None, None)
            
            if note_data:
                print(f"\n在{note_path}找到note数据")
                print(f"note数据的键: {list(note_data.keys())}")
                
                # 在note数据中寻找视频URL
                video_url, video_path = find_video_url(note_data, note_path) or (None, None)
                
                if video_url:
                    print(f"\n最终找到的视频URL: {video_url}")
                else:
                    print("\n在note数据中未找到视频URL")
            else:
                print("\n未找到note相关数据")
                # 在整个INITIAL_STATE中寻找视频URL
                video_url, video_path = find_video_url(initial_state) or (None, None)
                if video_url:
                    print(f"\n在INITIAL_STATE中找到视频URL: {video_url}")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"错误位置: {e.pos}")
            print(f"错误行: {e.lineno}, 列: {e.colno}")
            
            # 打印错误附近的内容
            error_start = max(0, e.pos - 50)
            error_end = min(len(initial_state_str), e.pos + 50)
            print(f"错误附近的内容: ...{initial_state_str[error_start:error_end]}...")
    else:
        print("未找到window.__INITIAL_STATE__")

if __name__ == "__main__":
    asyncio.run(test_xiaohongshu_json())