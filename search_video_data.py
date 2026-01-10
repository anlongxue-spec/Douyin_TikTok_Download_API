# 全面搜索视频数据
import json

# 读取修复后的JSON
with open('fixed_json.txt', 'r', encoding='utf-8') as f:
    fixed_json_str = f.read()

data = json.loads(fixed_json_str)

# 递归搜索视频数据
def search_video_data(obj, path=""):
    """递归搜索视频数据"""
    if isinstance(obj, dict):
        # 检查是否包含视频相关字段
        if 'video' in obj:
            print(f"\n在{path}找到video字段")
            video = obj['video']
            print(f"video的键: {list(video.keys())}")
            return True
        
        # 检查是否包含note相关字段
        if 'note' in obj:
            print(f"\n在{path}找到note字段")
            note = obj['note']
            print(f"note的键: {list(note.keys())}")
            if 'video' in note:
                print(f"在{path}.note找到video字段")
                video = note['video']
                print(f"video的键: {list(video.keys())}")
                
                # 寻找视频URL
                if 'media' in video:
                    media = video['media']
                    print(f"media的键: {list(media.keys())}")
                    
                    # 尝试各种可能的视频URL字段
                    possible_fields = ['stream', 'url', 'playUrl', 'play_url', 'main_url', 'video_url', 'urls']
                    for field in possible_fields:
                        if field in media:
                            video_url = media[field]
                            print(f"找到视频URL: {video_url}")
                            return True
                
                # 检查playInfos
                if 'playInfos' in video:
                    play_infos = video['playInfos']
                    print(f"playInfos长度: {len(play_infos)}")
                    for i, info in enumerate(play_infos):
                        print(f"playInfo[{i}]的键: {list(info.keys())}")
                        if 'url' in info:
                            print(f"找到playInfo URL: {info['url']}")
                            return True
        
        # 递归搜索所有键
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            if search_video_data(value, current_path):
                return True
    
    elif isinstance(obj, list):
        # 递归搜索列表中的所有元素
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            if search_video_data(item, current_path):
                return True
    
    return False

# 开始搜索
print("开始搜索视频数据...")
if not search_video_data(data):
    print("\n未找到视频数据")
    
    # 打印整个JSON的键结构
    print("\nJSON结构概览:")
    def print_structure(obj, indent=0, max_depth=2):
        if indent > max_depth:
            return
            
        if isinstance(obj, dict):
            for key, value in obj.items():
                print('  ' * indent + f"- {key}:")
                print_structure(value, indent + 1, max_depth)
        elif isinstance(obj, list):
            print('  ' * indent + f"- [列表，长度: {len(obj)}]")
            if obj:
                print_structure(obj[0], indent + 1, max_depth)
        else:
            print('  ' * indent + f"- {type(obj).__name__}: {str(obj)[:50]}...")
    
    print_structure(data)