import os
import subprocess
import yaml

# 读取配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# 获取FFmpeg路径
ffmpeg_path = config.get('API').get('FFmpeg_Path')
print(f"FFmpeg path from config: {ffmpeg_path}")
print(f"FFmpeg exists: {os.path.exists(ffmpeg_path)}")
print(f"FFmpeg is file: {os.path.isfile(ffmpeg_path)}")

# 测试FFmpeg命令
if os.path.exists(ffmpeg_path):
    try:
        result = subprocess.run([ffmpeg_path, '-version'], capture_output=True, text=True, timeout=10)
        print(f"FFmpeg version command return code: {result.returncode}")
        if result.returncode == 0:
            print(f"FFmpeg version info: {result.stdout[:100]}...")
        else:
            print(f"FFmpeg version command failed: {result.stderr}")
    except Exception as e:
        print(f"Error running FFmpeg: {e}")
else:
    print("FFmpeg path is invalid")

# 测试另一种FFmpeg路径格式
manual_ffmpeg_path = r"C:\Program Files (x86)\iflyrecClient\resources\tj_B1\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
print(f"\nManual FFmpeg path: {manual_ffmpeg_path}")
print(f"Manual path exists: {os.path.exists(manual_ffmpeg_path)}")
