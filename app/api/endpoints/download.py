import os
import zipfile
import subprocess
import tempfile

import aiofiles
import httpx
import yaml
from fastapi import APIRouter, Request, Query, HTTPException  # 导入FastAPI组件
from starlette.responses import FileResponse

from app.api.models.APIResponseModel import ErrorResponseModel  # 导入响应模型
from crawlers.hybrid.hybrid_crawler import HybridCrawler  # 导入混合数据爬虫

router = APIRouter()
HybridCrawler = HybridCrawler()

# 读取上级再上级目录的配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config.yaml')
print(f"Reading config from: {config_path}")
print(f"Config file exists: {os.path.exists(config_path)}")
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

async def fetch_data(url: str, headers: dict = None):
    # 处理headers参数，支持直接传递headers字典或包含headers键的字典
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    elif isinstance(headers, dict) and 'headers' in headers:
        headers = headers['headers']
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()  # 确保响应是成功的
        return response

# 下载视频专用
async def fetch_data_stream(url: str, request:Request , headers: dict = None, file_path: str = None):
    # 处理headers参数，支持直接传递headers字典或包含headers键的字典
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    elif isinstance(headers, dict) and 'headers' in headers:
        # 从包含headers键的字典中提取headers
        extracted_headers = headers['headers']
        if isinstance(extracted_headers, dict):
            headers = extracted_headers
            print(f"Extracted headers from dict: {list(headers.keys())}")
    
    # 设置超时和重试策略
    httpx_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),  # 总超时时间
        follow_redirects=True
    )
    
    async with httpx_client as client:
        try:
            # 启用流式请求
            async with client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()
                
                # 验证响应头
                if "content-length" in response.headers:
                    print(f"  Content-Length: {response.headers['content-length']} 字节")
                
                # 流式保存文件
                async with aiofiles.open(file_path, 'wb') as out_file:
                    total_bytes = 0
                    async for chunk in response.aiter_bytes():
                        if await request.is_disconnected():
                            print("客户端断开连接，清理未完成的文件")
                            await out_file.close()
                            os.remove(file_path)
                            return False
                        
                        # 检查chunk是否为空
                        if not chunk:
                            continue
                        
                        await out_file.write(chunk)
                        total_bytes += len(chunk)
                    
                    # 验证下载的文件大小
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"  实际下载大小: {file_size} 字节")
                        print(f"  预期下载大小: {total_bytes} 字节")
                        
                        # 允许一定的误差范围（4096字节），避免网络波动导致的小误差
                        if abs(file_size - total_bytes) > 4096:
                            print(f"  文件下载不完整，清理文件 (预期: {total_bytes} 字节, 实际: {file_size} 字节)")
                            try:
                                os.remove(file_path)
                            except PermissionError:
                                print("  无法删除文件，可能被其他程序占用")
                            return False
                        else:
                            print(f"  文件下载完整 (预期: {total_bytes} 字节, 实际: {file_size} 字节)")
                    
                    return True
        except httpx.TimeoutException:
            print(f"  请求超时: {url}")
            return False
        except httpx.HTTPStatusError as e:
            print(f"  HTTP错误: {e.response.status_code} - {e.response.reason_phrase}")
            return False
        except Exception as e:
            print(f"  下载失败: {e}")
            import traceback
            traceback.print_exc()
            return False

async def merge_bilibili_video_audio(video_url: str, audio_url: str, request: Request, output_path: str, headers: dict) -> bool:
    """
    下载并合并 Bilibili 的视频流和音频流
    """
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.m4v', delete=False) as video_temp:
            video_temp_path = video_temp.name
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as audio_temp:
            audio_temp_path = audio_temp.name
        
        print(f"Created temporary files:")
        print(f"Video temp path: {video_temp_path}")
        print(f"Audio temp path: {audio_temp_path}")
        
        # 清理视频和音频URL中的反引号和引号
        import re
        cleaned_video_url = video_url.strip()  # 去除首尾空格
        cleaned_video_url = re.sub(r"[`'\"]", '', cleaned_video_url)  # 去除所有反引号和引号
        cleaned_video_url = re.sub(r'\s+', ' ', cleaned_video_url)  # 多个空格替换为单个空格
        cleaned_video_url = cleaned_video_url.strip()  # 再次去除首尾空格
        # 确保完全移除反引号
        cleaned_video_url = cleaned_video_url.replace('`', '')
        
        cleaned_audio_url = audio_url.strip()  # 去除首尾空格
        cleaned_audio_url = re.sub(r"[`'\"]", '', cleaned_audio_url)  # 去除所有反引号和引号
        cleaned_audio_url = re.sub(r'\s+', ' ', cleaned_audio_url)  # 多个空格替换为单个空格
        cleaned_audio_url = cleaned_audio_url.strip()  # 再次去除首尾空格
        # 确保完全移除反引号
        cleaned_audio_url = cleaned_audio_url.replace('`', '')
        
        print(f"清理前视频URL: '{video_url}'")
        print(f"清理后视频URL: '{cleaned_video_url}'")
        print(f"清理前音频URL: '{audio_url}'")
        print(f"清理后音频URL: '{cleaned_audio_url}'")
        
        # 下载视频流（带重试机制）
        print(f"Downloading video stream from: {cleaned_video_url}")
        video_success = False
        max_retries = 3
        for attempt in range(max_retries):
            try:
                video_success = await fetch_data_stream(cleaned_video_url, request, headers=headers, file_path=video_temp_path)
                print(f"Video download attempt {attempt+1}/{max_retries} success: {video_success}")
                if video_success:
                    break
                print(f"Retrying video download... ({attempt+1}/{max_retries})")
            except Exception as e:
                print(f"Video download attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    return False
        
        # 下载音频流（带重试机制）
        print(f"Downloading audio stream from: {cleaned_audio_url}")
        audio_success = False
        for attempt in range(max_retries):
            try:
                audio_success = await fetch_data_stream(cleaned_audio_url, request, headers=headers, file_path=audio_temp_path)
                print(f"Audio download attempt {attempt+1}/{max_retries} success: {audio_success}")
                if audio_success:
                    break
                print(f"Retrying audio download... ({attempt+1}/{max_retries})")
            except Exception as e:
                print(f"Audio download attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    return False
        
        if not video_success or not audio_success:
            print("Failed to download video or audio stream after multiple attempts")
            return False
        
        # 检查下载的文件大小和存在性
        video_exists = os.path.exists(video_temp_path)
        audio_exists = os.path.exists(audio_temp_path)
        video_size = os.path.getsize(video_temp_path) if video_exists else 0
        audio_size = os.path.getsize(audio_temp_path) if audio_exists else 0
        print(f"Video file exists: {video_exists}, size: {video_size} bytes")
        print(f"Audio file exists: {audio_exists}, size: {audio_size} bytes")
        
        if not video_exists or video_size == 0:
            print("Video file is empty or doesn't exist")
            return False
        if not audio_exists or audio_size == 0:
            print("Audio file is empty or doesn't exist")
            return False
        
        # 使用微信云托管环境中已安装的ffmpeg工具
        try:
            import platform
            import shutil
            system = platform.system()
            ffmpeg_path = None
            
            print(f"Current system: {system}")
            
            # 方法1: 尝试使用系统PATH中的ffmpeg
            print("Method 1: Trying to find FFmpeg in system PATH")
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                print(f"Found FFmpeg in PATH: {ffmpeg_path}")
            
            # 方法2: 直接执行which命令查找ffmpeg
            if not ffmpeg_path:
                print("Method 2: Trying to execute 'which ffmpeg' command")
                try:
                    result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        ffmpeg_path = result.stdout.strip()
                        print(f"Found FFmpeg via 'which' command: {ffmpeg_path}")
                except Exception as e:
                    print(f"'which ffmpeg' command failed: {e}")
            
            # 方法3: 尝试直接执行ffmpeg命令验证
            if not ffmpeg_path:
                print("Method 3: Trying to execute 'ffmpeg' command directly")
                try:
                    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        # 如果命令执行成功，说明ffmpeg在PATH中
                        ffmpeg_path = "ffmpeg"
                        print(f"Found FFmpeg by direct execution")
                except Exception as e:
                    print(f"Direct execution failed: {e}")
            
            # 方法4: 如果PATH中没有，尝试常见的Linux FFmpeg路径
            if not ffmpeg_path and system == "Linux":
                print("Method 4: Trying common Linux FFmpeg paths")
                common_paths = [
                    "/usr/bin/ffmpeg",
                    "/usr/local/bin/ffmpeg",
                    "/bin/ffmpeg",
                    "/sbin/ffmpeg",
                    "/usr/sbin/ffmpeg",
                    "/usr/local/ffmpeg/bin/ffmpeg",
                    "/opt/ffmpeg/bin/ffmpeg",
                    "/usr/ffmpeg/bin/ffmpeg"
                ]
                for path in common_paths:
                    if os.path.exists(path):
                        ffmpeg_path = path
                        print(f"Found FFmpeg in common path: {ffmpeg_path}")
                        break
            
            # 方法5: Windows环境的常见路径
            if not ffmpeg_path and system == "Windows":
                print("Method 5: Trying common Windows FFmpeg paths")
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
            
            # 验证FFmpeg路径
            if not ffmpeg_path:
                print("ERROR: FFmpeg path not found in any location")
                print("Please ensure FFmpeg is installed in the environment")
                print("Cannot merge video and audio without FFmpeg")
                print("Video will have no sound")
                # 清理临时文件
                try:
                    if os.path.exists(video_temp_path):
                        os.unlink(video_temp_path)
                    if os.path.exists(audio_temp_path):
                        os.unlink(audio_temp_path)
                    print("Temporary files cleaned up")
                except Exception as e:
                    print(f"Failed to clean up temporary files: {e}")
                return False
            
            # 验证FFmpeg路径是否存在
            if not os.path.exists(ffmpeg_path):
                print(f"ERROR: FFmpeg path does not exist: {ffmpeg_path}")
                print("Cannot merge video and audio without FFmpeg")
                print("Video will have no sound")
                # 清理临时文件
                try:
                    if os.path.exists(video_temp_path):
                        os.unlink(video_temp_path)
                    if os.path.exists(audio_temp_path):
                        os.unlink(audio_temp_path)
                    print("Temporary files cleaned up")
                except Exception as e:
                    print(f"Failed to clean up temporary files: {e}")
                return False
            
            # 验证FFmpeg是否为文件
            if not os.path.isfile(ffmpeg_path):
                print(f"ERROR: FFmpeg path is not a file: {ffmpeg_path}")
                print("Cannot merge video and audio without FFmpeg")
                print("Video will have no sound")
                # 清理临时文件
                try:
                    if os.path.exists(video_temp_path):
                        os.unlink(video_temp_path)
                    if os.path.exists(audio_temp_path):
                        os.unlink(audio_temp_path)
                    print("Temporary files cleaned up")
                except Exception as e:
                    print(f"Failed to clean up temporary files: {e}")
                return False
            
            # 验证FFmpeg是否有可执行权限
            if not os.access(ffmpeg_path, os.X_OK):
                print(f"ERROR: FFmpeg does not have executable permissions: {ffmpeg_path}")
                print("Cannot merge video and audio without FFmpeg")
                print("Video will have no sound")
                # 清理临时文件
                try:
                    if os.path.exists(video_temp_path):
                        os.unlink(video_temp_path)
                    if os.path.exists(audio_temp_path):
                        os.unlink(audio_temp_path)
                    print("Temporary files cleaned up")
                except Exception as e:
                    print(f"Failed to clean up temporary files: {e}")
                return False
            
            # 验证FFmpeg是否可以正常执行
            try:
                result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    print(f"ERROR: FFmpeg execution failed: {result.stderr}")
                    print("Trying to return video stream directly without FFmpeg")
                    # 复制视频流到输出路径
                    import shutil
                    shutil.copy2(video_temp_path, output_path)
                    print(f"Copied video stream directly to: {output_path}")
                    # 清理临时文件
                    try:
                        if os.path.exists(video_temp_path):
                            os.unlink(video_temp_path)
                        if os.path.exists(audio_temp_path):
                            os.unlink(audio_temp_path)
                        print("Temporary files cleaned up")
                    except Exception as e:
                        print(f"Failed to clean up temporary files: {e}")
                    return True
                # 提取版本信息，避免在f-string中使用反斜杠
                version_line = result.stdout.split('\n')[0]
                print(f"Verified FFmpeg works correctly: {version_line}")
            except Exception as e:
                print(f"ERROR: Failed to verify FFmpeg execution: {e}")
                print("Trying to return video stream directly without FFmpeg")
                # 复制视频流到输出路径
                import shutil
                shutil.copy2(video_temp_path, output_path)
                print(f"Copied video stream directly to: {output_path}")
                # 清理临时文件
                try:
                    if os.path.exists(video_temp_path):
                        os.unlink(video_temp_path)
                    if os.path.exists(audio_temp_path):
                        os.unlink(audio_temp_path)
                    print("Temporary files cleaned up")
                except Exception as e:
                    print(f"Failed to clean up temporary files: {e}")
                return True
            
            print(f"Final FFmpeg path: {ffmpeg_path}")
            
        except Exception as e:
            print(f"ERROR: Failed to determine FFmpeg path: {e}")
            import traceback
            traceback.print_exc()
            # 在异常情况下，尝试直接返回视频流
            print("Trying to return video stream directly without FFmpeg due to exception")
            try:
                if 'video_temp_path' in locals() and os.path.exists(video_temp_path):
                    import shutil
                    shutil.copy2(video_temp_path, output_path)
                    print(f"Copied video stream directly to: {output_path}")
                    # 清理临时文件
                    if 'audio_temp_path' in locals() and os.path.exists(audio_temp_path):
                        os.unlink(audio_temp_path)
                    os.unlink(video_temp_path)
                    print("Temporary files cleaned up")
                    return True
            except Exception as cleanup_error:
                print(f"Failed to clean up temporary files: {cleanup_error}")
            return False
        
        # 使用 FFmpeg 合并视频和音频
        ffmpeg_cmd = [
            ffmpeg_path, '-y',  # -y 覆盖输出文件
            '-i', video_temp_path,  # 视频输入
            '-i', audio_temp_path,  # 音频输入
            '-c:v', 'copy',  # 复制视频编码，不重新编码
            '-c:a', 'copy',  # 复制音频编码，不重新编码（保持原始质量）
            '-f', 'mp4',     # 确保输出格式为MP4
            output_path
        ]
        
        print(f"Executing FFmpeg command: {' '.join(ffmpeg_cmd)}")
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            print(f"FFmpeg return code: {result.returncode}")
            if result.stdout:
                print(f"FFmpeg stdout: {result.stdout}")
            if result.stderr:
                print(f"FFmpeg stderr: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("FFmpeg command timed out")
            return False
        except Exception as e:
            print(f"Failed to execute FFmpeg command: {e}")
            return False
        
        # 检查输出文件
        output_exists = os.path.exists(output_path)
        output_size = os.path.getsize(output_path) if output_exists else 0
        print(f"Output file exists: {output_exists}, size: {output_size} bytes")
        
        # 清理临时文件
        try:
            if os.path.exists(video_temp_path):
                os.unlink(video_temp_path)
            if os.path.exists(audio_temp_path):
                os.unlink(audio_temp_path)
            print("Temporary files cleaned up")
        except Exception as e:
            print(f"Failed to clean up temporary files: {e}")
        
        return result.returncode == 0 and output_exists and output_size > 0
        
    except Exception as e:
        # 清理临时文件
        try:
            if 'video_temp_path' in locals() and os.path.exists(video_temp_path):
                os.unlink(video_temp_path)
            if 'audio_temp_path' in locals() and os.path.exists(audio_temp_path):
                os.unlink(audio_temp_path)
            print("Temporary files cleaned up in exception handler")
        except:
            pass
        print(f"Error merging video and audio: {e}")
        import traceback
        traceback.print_exc()
        return False

@router.get("/download", summary="在线下载抖音|TikTok|Bilibili视频/图片/Online download Douyin|TikTok|Bilibili video/image")
async def download_file_hybrid(request: Request,
                               url: str = Query(
                                   example="https://www.douyin.com/video/7372484719365098803",
                                   description="视频或图片的URL地址，支持抖音|TikTok|Bilibili的分享链接，例如：https://v.douyin.com/e4J8Q7A/ 或 https://www.bilibili.com/video/BV1xxxxxxxxx"),
                               prefix: bool = True,
                               with_watermark: bool = False):
    """
    # [中文]
    ### 用途:
    - 在线下载抖音|TikTok|Bilibili 无水印或有水印的视频/图片
    - 通过传入的视频URL参数，获取对应的视频或图片数据，然后下载到本地。
    - 如果你在尝试直接访问TikTok单一视频接口的JSON数据中的视频播放地址时遇到HTTP403错误，那么你可以使用此接口来下载视频。
    - Bilibili视频会自动合并视频流和音频流，确保下载的视频有声音。
    - 这个接口会占用一定的服务器资源，所以在Demo站点是默认关闭的，你可以在本地部署后调用此接口。
    ### 参数:
    - url: 视频或图片的URL地址，支持抖音|TikTok|Bilibili的分享链接，例如：https://v.douyin.com/e4J8Q7A/ 或 https://www.bilibili.com/video/BV1xxxxxxxxx
    - prefix: 下载文件的前缀，默认为True，可以在配置文件中修改。
    - with_watermark: 是否下载带水印的视频或图片，默认为False。(注意：Bilibili没有水印概念)
    ### 返回:
    - 返回下载的视频或图片文件响应。

    # [English]
    ### Purpose:
    - Download Douyin|TikTok|Bilibili video/image with or without watermark online.
    - By passing the video URL parameter, get the corresponding video or image data, and then download it to the local.
    - If you encounter an HTTP403 error when trying to access the video playback address in the JSON data of the TikTok single video interface directly, you can use this interface to download the video.
    - Bilibili videos will automatically merge video and audio streams to ensure downloaded videos have sound.
    - This interface will occupy a certain amount of server resources, so it is disabled by default on the Demo site, you can call this interface after deploying it locally.
    ### Parameters:
    - url: The URL address of the video or image, supports Douyin|TikTok|Bilibili sharing links, for example: https://v.douyin.com/e4J8Q7A/ or https://www.bilibili.com/video/BV1xxxxxxxxx
    - prefix: The prefix of the downloaded file, the default is True, and can be modified in the configuration file.
    - with_watermark: Whether to download videos or images with watermarks, the default is False. (Note: Bilibili has no watermark concept)
    ### Returns:
    - Return the response of the downloaded video or image file.

    # [示例/Example]
    url: https://www.bilibili.com/video/BV1U5efz2Egn
    """
    # 是否开启此端点/Whether to enable this endpoint
    if not config["API"]["Download_Switch"]:
        code = 400
        message = "Download endpoint is disabled in the configuration file. | 配置文件中已禁用下载端点。"
        return ErrorResponseModel(code=code, message=message, router=request.url.path,
                                  params=dict(request.query_params))

    # 开始解析数据/Start parsing data
    try:
        # 清理URL，去除多余的空格和反引号
        import re
        cleaned_url = url.strip()  # 去除首尾空格
        cleaned_url = re.sub(r"[`'\"]", '', cleaned_url)  # 去除所有反引号和引号
        cleaned_url = re.sub(r'\s+', ' ', cleaned_url)  # 多个空格替换为单个空格
        cleaned_url = cleaned_url.strip()  # 再次去除首尾空格
        print(f"清理前URL: '{url}'")
        print(f"清理后URL: '{cleaned_url}'")
        
        data = await HybridCrawler.hybrid_parsing_single_video(cleaned_url, minimal=True)
    except Exception as e:
        code = 400
        return ErrorResponseModel(code=code, message=str(e), router=request.url.path, params=dict(request.query_params))

    # 开始下载文件/Start downloading files
    try:
        data_type = data.get('type')
        platform = data.get('platform')
        video_id = data.get('video_id')  # 改为使用video_id
        file_prefix = config.get("API").get("Download_File_Prefix") if prefix else ''
        download_path = os.path.join(config.get("API").get("Download_Path"), f"{platform}_{data_type}")

        # 确保目录存在/Ensure the directory exists
        os.makedirs(download_path, exist_ok=True)

        # 下载视频文件/Download video file
        if data_type == 'video':
            file_name = f"{file_prefix}{platform}_{video_id}.mp4" if not with_watermark else f"{file_prefix}{platform}_{video_id}_watermark.mp4"
            file_path = os.path.join(download_path, file_name)

            # 判断文件是否存在，存在就直接返回
            if os.path.exists(file_path):
                return FileResponse(path=file_path, media_type='video/mp4', filename=file_name)

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

            # 获取视频数据
            video_data = data.get('video_data', {})
            
            # Bilibili 特殊处理：音视频分离
            if platform == 'bilibili':
                print(f"Debug: Processing Bilibili video with data: {data}")
                print(f"Debug: Video data: {video_data}")
                video_url = video_data.get('nwm_video_url_HQ') if not with_watermark else video_data.get('wm_video_url_HQ')
                audio_url = video_data.get('audio_url')
                print(f"Debug: Bilibili video URL (no watermark): {video_url}")
                print(f"Debug: Bilibili audio URL: {audio_url}")
                if not video_url:
                    print(f"Debug: nwm_video_url_HQ not found, trying nwm_video_url")
                    video_url = video_data.get('nwm_video_url') if not with_watermark else video_data.get('wm_video_url')
                    print(f"Debug: Using fallback video URL: {video_url}")
                if not audio_url:
                    print(f"Debug: audio_url not found in video_data")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to get audio URL from Bilibili"
                    )
                if not video_url:
                    print(f"Debug: video_url still not found after fallback")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to get video URL from Bilibili"
                    )
                
                # 使用专门的函数合并音视频
                print(f"Debug: Calling merge_bilibili_video_audio with video_url: {video_url}, audio_url: {audio_url}")
                print(f"Debug: Using headers: {__headers.get('headers')}")
                print(f"Debug: Output path: {file_path}")
                print(f"Debug: FFmpeg path from config: {config.get('API').get('FFmpeg_Path')}")
                try:
                    success = await merge_bilibili_video_audio(video_url, audio_url, request, file_path, __headers.get('headers'))
                    print(f"Debug: merge_bilibili_video_audio returned: {success}")
                except Exception as e:
                    print(f"Debug: Exception in merge_bilibili_video_audio: {e}")
                    import traceback
                    traceback.print_exc()
                    success = False
                if not success:
                    print(f"Debug: Raising HTTPException because merge failed")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to merge Bilibili video and audio streams"
                    )
            # 其他平台的常规处理
            else:
                # 获取视频URL
                url = video_data.get('nwm_video_url_HQ') if not with_watermark else video_data.get('wm_video_url_HQ')
                # 再次检查URL是否为None
                if not url:
                    url = video_data.get('nwm_video_url') if not with_watermark else video_data.get('wm_video_url')
                    
                if not url:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Failed to get video URL from {platform}"
                    )
                    
                # 下载视频
                success = await fetch_data_stream(url, request, headers=__headers, file_path=file_path)
                if not success:
                    raise HTTPException(
                        status_code=500,
                        detail="An error occurred while fetching data"
                    )

            # # 保存文件
            # async with aiofiles.open(file_path, 'wb') as out_file:
            #     await out_file.write(response.content)

            # 返回文件内容
            return FileResponse(path=file_path, filename=file_name, media_type="video/mp4")

        # 下载图片文件/Download image file
        elif data_type == 'image':
            # 压缩文件属性/Compress file properties
            zip_file_name = f"{file_prefix}{platform}_{video_id}_images.zip" if not with_watermark else f"{file_prefix}{platform}_{video_id}_images_watermark.zip"
            zip_file_path = os.path.join(download_path, zip_file_name)

            # 判断文件是否存在，存在就直接返回、
            if os.path.exists(zip_file_path):
                return FileResponse(path=zip_file_path, filename=zip_file_name, media_type="application/zip")

            # 获取图片文件/Get image file
            urls = data.get('image_data').get('no_watermark_image_list') if not with_watermark else data.get(
                'image_data').get('watermark_image_list')
            image_file_list = []
            for url in urls:
                # 请求图片文件/Request image file
                response = await fetch_data(url)
                index = int(urls.index(url))
                content_type = response.headers.get('content-type')
                file_format = content_type.split('/')[1]
                file_name = f"{file_prefix}{platform}_{video_id}_{index + 1}.{file_format}" if not with_watermark else f"{file_prefix}{platform}_{video_id}_{index + 1}_watermark.{file_format}"
                file_path = os.path.join(download_path, file_name)
                image_file_list.append(file_path)

                # 保存文件/Save file
                async with aiofiles.open(file_path, 'wb') as out_file:
                    await out_file.write(response.content)

            # 压缩文件/Compress file
            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                for image_file in image_file_list:
                    zip_file.write(image_file, os.path.basename(image_file))

            # 返回压缩文件/Return compressed file
            return FileResponse(path=zip_file_path, filename=zip_file_name, media_type="application/zip")

    # 异常处理/Exception handling
    except Exception as e:
        print(e)
        code = 400
        return ErrorResponseModel(code=code, message=str(e), router=request.url.path, params=dict(request.query_params))
