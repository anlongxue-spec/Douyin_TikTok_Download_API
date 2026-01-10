import asyncio
import httpx
import re
import json
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_weibo_video():
    """测试微博视频解析"""
    url = "https://video.weibo.com/show?fid=1034:5245644953288730"
    print(f"测试微博视频解析: {url}")
    
    try:
        # 获取视频页面，跟随重定向
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Referer": "https://weibo.com/",
            }
            response = await client.get(url, headers=headers)
            html_content = response.text
            
        print(f"页面状态码: {response.status_code}")
        print(f"页面大小: {len(html_content)} 字节")
        
        # 提取视频ID
        fid_pattern = r'fid=1034:([a-zA-Z0-9]+)'
        fid_match = re.search(fid_pattern, url)
        if fid_match:
            video_id = fid_match.group(1)
            print(f"提取到视频ID: {video_id}")
        
        # 保存页面内容到文件，方便分析
        with open("weibo_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("页面内容已保存到 weibo_page.html")
        
        # 尝试提取视频信息
        print("\n=== 尝试提取视频信息 ===")
        
        # 方法1: 查找所有可能的视频相关数据
        patterns = [
            r'\bvideo(?:Data|Info|Url|Src|Path)\s*=\s*([^;]+);',
            r'\b(?:play|video)_info\s*=\s*([^;]+);',
            r'\b(?:video|media)_urls?\s*=\s*([^;]+);',
            r'\bswf\.addVariable\(["\']video(?:_url)?["\'],\s*["\']([^"\']+)["\']\)',
            r'\b(?:mp4|flv|avi|mov|wmv|webm)\s*[:=]\s*["\']([^"\']+)',
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                print(f"模式{i+1} 找到匹配: {match.group(1)[:100]}...")
        
        # 方法2: 查找JSON数据
        json_patterns = [
            r'({\s*"(?:video|play|media).*?})',
            r'\[\s*{\s*"(?:video|play|media).*?}\s*\]',
        ]
        
        for i, pattern in enumerate(json_patterns):
            matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    json_data = json.loads(match.group(1))
                    print(f"JSON模式{i+1} 解析成功: {type(json_data).__name__}, 键: {list(json_data.keys()) if isinstance(json_data, dict) else len(json_data) if isinstance(json_data, list) else ''}")
                except json.JSONDecodeError:
                    print(f"JSON模式{i+1} 找到可能的JSON: {match.group(1)[:100]}...")
        
        # 方法3: 查找script标签中的关键信息
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        print(f"\n=== 找到 {len(script_tags)} 个script标签 ===")
        
        for i, script in enumerate(script_tags):
            if any(keyword in script.lower() for keyword in ['video', 'play', 'media', 'fid']):
                if len(script) > 500:
                    print(f"Script {i+1} 包含视频相关内容，长度: {len(script)} 字节")
                else:
                    print(f"Script {i+1}: {script.strip()}")
        
        # 方法4: 尝试调用微博API
        if fid_match:
            print("\n=== 尝试调用微博API ===")
            fid = fid_match.group(0)  # 完整的fid参数
            api_url = f"https://video.weibo.com/show?{fid}"
            print(f"尝试API URL: {api_url}")
            
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    api_response = await client.get(api_url, headers=headers)
                    print(f"API响应状态码: {api_response.status_code}")
                    print(f"API响应大小: {len(api_response.text)} 字节")
                    
                    # 检查API响应中是否有视频URL
                    video_url_pattern = r'(https?://[^"\']*\.(?:mp4|flv|avi|mov|wmv|webm))'
                    video_urls = re.findall(video_url_pattern, api_response.text)
                    if video_urls:
                        print(f"找到视频URL: {video_urls[:3]}")  # 只显示前3个
            except Exception as e:
                print(f"API调用失败: {e}")
        
        # 方法6: 直接尝试微博视频播放API
        if fid_match:
            print("\n=== 尝试直接调用微博视频播放API ===")
            video_id = fid_match.group(1)
            # 构建直接的视频播放API URL
            direct_api_url = f"https://weibo.com/tv/api/component?page=/tv/show/{video_id}&type=mp4"
            print(f"尝试直接API URL: {direct_api_url}")
            
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    # 需要正确的Cookie才能访问API
                    headers.update({
                        "Cookie": "SUB=_2AkMVpM6Xf8NxqwJRmP4TzmPgaoyH-jyYsmR9An7uJhMyAxgv7X9jqmgMbt-R6ARqFk7m9bA1wL0Cye20xT6cFgJ34e0H",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-Requested-With": "XMLHttpRequest"
                    })
                    payload = {
                        "data": json.dumps({
                            "Component_Play_Playinfo": {
                                "oid": f"1034:{video_id}",
                                "plid": "",
                                "quality": 4,
                                "isHttps": 1,
                                "cType": 12
                            }
                        })
                    }
                    api_response = await client.post(direct_api_url, headers=headers, data=payload, timeout=10)
                    print(f"直接API响应状态码: {api_response.status_code}")
                    print(f"直接API响应内容:")
                    print(api_response.text)
                    
                    # 解析JSON响应
                    try:
                        api_data = json.loads(api_response.text)
                        print(f"\n解析API响应成功")
                        # 检查数据结构
                        if "data" in api_data and "Component_Play_Playinfo" in api_data["data"]:
                            play_info = api_data["data"]["Component_Play_Playinfo"]
                            print(f"播放信息包含以下键: {list(play_info.keys())}")
                            
                            # 查找视频URL
                            if "urls" in play_info:
                                print(f"视频URLs: {play_info['urls']}")
                            elif "mp4_720p" in play_info:
                                print(f"720p视频URL: {play_info['mp4_720p']}")
                            elif "mp4_hd" in play_info:
                                print(f"高清视频URL: {play_info['mp4_hd']}")
                            elif "mp4_sd" in play_info:
                                print(f"标清视频URL: {play_info['mp4_sd']}")
                    except json.JSONDecodeError as e:
                        print(f"解析API响应失败: {e}")
            except Exception as e:
                print(f"直接API调用失败: {e}")
        
        # 方法7: 查看重定向后的最终URL
        print(f"\n=== 重定向信息 ===")
        print(f"原始URL: {url}")
        print(f"最终URL: {str(response.url)}")
        print(f"重定向历史: {[str(h) for h in response.history]}")
        
        # 方法5: 查找iframe
        iframe_pattern = r'<iframe[^>]*src=["\']([^"\']+)["\'][^>]*>'
        iframes = re.findall(iframe_pattern, html_content)
        print(f"\n=== 找到 {len(iframes)} 个iframe ===")
        for iframe in iframes:
            print(f"Iframe src: {iframe}")
            # 尝试获取iframe内容
            try:
                async with httpx.AsyncClient() as client:
                    iframe_response = await client.get(iframe, headers=headers, timeout=10)
                    print(f"  Iframe响应状态码: {iframe_response.status_code}")
                    print(f"  Iframe响应大小: {len(iframe_response.text)} 字节")
                    # 在iframe内容中查找视频URL
                    video_url_pattern = r'(https?://[^"\']*\.(?:mp4|flv))'
                    iframe_video_urls = re.findall(video_url_pattern, iframe_response.text)
                    if iframe_video_urls:
                        print(f"  找到视频URL: {iframe_video_urls[:3]}")
            except Exception as e:
                print(f"  获取iframe内容失败: {e}")
            
    except Exception as e:
        print(f"解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_weibo_video())