import asyncio
import os
import tempfile
import httpx
import aiofiles
import subprocess
from crawlers.hybrid.hybrid_crawler import HybridCrawler

async def fetch_data_stream(url: str, headers: dict = None, file_path: str = None):
    headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url, headers=headers) as response:
            response.raise_for_status()
            async with aiofiles.open(file_path, 'wb') as out_file:
                async for chunk in response.aiter_bytes():
                    await out_file.write(chunk)
            return True

async def merge_bilibili_test(video_url: str, audio_url: str, headers: dict):
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.m4v', delete=False) as video_temp:
            video_temp_path = video_temp.name
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as audio_temp:
            audio_temp_path = audio_temp.name
        
        print(f"Created temp files:")
        print(f"Video: {video_temp_path}")
        print(f"Audio: {audio_temp_path}")
        
        # 下载视频
        print(f"Downloading video from: {video_url}")
        await fetch_data_stream(video_url, headers=headers, file_path=video_temp_path)
        print(f"Video size: {os.path.getsize(video_temp_path)} bytes")
        
        # 下载音频
        print(f"Downloading audio from: {audio_url}")
        await fetch_data_stream(audio_url, headers=headers, file_path=audio_temp_path)
        print(f"Audio size: {os.path.getsize(audio_temp_path)} bytes")
        
        # 合并
        output_path = tempfile.mktemp(suffix='.mp4')
        ffmpeg_path = "C:\Program Files (x86)\iflyrecClient\resources\tj_B1\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
        
        print(f"Merging with FFmpeg at: {ffmpeg_path}")
        cmd = [
            ffmpeg_path, '-y',
            '-i', video_temp_path,
            '-i', audio_temp_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'mp4',
            output_path
        ]
        
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        # 检查结果
        if os.path.exists(output_path):
            print(f"Success! Output: {output_path}, size: {os.path.getsize(output_path)} bytes")
        else:
            print("Failed! Output file not created")
            
    finally:
        # 清理
        for path in [video_temp_path, audio_temp_path, output_path]:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except:
                pass

async def main():
    print("=== Testing Bilibili Video Merge Directly ===")
    
    # 解析视频
    crawler = HybridCrawler()
    url = "https://b23.tv/UzSQvAW"
    
    print(f"Parsing video: {url}")
    data = await crawler.hybrid_parsing_single_video(url, minimal=True)
    print(f"Parsed data: {data}")
    
    # 获取视频和音频URL
    video_data = data.get('video_data', {})
    video_url = video_data.get('nwm_video_url_HQ')
    audio_url = video_data.get('audio_url')
    
    print(f"Video URL: {video_url}")
    print(f"Audio URL: {audio_url}")
    
    if not video_url or not audio_url:
        print("Missing video or audio URL")
        return
    
    # 获取headers
    headers = await crawler.BilibiliWebCrawler.get_bilibili_headers()
    headers_dict = headers.get('headers', {})
    print(f"Headers: {headers_dict}")
    
    # 测试合并
    await merge_bilibili_test(video_url, audio_url, headers_dict)

if __name__ == "__main__":
    asyncio.run(main())
