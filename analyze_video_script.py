import json

# 读取保存的video_script.txt文件
with open('video_script.txt', 'r', encoding='utf-8') as f:
    script_content = f.read()

print(f"script内容长度: {len(script_content)} 字符")

# 提取INITIAL_STATE
start_pos = script_content.find('window.__INITIAL_STATE__ = ')
if start_pos == -1:
    print("未找到window.__INITIAL_STATE__")
else:
    # 从开始位置到末尾
    initial_state_str = script_content[start_pos + 27:].strip()  # 27是'window.__INITIAL_STATE__ = '的长度
    
    # 移除末尾可能的函数调用
    end_pos = initial_state_str.find('; (function(')
    if end_pos != -1:
        initial_state_str = initial_state_str[:end_pos].strip()
    
    print(f"提取的INITIAL_STATE长度: {len(initial_state_str)} 字符")
    
    # 保存提取的INITIAL_STATE
    with open('initial_state_from_script.txt', 'w', encoding='utf-8') as f:
        f.write(initial_state_str)
    
    # 尝试解析JSON
    try:
        data = json.loads(initial_state_str)
        print("JSON解析成功")
        
        # 寻找noteDetailMap
        if 'common' in data:
            common = data['common']
            print(f"common的键: {list(common.keys())}")
            
            if 'noteDetailMap' in common:
                note_detail_map = common['noteDetailMap']
                print(f"noteDetailMap的键: {list(note_detail_map.keys())}")
                
                # 遍历noteDetailMap
                for note_id, note_detail in note_detail_map.items():
                    print(f"\n笔记ID: {note_id}")
                    print(f"noteDetail的键: {list(note_detail.keys())}")
                    
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
                                        print(f"找到视频URL: {media[field]}")
                                        break
                            
                            # 检查playInfos
                            if 'playInfos' in video:
                                play_infos = video['playInfos']
                                print(f"playInfos长度: {len(play_infos)}")
                                for i, info in enumerate(play_infos):
                                    print(f"playInfo[{i}]的键: {list(info.keys())}")
                                    if 'url' in info:
                                        print(f"找到playInfo URL: {info['url']}")
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"错误位置: {e.pos}")
        
        # 打印错误附近的内容
        error_start = max(0, e.pos - 100)
        error_end = min(len(initial_state_str), e.pos + 100)
        print(f"错误附近的内容: ...{initial_state_str[error_start:error_end]}...")