import asyncio
import httpx
from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse
import os
import tempfile
import aiofiles
import re

from crawlers.hybrid.hybrid_crawler import HybridCrawler

# 导入现有的合并函数
from app.api.endpoints.download import merge_bilibili_video_audio

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
            # 创建临时输出文件
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as output_temp:
                output_temp_path = output_temp.name
            
            try:
                # 尝试通过原始视频URL获取完整的视频信息（包括音频）
                print("Trying to get complete video info via hybrid parsing")
                
                # 尝试从视频URL中提取BV号
                bv_id = None
                bv_pattern = r'(BV[A-Za-z0-9]+)'
                bv_match = re.search(bv_pattern, video_url)
                if bv_match:
                    bv_id = bv_match.group(1)
                    print(f"Extracted BV ID from video URL: {bv_id}")
                
                # 如果找到BV号，直接使用BV号解析
                if bv_id:
                    bv_url = f"https://b23.tv/{bv_id}"
                    print(f"Using BV URL for hybrid parsing: {bv_url}")
                    try:
                        # 使用HybridCrawler解析视频信息
                        video_info = await HybridCrawler.hybrid_parsing_single_video(bv_url, minimal=False)
                        if video_info and 'data' in video_info and 'audio_url' in video_info['data']:
                            audio_url = video_info['data']['audio_url']
                            if audio_url:
                                print(f"Got audio URL via hybrid parsing: {audio_url}")
                                # 尝试合并音视频
                                try:
                                    success = await merge_bilibili_video_audio(video_url, audio_url, request, output_temp_path, headers)
                                    print(f"merge_bilibili_video_audio returned: {success}")
                                    
                                    if success and os.path.exists(output_temp_path) and os.path.getsize(output_temp_path) > 0:
                                        print(f"Successfully merged video and audio: {output_temp_path}")
                                        print(f"Merged file size: {os.path.getsize(output_temp_path)} bytes")
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
                                except Exception as e:
                                    print(f"Error in merge_bilibili_video_audio: {e}")
                    except Exception as e:
                        print(f"Failed to parse video via hybrid crawler: {e}")
                
                # 方法2: 如果没有BV号，尝试从视频流URL中提取信息
                print("Trying to extract video info from stream URL")
                # 尝试匹配视频流URL模式
                video_pattern = r'(https://[^/]+/upgcxcode/[0-9a-f]+/[0-9a-f]+/[0-9]+)/([0-9]+)-1-([0-9]+)\.(m4v|m4s)(\?.*)?$'
                video_match = re.search(video_pattern, video_url)
                
                if video_match:
                    base_url = video_match.group(1)
                    video_id = video_match.group(2)
                    query_params = video_match.group(5)
                    print(f"Extracted from stream URL: base_url={base_url}, video_id={video_id}")
                    
                    # 尝试直接使用视频流的基础URL和参数，修改格式为音频格式
                    # 常见的音频格式代码
                    audio_formats = ['30280', '30216', '30232', '101', '10000']
                    audio_exts = ['m4s', 'm4a']
                    
                    for fmt in audio_formats:
                        for ext in audio_exts:
                            # 生成音频URL
                            audio_url = f"{base_url}/{video_id}-1-{fmt}.{ext}"
                            if query_params:
                                audio_url += query_params
                            print(f"Trying audio URL: {audio_url}")
                            
                            # 尝试合并
                            try:
                                success = await merge_bilibili_video_audio(video_url, audio_url, request, output_temp_path, headers)
                                print(f"Merge attempt returned: {success}")
                                
                                if success and os.path.exists(output_temp_path) and os.path.getsize(output_temp_path) > 0:
                                    print(f"Successfully merged with audio URL: {output_temp_path}")
                                    print(f"Merged file size: {os.path.getsize(output_temp_path)} bytes")
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
                            except Exception as e:
                                print(f"Merge attempt failed: {e}")
                
                print("All audio URL attempts failed, returning video stream directly")
                
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
                if os.path.exists(output_temp_path):
                    try:
                        os.unlink(output_temp_path)
                        print(f"Cleaned up temporary file: {output_temp_path}")
                    except Exception as e:
                        print(f"Failed to clean up temporary file {output_temp_path}: {e}")
        
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