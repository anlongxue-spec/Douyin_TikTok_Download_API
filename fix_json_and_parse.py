# 修复JSON中的undefined值
with open('extracted_json_manual.txt', 'r', encoding='utf-8') as f:
    json_str = f.read()

# 将undefined替换为null
fixed_json_str = json_str.replace('undefined', 'null')

# 保存修复后的JSON
with open('fixed_json.txt', 'w', encoding='utf-8') as f:
    f.write(fixed_json_str)

print("已将undefined替换为null并保存到fixed_json.txt")

# 尝试解析修复后的JSON
import json

try:
    data = json.loads(fixed_json_str)
    print("JSON解析成功")
    
    # 寻找视频数据
    if 'common' in data:
        common = data['common']
        print(f"common的键: {list(common.keys())}")
        
        if 'noteDetailMap' in common:
            note_detail_map = common['noteDetailMap']
            print(f"noteDetailMap的键: {list(note_detail_map.keys())}")
            
            # 遍历笔记
            for note_id, note_detail in note_detail_map.items():
                print(f"\n笔记ID: {note_id}")
                
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
                                    print(f"URL类型: {type(info['url'])}")
                                    
                                    # 如果是列表，取第一个
                                    if isinstance(info['url'], list):
                                        if info['url']:
                                            print(f"URL列表的第一个: {info['url'][0]}")

except json.JSONDecodeError as e:
    print(f"JSON解析失败: {e}")
    print(f"错误位置: {e.pos}")
    
    # 打印错误附近的内容
    error_start = max(0, e.pos - 100)
    error_end = min(len(fixed_json_str), e.pos + 100)
    print(f"错误附近的内容: ...{fixed_json_str[error_start:error_end]}...")