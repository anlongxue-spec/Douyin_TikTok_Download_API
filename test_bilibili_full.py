import asyncio
import os
import subprocess
import tempfile
import httpx
import aiofiles
from crawlers.hybrid.hybrid_crawler import HybridCrawler

async def fetch_data_stream(url: str, headers: dict = None, file_path: str = None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    } if headers is None else headers
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url, headers=headers) as response:
            response.raise_for_status()
            async with aiofiles.open(file_path, 'wb') as out_file:
                async for chunk in response.aiter_bytes():
                    await out_file.write(chunk)
            return True

async def merge_bilibili_video_audio_test(video_url: str, audio_url: str, headers: dict):
    """
    测试合并Bilibili视频和音频流的功能
    """
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.m4v', delete=False) as video_temp:
            video_temp_path = video_temp.name
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as audio_temp:
            audio_temp_path = audio_temp.name
        
        print(f"创建的临时文件:")
        print(f"视频临时文件: {video_temp_path}")
        print(f"音频临时文件: {audio_temp_path}")
        
        # 下载视频流
        print(f"\n开始下载视频流: {video_url}")
        try:
            video_success = await fetch_data_stream(video_url, headers=headers, file_path=video_temp_path)
            print(f"视频下载成功: {video_success}")
        except Exception as e:
            print(f"视频下载失败: {e}")
            return False
        
        # 下载音频流
        print(f"\n开始下载音频流: {audio_url}")
        try:
            audio_success = await fetch_data_stream(audio_url, headers=headers, file_path=audio_temp_path)
            print(f"音频下载成功: {audio_success}")
        except Exception as e:
            print(f"音频下载失败: {e}")
            return False
        
        if not video_success or not audio_success:
            print("下载失败")
            return False
        
        # 检查下载的文件大小
        video_size = os.path.getsize(video_temp_path) if os.path.exists(video_temp_path) else 0
        audio_size = os.path.getsize(audio_temp_path) if os.path.exists(audio_temp_path) else 0
        print(f"\n下载的文件大小:")
        print(f"视频文件大小: {video_size} 字节")
        print(f"音频文件大小: {audio_size} 字节")
        
        # 使用 FFmpeg 合并视频和音频
        output_path = tempfile.mktemp(suffix='.mp4')
        print(f"\n输出文件: {output_path}")
        
        # 测试FFmpeg路径
        ffmpeg_path = "C:\\Program Files (x86)\\iflyrecClient\\resources\\tj_B1\\node_modules\\@ffmpeg-installer\\win32-x64\\ffmpeg.exe"
        print(f"使用的FFmpeg路径: {ffmpeg_path}")
        print(f"FFmpeg是否存在: {os.path.exists(ffmpeg_path)}")
        
        ffmpeg_cmd = [
            ffmpeg_path, '-y',
            '-i', video_temp_path,
            '-i', audio_temp_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'mp4',
            output_path
        ]
        
        print(f"\n执行FFmpeg命令: {' '.join(ffmpeg_cmd)}")
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            print(f"FFmpeg返回码: {result.returncode}")
            if result.stdout:
                print(f"FFmpeg标准输出: {result.stdout}")
            if result.stderr:
                print(f"FFmpeg错误输出: {result.stderr}")
        except Exception as e:
            print(f"执行FFmpeg命令失败: {e}")
            return False
        
        # 检查输出文件
        if result.returncode == 0 and os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            print(f"\n合并成功！")
            print(f"输出文件大小: {output_size} 字节")
        else:
            print(f"\n合并失败！")
        
        # 清理临时文件
        try:
            if os.path.exists(video_temp_path):
                os.unlink(video_temp_path)
            if os.path.exists(audio_temp_path):
                os.unlink(audio_temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
            print(f"\n临时文件已清理")
        except Exception as e:
            print(f"清理临时文件失败: {e}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"发生错误: {e}")
        # 清理临时文件
        try:
            if 'video_temp_path' in locals() and os.path.exists(video_temp_path):
                os.unlink(video_temp_path)
            if 'audio_temp_path' in locals() and os.path.exists(audio_temp_path):
                os.unlink(audio_temp_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.unlink(output_path)
        except:
            pass
        return False

async def main():
    print("===== 测试Bilibili视频下载和合并功能 =====")
    
    # 测试1: 检查FFmpeg是否可用
    print("\n1. 检查FFmpeg是否可用:")
    ffmpeg_path = "C:\\Program Files (x86)\\iflyrecClient\\resources\\tj_B1\\node_modules\\@ffmpeg-installer\\win32-x64\\ffmpeg.exe"
    print(f"FFmpeg路径: {ffmpeg_path}")
    print(f"FFmpeg是否存在: {os.path.exists(ffmpeg_path)}")
    
    try:
        result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True)
        print(f"FFmpeg版本检查返回码: {result.returncode}")
        if result.returncode == 0:
            print(f"FFmpeg版本: {result.stdout.split()[2]}")
        else:
            print(f"FFmpeg版本检查失败: {result.stderr}")
    except Exception as e:
        print(f"执行FFmpeg版本检查失败: {e}")
    
    # 测试2: 解析Bilibili视频
    print("\n2. 解析Bilibili视频:")
    crawler = HybridCrawler()
    try:
        data = await crawler.hybrid_parsing_single_video('https://b23.tv/UzSQvAW', minimal=True)
        print(f"解析成功")
        print(f"平台: {data.get('platform')}")
        print(f"视频ID: {data.get('video_id')}")
        
        video_data = data.get('video_data', {})
        video_url = video_data.get('nwm_video_url_HQ')
        audio_url = video_data.get('audio_url')
        print(f"视频URL: {video_url}")
        print(f"音频URL: {audio_url}")
        
        if video_url and audio_url:
            # 测试3: 下载并合并视频和音频
            print("\n3. 下载并合并视频和音频:")
            
            # 获取Bilibili请求头
            bilibili_headers = await crawler.BilibiliWebCrawler.get_bilibili_headers()
            headers = bilibili_headers.get('headers', {})
            print(f"使用的请求头: {headers.keys()}")
            
            success = await merge_bilibili_video_audio_test(video_url, audio_url, headers)
            print(f"\n测试结果: {'成功' if success else '失败'}")
        else:
            print("无法获取视频或音频URL")
    except Exception as e:
        print(f"解析失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())