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
            print(f"Bilibili headers: {__headers.get('headers', {})}")
        elif platform == 'kuaishou':
            __headers = await HybridCrawler.KuaiShouWebCrawler.get_kuaishou_headers()
        elif platform == 'xiaohongshu':
            __headers = await HybridCrawler.XiaoHongShuWebCrawler.get_xiaohongshu_headers()
        elif platform == 'weibo':
            __headers = await HybridCrawler.get_weibo_headers()
        else:  # douyin
            __headers = await HybridCrawler.DouyinWebCrawler.get_douyin_headers()
        
        headers = __headers.get('headers', {})
        print(f"Using headers: {headers}")
        
        # B站视频特殊处理：直接流式返回视频内容
        if platform == 'bilibili':
            # 直接使用流式读取，返回视频内容，不使用临时文件
            print("Streaming Bilibili video content directly")
            print(f"Using video URL: {video_url}")
            print(f"Using headers: {headers}")
            try:
                async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                    async with client.stream('GET', video_url, headers=headers) as response:
                        # 检查响应状态码
                        print(f"Video stream response status: {response.status_code}")
                        print(f"Response headers: {dict(response.headers)}")
                        
                        if response.status_code != 200:
                            print(f"Video stream request failed with status: {response.status_code}")
                            # 确保使用标准的HTTP状态码
                            if response.status_code < 100 or response.status_code >= 600:
                                status_code = 500
                            else:
                                status_code = response.status_code
                            raise HTTPException(
                                status_code=status_code,
                                detail=f"视频流请求失败: {response.status_code}"
                            )
                        
                        async def stream_content():
                            total_bytes = 0
                            try:
                                async for chunk in response.aiter_bytes(chunk_size=8192):
                                    if chunk:
                                        total_bytes += len(chunk)
                                        print(f"Yielding chunk of size: {len(chunk)}, total: {total_bytes}")
                                        yield chunk
                                    else:
                                        print("Received empty chunk")
                                print(f"Stream completed, total bytes: {total_bytes}")
                            except httpx.StreamClosed:
                                print(f"Stream closed by server, total bytes sent: {total_bytes}")
                            except Exception as e:
                                print(f"Error reading stream: {e}")
                                import traceback
                                traceback.print_exc()
                        
                        print("Starting to stream Bilibili video content")
                        return StreamingResponse(
                            content=stream_content(),
                            media_type='video/mp4',
                            headers={
                                'Content-Disposition': f'attachment; filename="bilibili_video.mp4"',
                                'Access-Control-Allow-Origin': '*'
                            }
                        )
            except Exception as e:
                print(f"Streaming failed: {e}")
                import traceback
                traceback.print_exc()
                # 如果流式读取失败，尝试使用普通请求
                try:
                    async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                        response = await client.get(video_url, headers=headers)
                        print(f"Video stream response status: {response.status_code}")
                        print(f"Response content length: {len(response.content)}")
                        
                        async def stream_content():
                            yield response.content
                        
                        print("Returning Bilibili video content as bytes")
                        return StreamingResponse(
                            content=stream_content(),
                            media_type='video/mp4',
                            headers={
                                'Content-Disposition': f'attachment; filename="bilibili_video.mp4"'
                            }
                        )
                except Exception as e:
                    print(f"Failed to get video content: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"无法获取视频内容: {str(e)}"
                    )
        
        # 其他平台直接返回视频流
        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
            # 使用流式读取来避免内存问题
            try:
                async with client.stream('GET', video_url, headers=headers) as response:
                    # 不调用raise_for_status()，避免非标准状态码错误
                    print(f"Video stream response status: {response.status_code}")
                    
                    async def stream_content():
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            yield chunk
                    
                    # 返回视频流
                    return StreamingResponse(
                        content=stream_content(),
                        media_type='video/mp4',
                        headers={
                            'Content-Disposition': f'attachment; filename="{platform}_video.mp4"'
                        }
                    )
            except Exception as e:
                print(f"Streaming failed: {e}")
                # 如果流式读取失败，尝试使用普通请求
                response = await client.get(video_url, headers=headers)
                print(f"Video stream response status: {response.status_code}")
                
                async def stream_content():
                    yield response.content
                
                # 返回视频流
                return StreamingResponse(
                    content=stream_content(),
                    media_type='video/mp4',
                    headers={
                        'Content-Disposition': f'attachment; filename="{platform}_video.mp4"'
                    }
                )
            
    except httpx.HTTPStatusError as e:
        # 确保使用标准的HTTP状态码
        status_code = e.response.status_code
        if status_code < 100 or status_code >= 600:
            status_code = 500
        raise HTTPException(
            status_code=status_code,
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