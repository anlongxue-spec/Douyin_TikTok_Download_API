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
                
                # 如果成功获取到音频URL，使用现有的合并函数
                if audio_url:
                    print(f"Using existing merge function for Bilibili video and audio")
                    try:
                        # 调用现有的合并函数
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
                        else:
                            print("Merge failed, returning video stream directly")
                    except Exception as e:
                        print(f"Error in merge_bilibili_video_audio: {e}")
                        import traceback
                        traceback.print_exc()
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