import asyncio
import httpx
import re
import json

async def test_xiaohongshu_new_format():
    """测试小红书新格式URL和视频解析"""
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
        
        # 处理新的URL格式: discovery/item/note_id
        note_id_pattern = r'discovery/item/([a-zA-Z0-9-]+)'
        match = re.search(note_id_pattern, final_url)
        
        if match:
            note_id = match.group(1)
            print(f"正确提取的笔记ID: {note_id}")
        else:
            print("无法提取笔记ID")
        
        # 3. 分析script标签
        print("\n3. 分析script标签")
        html_content = response.text
        
        # 寻找所有script标签
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, html_content, re.DOTALL)
        
        # 寻找包含video的script标签
        video_script = None
        for i, script in enumerate(scripts):
            if 'video' in script.lower() and len(script) > 1000:
                video_script = script
                print(f"找到包含video的script标签，长度: {len(script)} 字符")
                
                # 保存这个script的内容
                with open('video_script.txt', 'w', encoding='utf-8') as f:
                    f.write(script)
                print("已保存video script到video_script.txt")
                break
        
        if video_script:
            # 尝试提取JSON数据
            print("\n4. 尝试提取JSON数据")
            
            # 寻找JSON的开始和结束
            json_start = video_script.find('{')
            json_end = video_script.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_str = video_script[json_start:json_end+1]
                print(f"提取的JSON长度: {len(json_str)}")
                
                # 保存JSON到文件
                with open('extracted_json.txt', 'w', encoding='utf-8') as f:
                    f.write(json_str)
                print("已保存提取的JSON到extracted_json.txt")
                
                # 尝试解析JSON
                try:
                    data = json.loads(json_str)
                    print("JSON解析成功")
                    print(f"JSON的键: {list(data.keys())}")
                    
                    # 递归查找视频URL
                    def find_video_url(data, path=""):
                        if isinstance(data, dict):
                            for key, value in data.items():
                                current_path = f"{path}.{key}" if path else key
                                
                                # 检查是否是视频URL
                                if isinstance(value, str) and ('http' in value and ('.mp4' in value or 'video' in value.lower() or 'stream' in key.lower())):
                                    print(f"找到视频URL: {value}")
                                    print(f"路径: {current_path}")
                                    return value
                                
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
                    
                    video_url = find_video_url(data)
                    if video_url:
                        print(f"\n成功找到视频URL: {video_url}")
                    else:
                        print("\n未找到视频URL")
                        
                        # 打印完整的JSON结构以便分析
                        print("\nJSON结构分析:")
                        def print_json_structure(data, indent=0, max_depth=3):
                            if indent > max_depth:
                                return
                            
                            if isinstance(data, dict):
                                for key, value in data.items():
                                    print('  ' * indent + f"- {key}:")
                                    print_json_structure(value, indent + 1, max_depth)
                            elif isinstance(data, list):
                                print('  ' * indent + f"- [列表，长度: {len(data)}]")
                                if data:
                                    print_json_structure(data[0], indent + 1, max_depth)
                            else:
                                print('  ' * indent + f"- {type(value).__name__}: {str(value)[:50]}...")
                        
                        print_json_structure(data)
                        
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
                    print(f"错误位置: {e.pos}")
                    print(f"错误行: {e.lineno}, 列: {e.colno}")
                    
                    # 打印错误附近的内容
                    error_start = max(0, e.pos - 100)
                    error_end = min(len(json_str), e.pos + 100)
                    print(f"错误附近的内容: ...{json_str[error_start:error_end]}...")

if __name__ == "__main__":
    asyncio.run(test_xiaohongshu_new_format())