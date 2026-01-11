import asyncio
import os
import subprocess
import tempfile
import httpx
import yaml
from crawlers.hybrid.hybrid_crawler import HybridCrawler

# 读取配置文件
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# 获取FFmpeg路径
FFMPEG_PATH = config.get("API", {}).get("FFmpeg_Path", "ffmpeg")

async def test_ffmpeg():
    """测试FFmpeg是否正常工作"""
    print("=== 测试FFmpeg ===")
    try:
        result = subprocess.run([FFMPEG_PATH, "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            print(f"版本信息: {result.stdout.split()[2]}")
            return True
        else:
            print("❌ FFmpeg未安装或无法访问")
            print(f"错误信息: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg未找到，请安装FFmpeg")
        return False

async def test_bilibili_video_parse():
    """测试Bilibili视频解析"""
    print("\n=== 测试Bilibili视频解析 ===")
    url = "https://b23.tv/UzSQvAW"
    
    try:
        crawler = HybridCrawler()
        data = await crawler.hybrid_parsing_single_video(url, minimal=True)
        
        print(f"✅ 视频解析成功")
        print(f"平台: {data.get('platform')}")
        print(f"视频ID: {data.get('video_id')}")
        print(f"视频标题: {data.get('desc')}")
        
        video_data = data.get('video_data', {})
        if video_data:
            print(f"视频URL: {video_data.get('nwm_video_url_HQ')}")
            print(f"音频URL: {video_data.get('audio_url')}")
            return video_data
        else:
            print("❌ 未找到视频数据")
            return None
    except Exception as e:
        print(f"❌ 视频解析失败: {e}")
        return None

async def test_video_download(video_url, audio_url, headers):
    """测试视频和音频下载"""
    print("\n=== 测试视频和音频下载 ===")
    
    async def download_url(url, filename):
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 下载成功: {filename}")
                print(f"文件大小: {os.path.getsize(filename)} 字节")
                return True
        except Exception as e:
            print(f"❌ 下载失败 {filename}: {e}")
            return False
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_temp:
        video_path = video_temp.name
    with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as audio_temp:
        audio_path = audio_temp.name
    
    try:
        # 下载视频和音频
        video_success = await download_url(video_url, video_path)
        audio_success = await download_url(audio_url, audio_path)
        
        return video_success, audio_success, video_path, audio_path
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False, False, None, None

async def test_merge(video_path, audio_path, output_path):
    """测试视频和音频合并"""
    print("\n=== 测试视频合并 ===")
    try:
        ffmpeg_cmd = [
            FFMPEG_PATH, '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'mp4',
            output_path
        ]
        
        print(f"执行命令: {' '.join(ffmpeg_cmd)}")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 合并成功")
            print(f"输出文件: {output_path}")
            print(f"文件大小: {os.path.getsize(output_path)} 字节")
            return True
        else:
            print(f"❌ 合并失败")
            print(f"返回码: {result.returncode}")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 合并过程出错: {e}")
        return False

async def main():
    # 测试FFmpeg
    if not await test_ffmpeg():
        return
    
    # 解析Bilibili视频
    video_data = await test_bilibili_video_parse()
    if not video_data:
        return
    
    video_url = video_data.get('nwm_video_url_HQ')
    audio_url = video_data.get('audio_url')
    
    if not video_url or not audio_url:
        print("❌ 缺少视频或音频URL")
        return
    
    # 获取Bilibili请求头
    crawler = HybridCrawler()
    bilibili_headers = await crawler.BilibiliWebCrawler.get_bilibili_headers()
    headers = bilibili_headers.get('headers', {})
    
    # 测试下载
    video_success, audio_success, video_path, audio_path = await test_video_download(video_url, audio_url, headers)
    
    if video_success and audio_success:
        # 测试合并
        output_path = tempfile.mktemp(suffix='.mp4')
        merge_success = await test_merge(video_path, audio_path, output_path)
        
        # 清理文件
        os.unlink(video_path)
        os.unlink(audio_path)
        if merge_success and os.path.exists(output_path):
            os.unlink(output_path)
    else:
        # 清理文件
        if video_path and os.path.exists(video_path):
            os.unlink(video_path)
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)

if __name__ == "__main__":
    asyncio.run(main())