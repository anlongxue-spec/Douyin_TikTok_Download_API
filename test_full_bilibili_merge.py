import asyncio
import os
import tempfile
import httpx
import aiofiles
import subprocess
import yaml

# 读取配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

async def fetch_data_stream(url: str, headers: dict = None, file_path: str = None):
    headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print(f"Downloading from: {url}")
    print(f"Saving to: {file_path}")
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()
                async with aiofiles.open(file_path, 'wb') as out_file:
                    total_bytes = 0
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await out_file.write(chunk)
                        total_bytes += len(chunk)
                print(f"Download completed, total bytes: {total_bytes}")
                return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False

def merge_video_audio(video_path: str, audio_path: str, output_path: str, ffmpeg_path: str):
    print(f"Merging video: {video_path}")
    print(f"With audio: {audio_path}")
    print(f"Output to: {output_path}")
    print(f"Using FFmpeg: {ffmpeg_path}")
    
    cmd = [
        ffmpeg_path, '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-f', 'mp4',
        output_path
    ]
    
    print(f"Executing command: {' '.join(cmd)}")
    
    try:
        # 使用shell=True可能有助于解决路径中的空格问题
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=False)
        print(f"Command return code: {result.returncode}")
        
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        if result.returncode == 0:
            if os.path.exists(output_path):
                print(f"Merge successful! Output file size: {os.path.getsize(output_path)} bytes")
                return True
            else:
                print(f"ERROR: Command succeeded but output file not found")
                return False
        else:
            print(f"ERROR: Command failed with return code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print(f"ERROR: Command timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"ERROR: Exception while running command: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=== Full Bilibili Merge Test ===")
    
    # 视频和音频URL（从之前的测试中获取）
    video_url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/07/99/35182479907/35182479907-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&oi=1928713262&og=ali&uipk=5&trid=0f78399e98994e8a9d233857a9f7564u&deadline=1768115208&gen=playurlv3&os=estgoss&nbs=1&platform=pc&mid=1563114089&upsig=4df7daa0275c635b6d809d031956a36e&uparams=e,oi,og,uipk,trid,deadline,gen,os,nbs,platform,mid&bvc=vod&nettype=0&bw=926070&buvid=439EB233-5D03-3E32-702A-5CB95A60614A57594infoc&build=0&dl=0&f=u_0_0&qn_dyeid=c6f18e9a5b046fd90051480a69632fe8&agrr=0&orderid=0,3"
    audio_url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/07/99/35182479907/35182479907-1-30232.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&mid=1563114089&uipk=5&platform=pc&trid=8f29b870b0ca4c00a517511f51ebc32u&deadline=1768115230&nbs=1&gen=playurlv3&os=estgoss&oi=1928713262&og=ali&upsig=d884046ddaa7ef707b0c9fba89625b46&uparams=e,mid,uipk,platform,trid,deadline,nbs,gen,os,oi,og&bvc=vod&nettype=0&bw=89018&buvid=439EB233-5D03-3E32-702A-5CB95A60614A57594infoc&build=0&dl=0&f=u_0_0&qn_dyeid=452e4d878c18be0c00188edf69632ffe&agrr=0&orderid=0,3"
    
    # 请求头（模拟应用程序使用的头）
    headers = {
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'origin': 'https://www.bilibili.com',
        'referer': 'https://space.bilibili.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    
    # 获取FFmpeg路径
    ffmpeg_path = config.get('API').get('FFmpeg_Path')
    if not ffmpeg_path or not os.path.exists(ffmpeg_path):
        ffmpeg_path = r"C:\Program Files (x86)\iflyrecClient\resources\tj_B1\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
    
    print(f"Using FFmpeg path: {ffmpeg_path}")
    
    # 创建临时文件
    try:
        with tempfile.NamedTemporaryFile(suffix='.m4v', delete=False) as video_temp:
            video_path = video_temp.name
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as audio_temp:
            audio_path = audio_temp.name
        
        output_path = tempfile.mktemp(suffix='.mp4')
        
        print(f"\nCreated temporary files:")
        print(f"Video: {video_path}")
        print(f"Audio: {audio_path}")
        print(f"Output: {output_path}")
        
        # 下载视频
        print(f"\nStep 1: Downloading video...")
        video_ok = await fetch_data_stream(video_url, headers=headers, file_path=video_path)
        if not video_ok:
            print("ERROR: Video download failed")
            return
        
        # 下载音频
        print(f"\nStep 2: Downloading audio...")
        audio_ok = await fetch_data_stream(audio_url, headers=headers, file_path=audio_path)
        if not audio_ok:
            print("ERROR: Audio download failed")
            return
        
        # 验证下载的文件
        print(f"\nStep 3: Verifying downloaded files...")
        if not os.path.exists(video_path):
            print(f"ERROR: Video file not found: {video_path}")
            return
        if not os.path.exists(audio_path):
            print(f"ERROR: Audio file not found: {audio_path}")
            return
            
        video_size = os.path.getsize(video_path)
        audio_size = os.path.getsize(audio_path)
        
        print(f"Video file size: {video_size} bytes")
        print(f"Audio file size: {audio_size} bytes")
        
        if video_size == 0:
            print("ERROR: Video file is empty")
            return
        if audio_size == 0:
            print("ERROR: Audio file is empty")
            return
        
        # 合并视频和音频
        print(f"\nStep 4: Merging video and audio...")
        merge_ok = merge_video_audio(video_path, audio_path, output_path, ffmpeg_path)
        if merge_ok:
            print(f"\nSUCCESS: Merge completed successfully!")
            print(f"Output file: {output_path}")
        else:
            print(f"\nERROR: Merge failed")
            
    finally:
        # 清理临时文件
        print(f"\nStep 5: Cleaning up temporary files...")
        for path in [video_path, audio_path, output_path]:
            try:
                if path and os.path.exists(path):
                    os.unlink(path)
                    print(f"Deleted: {path}")
            except Exception as e:
                print(f"Failed to delete {path}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
