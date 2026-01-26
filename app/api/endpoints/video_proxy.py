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
hybrid_crawler = HybridCrawler()

@router.get("/proxy_test", summary="代理配置测试/Proxy Configuration Test")
async def proxy_test(
    platform: str = Query(..., description="平台名称"),
):
    """
    测试代理配置
    """
    try:
        # 获取对应平台的headers
        if platform == 'tiktok':
            __headers = await hybrid_crawler.TikTokWebCrawler.get_tiktok_headers()
        elif platform == 'bilibili':
            __headers = await hybrid_crawler.BilibiliWebCrawler.get_bilibili_headers()
        elif platform == 'kuaishou':
            __headers = await hybrid_crawler.KuaiShouWebCrawler.get_kuaishou_headers()
        elif platform == 'xiaohongshu':
            __headers = await hybrid_crawler.XiaoHongShuWebCrawler.get_xiaohongshu_headers()
        elif platform == 'weibo':
            __headers = await hybrid_crawler.get_weibo_headers()
        else:  # douyin
            __headers = await hybrid_crawler.DouyinWebCrawler.get_douyin_headers()
        
        headers = __headers.get('headers', {})
        proxies = __headers.get('proxies', {})
        
        # 检查代理是否为空
        if not proxies:
            proxies_status = "Empty"
            proxies = None
        else:
            # 检查不同格式的代理配置
            has_valid_proxy = False
            
            # 检查标准格式（http, https）
            http_proxy = proxies.get('http')
            https_proxy = proxies.get('https')
            
            if http_proxy and isinstance(http_proxy, str) and http_proxy.strip():
                has_valid_proxy = True
            if https_proxy and isinstance(https_proxy, str) and https_proxy.strip():
                has_valid_proxy = True
            
            # 检查带协议格式（http://, https://）
            http_proxy_url = proxies.get('http://')
            https_proxy_url = proxies.get('https://')
            
            if http_proxy_url and isinstance(http_proxy_url, str) and http_proxy_url.strip():
                has_valid_proxy = True
            if https_proxy_url and isinstance(https_proxy_url, str) and https_proxy_url.strip():
                has_valid_proxy = True
            
            if not has_valid_proxy:
                proxies_status = "Empty"
                proxies = None
            else:
                proxies_status = "Valid"
        
        return {
            "platform": platform,
            "headers": headers,
            "proxies": proxies,
            "proxies_status": proxies_status
        }
    except Exception as e:
        return {
            "error": str(e)
        }

@router.get("/video_proxy", summary="视频代理下载/Video Proxy Download")
async def video_proxy(
    request: Request,
    video_url: str = Query(...),
    platform: str = Query(...),
    with_audio: bool = Query(False),
    merge: bool = Query(False) ):
    print(f"Received video proxy request for platform: {platform}")
    print(f"Video URL: {video_url}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"with_audio: {with_audio}, merge: {merge}")
    """
    视频代理下载端点，避免浏览器直接访问第三方视频URL导致的跨域错误
    
    Parameters:
    - video_url: 原始视频URL
    - platform: 平台名称（用于获取正确的headers）
    - with_audio: 是否包含音频
    - merge: 是否合并视频和音频
    """
    try:
        # 获取对应平台的headers
        if platform == 'tiktok':
            __headers = await hybrid_crawler.TikTokWebCrawler.get_tiktok_headers()
        elif platform == 'bilibili':
            __headers = await hybrid_crawler.BilibiliWebCrawler.get_bilibili_headers()
            print(f"Bilibili headers: {__headers.get('headers', {})}")
        elif platform == 'kuaishou':
            __headers = await hybrid_crawler.KuaiShouWebCrawler.get_kuaishou_headers()
        elif platform == 'xiaohongshu':
            __headers = await hybrid_crawler.XiaoHongShuWebCrawler.get_xiaohongshu_headers()
        elif platform == 'weibo':
            __headers = await hybrid_crawler.get_weibo_headers()
        else:  # douyin
            __headers = await hybrid_crawler.DouyinWebCrawler.get_douyin_headers()
        
        headers = __headers.get('headers', {})
        proxies = __headers.get('proxies', {})
        
        print(f"Original proxies: {proxies}")
        print(f"Type of proxies: {type(proxies)}")
        
        # 检查代理是否为空
        if not proxies:
            print("Empty proxies detected, using no proxy")
            proxies = None
        else:
            # 检查不同格式的代理配置
            has_valid_proxy = False
            
            # 检查标准格式（http, https）
            http_proxy = proxies.get('http')
            https_proxy = proxies.get('https')
            print(f"HTTP proxy: {http_proxy}")
            print(f"HTTPS proxy: {https_proxy}")
            
            if http_proxy and isinstance(http_proxy, str) and http_proxy.strip():
                has_valid_proxy = True
                print("Found valid HTTP proxy")
            if https_proxy and isinstance(https_proxy, str) and https_proxy.strip():
                has_valid_proxy = True
                print("Found valid HTTPS proxy")
            
            # 检查带协议格式（http://, https://）
            http_proxy_url = proxies.get('http://')
            https_proxy_url = proxies.get('https://')
            print(f"HTTP proxy URL: {http_proxy_url}")
            print(f"HTTPS proxy URL: {https_proxy_url}")
            
            if http_proxy_url and isinstance(http_proxy_url, str) and http_proxy_url.strip():
                has_valid_proxy = True
                print("Found valid HTTP proxy URL")
            if https_proxy_url and isinstance(https_proxy_url, str) and https_proxy_url.strip():
                has_valid_proxy = True
                print("Found valid HTTPS proxy URL")
            
            print(f"has_valid_proxy: {has_valid_proxy}")
            
            if not has_valid_proxy:
                print("Empty proxies detected, using no proxy")
                proxies = None
        
        print(f"Final proxies: {proxies}")
        
        # 处理范围请求
        range_header = request.headers.get('range')
        print(f"Range header: {range_header}")
        
        # 构建请求头，包含范围请求
        request_headers = headers.copy()
        if range_header:
            request_headers['range'] = range_header
            print(f"Added range header to request: {range_header}")
        
        print(f"Using headers: {request_headers}")
        print(f"Using proxies: {proxies}")
        
        # 统一的视频处理函数
        async def handle_video_request(url, platform_name):
            # 根据是否有代理来创建不同的client
            if proxies:
                async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False, proxies=proxies) as client:
                    try:
                        # 先尝试流式请求
                        async with client.stream('GET', url, headers=request_headers) as response:
                            return await process_response(response, platform_name)
                    except Exception as e:
                        print(f"Streaming request failed: {e}")
                        # 如果流式请求失败，尝试普通请求
                        try:
                            print("Falling back to non-streaming request")
                            response = await client.get(url, headers=request_headers)
                            return await process_non_streaming_response(response, platform_name)
                        except Exception as e2:
                            print(f"Non-streaming request failed: {e2}")
                            raise
            else:
                async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                    try:
                        # 先尝试流式请求
                        async with client.stream('GET', url, headers=request_headers) as response:
                            return await process_response(response, platform_name)
                    except Exception as e:
                        print(f"Streaming request failed: {e}")
                        # 如果流式请求失败，尝试普通请求
                        try:
                            print("Falling back to non-streaming request")
                            response = await client.get(url, headers=request_headers)
                            return await process_non_streaming_response(response, platform_name)
                        except Exception as e2:
                            print(f"Non-streaming request failed: {e2}")
                            raise
        
        async def process_response(response, platform_name):
            # 检查响应状态码
            print(f"Video stream response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code not in [200, 206]:
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
            
            # 获取响应头中的Content-Type
            content_type = response.headers.get('content-type', 'video/mp4')
            print(f"Content-Type from response: {content_type}")
            
            # 构建响应头
            response_headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Origin, Range, Content-Type',
                'Access-Control-Expose-Headers': 'Content-Length, Content-Range',
                'Content-Disposition': f'attachment; filename="{platform_name}_video.mp4"'
            }
            
            # 复制原始响应头中的相关字段
            if 'content-length' in response.headers:
                response_headers['Content-Length'] = response.headers['content-length']
            if 'content-range' in response.headers:
                response_headers['Content-Range'] = response.headers['content-range']
            if 'accept-ranges' in response.headers:
                response_headers['Accept-Ranges'] = response.headers['accept-ranges']
            
            async def stream_content():
                total_bytes = 0
                chunk_count = 0
                has_data = False
                try:
                    # 直接读取所有chunk
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        if chunk:
                            has_data = True
                            total_bytes += len(chunk)
                            chunk_count += 1
                            if chunk_count == 1:
                                print(f"Yielded first chunk, size: {len(chunk)}")
                            elif chunk_count % 10 == 0:  # 每10个chunk打印一次，避免日志过多
                                print(f"Yielded {chunk_count} chunks, total bytes: {total_bytes}")
                            yield chunk
                    
                    if not has_data:
                        print("No data received from server")
                        # 如果没有数据，抛出异常
                        raise HTTPException(
                            status_code=500,
                            detail="视频内容为空"
                        )
                    
                    print(f"Stream completed successfully, total bytes: {total_bytes}, total chunks: {chunk_count}")
                except httpx.StreamClosed as e:
                    print(f"Stream closed by server, total bytes sent: {total_bytes}, chunks: {chunk_count}")
                    # 继续完成流，不要中断
                except Exception as e:
                    print(f"Error reading stream: {e}")
                    import traceback
                    traceback.print_exc()
                    # 尝试继续，不要因为错误中断整个流程
            
            print("Starting to stream video content")
            return StreamingResponse(
                content=stream_content(),
                media_type=content_type,
                headers=response_headers,
                status_code=response.status_code
            )
        
        async def process_non_streaming_response(response, platform_name):
            print(f"Video response status: {response.status_code}")
            print(f"Response content length: {len(response.content)}")
            
            # 检查响应状态码
            if response.status_code not in [200, 206]:
                print(f"Video request failed with status: {response.status_code}")
                # 确保使用标准的HTTP状态码
                if response.status_code < 100 or response.status_code >= 600:
                    status_code = 500
                else:
                    status_code = response.status_code
                raise HTTPException(
                    status_code=status_code,
                    detail=f"视频请求失败: {response.status_code}"
                )
            
            # 检查响应内容是否为空
            if not response.content:
                print("Response content is empty")
                raise HTTPException(
                    status_code=500,
                    detail="视频内容为空"
                )
            
            # 获取响应头中的Content-Type
            content_type = response.headers.get('content-type', 'video/mp4')
            
            # 构建响应头
            response_headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Origin, Range, Content-Type',
                'Access-Control-Expose-Headers': 'Content-Length, Content-Range',
                'Content-Disposition': f'attachment; filename="{platform_name}_video.mp4"',
                'Content-Length': str(len(response.content))
            }
            
            # 复制原始响应头中的相关字段
            if 'content-range' in response.headers:
                response_headers['Content-Range'] = response.headers['content-range']
            if 'accept-ranges' in response.headers:
                response_headers['Accept-Ranges'] = response.headers['accept-ranges']
            
            async def stream_content():
                yield response.content
            
            print("Returning video content as bytes")
            return StreamingResponse(
                content=stream_content(),
                media_type=content_type,
                headers=response_headers,
                status_code=response.status_code
            )
        
        # 处理视频请求
        # 对于B站视频，如果需要音频且需要合并，使用专门的合并函数
        if platform == 'bilibili' and with_audio and merge:
            print("Processing Bilibili video with audio merge")
            # 从请求中获取音频URL（如果有）
            audio_url = request.query_params.get('audio_url')
            print(f"Audio URL from params: {audio_url}")
            
            if not audio_url:
                print("No audio URL provided, cannot merge video and audio")
                # 如果没有音频URL，回退到普通处理
                return await handle_video_request(video_url, platform)
            
            # 创建临时文件来存储合并后的视频
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_output:
                output_path = temp_output.name
            
            print(f"Created temporary output file: {output_path}")
            
            try:
                # 使用合并函数处理视频和音频
                success = await merge_bilibili_video_audio(video_url, audio_url, request, output_path, headers)
                print(f"Merge operation result: {success}")
                
                if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print(f"Merge successful, output size: {os.path.getsize(output_path)} bytes")
                    # 读取合并后的视频文件并返回
                    async def stream_merged_content():
                        async with aiofiles.open(output_path, 'rb') as f:
                            chunk = await f.read(8192)
                            while chunk:
                                yield chunk
                                chunk = await f.read(8192)
                    
                    # 构建响应头
                    response_headers = {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, OPTIONS',
                        'Access-Control-Allow-Headers': 'Origin, Range, Content-Type',
                        'Access-Control-Expose-Headers': 'Content-Length',
                        'Content-Disposition': f'attachment; filename="bilibili_video_merged.mp4"',
                        'Content-Length': str(os.path.getsize(output_path))
                    }
                    
                    print("Returning merged video content")
                    return StreamingResponse(
                        content=stream_merged_content(),
                        media_type='video/mp4',
                        headers=response_headers
                    )
                else:
                    print("Merge failed, falling back to original video")
                    # 如果合并失败，回退到普通处理
                    return await handle_video_request(video_url, platform)
            finally:
                # 清理临时文件
                if os.path.exists(output_path):
                    try:
                        os.unlink(output_path)
                        print(f"Cleaned up temporary file: {output_path}")
                    except Exception as e:
                        print(f"Failed to clean up temporary file: {e}")
        else:
            # 其他情况，使用普通处理
            return await handle_video_request(video_url, platform)
        
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