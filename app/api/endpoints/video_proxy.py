import asyncio
import httpx
from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse
import os
import tempfile
import aiofiles

from crawlers.hybrid.hybrid_crawler import HybridCrawler

router = APIRouter()
HybridCrawler = HybridCrawler()

@router.get("/video_proxy", summary="视频代理下载/Video Proxy Download")
async def video_proxy(
    request: Request,
    video_url: str = Query(...),
    platform: str = Query(...) ):
    """
    视频代理下载端点，避免浏览器直接访问第三方视频URL导致的跨域错误
    
    Parameters:
    - video_url: 原始视频URL
    - platform: 平台名称（用于获取正确的headers）
    """
    try:
        # 获取对应平台的headers
        if platform == 'tiktok':
            __headers = await HybridCrawler.TikTokWebCrawler.get_tiktok_headers()
        elif platform == 'bilibili':
            __headers = await HybridCrawler.BilibiliWebCrawler.get_bilibili_headers()
        elif platform == 'kuaishou':
            __headers = await HybridCrawler.KuaiShouWebCrawler.get_kuaishou_headers()
        elif platform == 'xiaohongshu':
            __headers = await HybridCrawler.XiaoHongShuWebCrawler.get_xiaohongshu_headers()
        elif platform == 'weibo':
            __headers = await HybridCrawler.get_weibo_headers()
        else:  # douyin
            __headers = await HybridCrawler.DouyinWebCrawler.get_douyin_headers()
        
        headers = __headers.get('headers', {})
        
        # B站视频特殊处理：音视频合并
        if platform == 'bilibili':
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.m4v', delete=False) as video_temp:
                video_temp_path = video_temp.name
            with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as audio_temp:
                audio_temp_path = audio_temp.name
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as output_temp:
                output_temp_path = output_temp.name
            
            try:
                # 下载视频流
                print(f"Downloading Bilibili video stream: {video_url}")
                async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                    async with client.stream("GET", video_url, headers=headers) as response:
                        response.raise_for_status()
                        async with aiofiles.open(video_temp_path, 'wb') as f:
                            async for chunk in response.aiter_bytes():
                                await f.write(chunk)
                
                # 检查视频文件是否下载成功
                if not os.path.exists(video_temp_path) or os.path.getsize(video_temp_path) == 0:
                    print("Video file download failed or empty")
                    # 如果视频下载失败，返回错误
                    raise HTTPException(
                        status_code=500,
                        detail="B站视频流下载失败"
                    )
                
                # 尝试获取音频URL
                audio_url = None
                try:
                    # 方法1: 从视频URL中提取信息，尝试获取对应的音频URL
                    print("Trying to get audio URL from video URL")
                    
                    # 分析视频URL，尝试获取BV号
                    bv_id = None
                    # 从视频URL中提取BV号
                    bv_pattern = r'(BV[A-Za-z0-9]+)'
                    bv_match = re.search(bv_pattern, video_url)
                    if bv_match:
                        bv_id = bv_match.group(1)
                        print(f"Extracted BV ID from video URL: {bv_id}")
                    
                    if bv_id:
                        # 获取视频详情，获取cid
                        video_detail = await HybridCrawler.BilibiliWebCrawler.fetch_one_video(bv_id)
                        cid = video_detail.get('data', {}).get('cid')
                        if cid:
                            print(f"Got CID for Bilibili video: {cid}")
                            # 获取播放链接
                            playurl_data = await HybridCrawler.BilibiliWebCrawler.fetch_video_playurl(bv_id, str(cid))
                            # 从播放数据中提取音频URL
                            dash = playurl_data.get('data', {}).get('dash', {})
                            audio_list = dash.get('audio', [])
                            # 按音频带宽从高到低排序
                            sorted_audio_list = sorted(audio_list, key=lambda x: x.get('bandwidth', 0), reverse=True) if audio_list else []
                            # 选择最高质量的音频
                            audio_url = sorted_audio_list[0].get('baseUrl') if sorted_audio_list else None
                            print(f"Got audio URL: {audio_url}")
                except Exception as e:
                    print(f"Failed to get audio URL: {e}")
                
                # 如果成功获取到音频URL，下载音频流
                if audio_url:
                    print(f"Downloading Bilibili audio stream: {audio_url}")
                    try:
                        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                            async with client.stream("GET", audio_url, headers=headers) as response:
                                response.raise_for_status()
                                async with aiofiles.open(audio_temp_path, 'wb') as f:
                                    async for chunk in response.aiter_bytes():
                                        await f.write(chunk)
                        
                        # 检查音频文件是否下载成功
                        if not os.path.exists(audio_temp_path) or os.path.getsize(audio_temp_path) == 0:
                            print("Audio file download failed or empty, returning video stream directly")
                            audio_url = None
                    except Exception as e:
                        print(f"Failed to download audio stream: {e}, returning video stream directly")
                        audio_url = None
                
                # 如果有音频URL，尝试合并
                if audio_url:
                    # 使用FFmpeg合并音视频
                    print("Merging video and audio with FFmpeg")
                    import subprocess
                    import shutil
                    import platform as sys_platform
                    
                    # 查找FFmpeg路径
                    ffmpeg_path = None
                    system = sys_platform.system()
                    
                    # 方法1: 尝试使用系统PATH中的ffmpeg
                    ffmpeg_path = shutil.which("ffmpeg")
                    if ffmpeg_path:
                        print(f"Found FFmpeg in PATH: {ffmpeg_path}")
                    
                    # 方法2: 尝试常见的Linux FFmpeg路径
                    if not ffmpeg_path and system == "Linux":
                        common_paths = [
                            "/usr/bin/ffmpeg",
                            "/usr/local/bin/ffmpeg",
                            "/bin/ffmpeg"
                        ]
                        for path in common_paths:
                            if os.path.exists(path):
                                ffmpeg_path = path
                                print(f"Found FFmpeg in common path: {ffmpeg_path}")
                                break
                    
                    # 方法3: Windows环境的常见路径
                    if not ffmpeg_path and system == "Windows":
                        common_paths = [
                            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                            r"C:\ffmpeg\bin\ffmpeg.exe"
                        ]
                        for path in common_paths:
                            if os.path.exists(path):
                                ffmpeg_path = path
                                print(f"Found FFmpeg in common path: {ffmpeg_path}")
                                break
                    
                    if ffmpeg_path and os.path.exists(ffmpeg_path):
                        ffmpeg_cmd = [
                            ffmpeg_path, '-y',  # -y 覆盖输出文件
                            '-i', video_temp_path,
                            '-i', audio_temp_path,
                            '-c:v', 'copy',  # 复制视频编码，不重新编码
                            '-c:a', 'copy',  # 复制音频编码，不重新编码
                            '-f', 'mp4',     # 确保输出格式为MP4
                            output_temp_path
                        ]
                        
                        print(f"Executing FFmpeg command: {' '.join(ffmpeg_cmd)}")
                        try:
                            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
                            print(f"FFmpeg return code: {result.returncode}")
                            if result.stdout:
                                print(f"FFmpeg stdout: {result.stdout}")
                            if result.stderr:
                                print(f"FFmpeg stderr: {result.stderr}")
                            
                            if result.returncode == 0 and os.path.exists(output_temp_path) and os.path.getsize(output_temp_path) > 0:
                                print(f"Successfully merged video and audio: {output_temp_path}")
                                # 返回合并后的视频
                                async def stream_merged_video():
                                    async with aiofiles.open(output_temp_path, 'rb') as f:
                                        chunk = await f.read(8192)
                                        while chunk:
                                            yield chunk
                                            chunk = await f.read(8192)
                                
                                return StreamingResponse(
                                    content=stream_merged_video(),
                                    media_type='video/mp4',
                                    headers={
                                        'Content-Disposition': f'attachment; filename="bilibili_video.mp4"'
                                    }
                                )
                            else:
                                print("FFmpeg merge failed, returning video stream directly")
                        except subprocess.TimeoutExpired:
                            print("FFmpeg command timed out, returning video stream directly")
                        except Exception as e:
                            print(f"FFmpeg execution error: {e}, returning video stream directly")
                    else:
                        print("FFmpeg not found, returning video stream directly")
                else:
                    print("Audio URL not found, returning video stream directly")
                
                # 如果合并失败或没有音频URL，返回原始视频流
                async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                    response = await client.get(video_url, headers=headers)
                    response.raise_for_status()
                    
                    async def stream_content():
                        yield response.content
                    
                    return StreamingResponse(
                        content=stream_content(),
                        media_type='video/mp4',
                        headers={
                            'Content-Disposition': f'attachment; filename="bilibili_video.mp4"',
                            'Content-Length': str(len(response.content))
                        }
                    )
                    
            finally:
                # 清理临时文件
                for path in [video_temp_path, audio_temp_path, output_temp_path]:
                    if os.path.exists(path):
                        try:
                            os.unlink(path)
                            print(f"Cleaned up temporary file: {path}")
                        except Exception as e:
                            print(f"Failed to clean up temporary file {path}: {e}")
        
        # 其他平台直接返回视频流
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            response = await client.get(video_url, headers=headers)
            response.raise_for_status()
            
            # 流式返回视频内容
            async def stream_content():
                yield response.content
            
            # 返回视频流
            return StreamingResponse(
                content=stream_content(),
                media_type='video/mp4',
                headers={
                    'Content-Disposition': f'attachment; filename="{platform}_video.mp4"',
                    'Content-Length': str(len(response.content))
                }
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"视频请求失败: {e.response.reason_phrase}"
        )
    except Exception as e:
        print(f"Video proxy error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"视频代理下载失败: {str(e)}"
        )