import asyncio
import httpx
import re
import json

async def test_xiaohongshu_simple():
    """使用简单方法提取小红书视频数据"""
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
        
    # 2. 提取INITIAL_STATE - 使用更简单的方法
    print("\n提取INITIAL_STATE")
    
    # 找到window.__INITIAL_STATE__的位置
    start_pos = html_content.find('window.__INITIAL_STATE__ = ')
    if start_pos == -1:
        print("未找到window.__INITIAL_STATE__")
        return
    
    # 从开始位置向后查找下一个window.或</script>标签
    end_pos_window = html_content.find('window.', start_pos + 27)  # 27是'window.__INITIAL_STATE__ = '的长度
    end_pos_script = html_content.find('</script>', start_pos)
    
    # 选择更接近的结束位置
    if end_pos_window == -1:
        end_pos = end_pos_script
    elif end_pos_script == -1:
        end_pos = end_pos_window
    else:
        end_pos = min(end_pos_window, end_pos_script)
    
    if end_pos == -1:
        print("未找到结束位置")
        return
    
    # 提取JSON字符串
    initial_state_str = html_content[start_pos + 27:end_pos].strip()
    
    # 移除末尾可能的分号
    if initial_state_str.endswith(';'):
        initial_state_str = initial_state_str[:-1]
    
    print(f"提取的INITIAL_STATE长度: {len(initial_state_str)} 字符")
    
    # 保存完整的INITIAL_STATE
    with open('initial_state_final.txt', 'w', encoding='utf-8') as f:
        f.write(initial_state_str)
    print("已保存完整INITIAL_STATE到initial_state_final.txt")
    
    # 3. 解析JSON
    print("\n解析JSON")
    try:
        initial_state = json.loads(initial_state_str)
        print("JSON解析成功")
        
        # 4. 寻找视频数据
        print("\n寻找视频数据")
        
        # 检查common字段
        if 'common' in initial_state:
            common = initial_state['common']
            print(f"common的键: {list(common.keys())}")
            
            if 'noteDetailMap' in common:
                note_detail_map = common['noteDetailMap']
                print(f"noteDetailMap的键: {list(note_detail_map.keys())}")
                
                # 遍历noteDetailMap
                for note_id, note_detail in note_detail_map.items():
                    print(f"\n笔记ID: {note_id}")
                    print(f"noteDetail的键: {list(note_detail.keys())}")
                    
                    # 检查是否有视频信息
                    if 'note' in note_detail:
                        note = note_detail['note']
                        print(f"note的键: {list(note.keys())}")
                        
                        if 'video' in note:
                            video = note['video']
                            print(f"video的键: {list(video.keys())}")
                            
                            # 寻找视频URL
                            if 'media' in video:
                                media = video['media']
                                print(f"media的键: {list(media.keys())}")
                                
                                # 尝试各种可能的视频URL字段
                                possible_fields = ['stream', 'url', 'playUrl', 'play_url', 'main_url', 'video_url']
                                for field in possible_fields:
                                    if field in media:
                                        video_url = media[field]
                                        print(f"找到视频URL: {video_url}")
                                        print(f"URL类型: {type(video_url)}")
                                        
                                        # 如果是列表，取第一个
                                        if isinstance(video_url, list):
                                            if video_url:
                                                print(f"视频URL列表的第一个: {video_url[0]}")
                                        break
                            
                            # 检查其他可能的视频URL位置
                            if 'playInfos' in video:
                                play_infos = video['playInfos']
                                print(f"playInfos的长度: {len(play_infos)}")
                                for i, info in enumerate(play_infos):
                                    print(f"playInfo[{i}]的键: {list(info.keys())}")
                                    if 'url' in info:
                                        print(f"playInfo[{i}]的URL: {info['url']}")
    
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"错误位置: {e.pos}")
        print(f"错误行: {e.lineno}, 列: {e.colno}")
        
        # 打印错误附近的内容
        error_start = max(0, e.pos - 100)
        error_end = min(len(initial_state_str), e.pos + 100)
        print(f"错误附近的内容: ...{initial_state_str[error_start:error_end]}...")
    except Exception as e:
        print(f"其他错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_xiaohongshu_simple())