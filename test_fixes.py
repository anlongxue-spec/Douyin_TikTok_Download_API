import re
import platform
import subprocess
import os

def test_url_cleaning():
    """测试URL清理功能"""
    print("=== 测试URL清理功能 ===")
    
    test_urls = [
        "`https://b23.tv/UzSQvAW`",
        " 'https://b23.tv/UzSQvAW' ",
        '"https://b23.tv/UzSQvAW"',
        "https://b23.tv/UzSQvAW",
        " ` https://b23.tv/UzSQvAW ` "
    ]
    
    for url in test_urls:
        # 模拟修复后的URL清理逻辑
        cleaned_url = url.strip()  # 去除首尾空格
        cleaned_url = re.sub(r'[`\'\"]', '', cleaned_url)  # 去除所有反引号和引号
        cleaned_url = re.sub(r'\s+', ' ', cleaned_url)  # 多个空格替换为单个空格
        cleaned_url = cleaned_url.strip()  # 再次去除首尾空格
        
        print(f"原始URL: '{url}'")
        print(f"清理后URL: '{cleaned_url}'")
        has_backtick = '`' in cleaned_url
        has_single_quote = "'" in cleaned_url
        has_double_quote = '"' in cleaned_url
        print(f"是否包含反引号: {has_backtick}")
        print(f"是否包含单引号: {has_single_quote}")
        print(f"是否包含双引号: {has_double_quote}")
        print()

def test_ffmpeg_detection():
    """测试FFmpeg路径检测功能"""
    print("=== 测试FFmpeg路径检测功能 ===")
    
    system = platform.system()
    print(f"当前系统: {system}")
    
    # 方法1: 尝试使用系统命令查找
    print("方法1: 尝试使用系统命令查找FFmpeg")
    try:
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            print(f"在PATH中找到FFmpeg: {ffmpeg_path}")
        else:
            print("在PATH中未找到FFmpeg")
    except Exception as e:
        print(f"查找失败: {e}")
    
    # 方法2: 尝试硬编码路径
    print("\n方法2: 尝试硬编码路径")
    if system == "Windows":
        possible_paths = [
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\iflyrecClient\resources\tj_B1\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe"
        ]
    else:
        possible_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
            "/bin/ffmpeg",
            "/sbin/ffmpeg",
            "/usr/sbin/ffmpeg"
        ]
    
    found = False
    for path in possible_paths:
        if os.path.exists(path):
            print(f"在硬编码路径中找到FFmpeg: {path}")
            found = True
            break
    
    if not found:
        print("在硬编码路径中未找到FFmpeg")
    
    # 方法3: 尝试直接执行ffmpeg命令
    print("\n方法3: 尝试直接执行ffmpeg命令")
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("FFmpeg命令执行成功")
            # 避免f-string中的反斜杠问题
            version_line = result.stdout.split('\n')[0]
            print(f"FFmpeg版本: {version_line}")
        else:
            print(f"FFmpeg命令执行失败: {result.stderr}")
    except Exception as e:
        print(f"执行失败: {e}")

if __name__ == "__main__":
    test_url_cleaning()
    test_ffmpeg_detection()
