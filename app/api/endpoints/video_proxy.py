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
    platform: str = Query(...) ):
    print(f"Received video proxy request for platform: {platform}")
    print(f"Video URL: {video_url}")
    print(f"Request headers: {dict(request.headers)}")
    """
    视频代理下载端点，避免浏览器直接访问第三方视频URL导致的跨域错误
    
    Parameters:
    - video_url: 原始视频URL
    - platform: 平台名称（用于获取正确的headers）
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
        
        print(f"Using headers: {headers}")
        print(f"Using proxies: {proxies}")
        
        # B站视频特殊处理：直接流式返回视频内容
        if platform == 'bilibili':
            # 直接使用流式读取，返回视频内容，不使用临时文件
            print("Streaming Bilibili video content directly")
            print(f"Using video URL: {video_url}")
            print(f"Using headers: {headers}")
            try:
                # 根据是否有代理来创建不同的client
                if proxies:
                    async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False, proxies=proxies) as client:
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
                            
                            # 获取响应头中的Content-Type
                            content_type = response.headers.get('content-type', 'video/mp4')
                            print(f"Content-Type from response: {content_type}")
                            
                            # 构建响应头
                            response_headers = {
                                'Access-Control-Allow-Origin': '*',
                                'Content-Disposition': f'attachment; filename="bilibili_video.mp4"'
                            }
                            
                            # 先尝试读取第一个chunk，确保有数据可用
                            first_chunk = None
                            try:
                                async for chunk in response.aiter_bytes(chunk_size=8192):
                                    first_chunk = chunk
                                    break
                            except Exception as e:
                                print(f"Error reading first chunk: {e}")
                            
                            # 检查是否有数据
                            if not first_chunk:
                                print("No data received from server, falling back to non-streaming request")
                                # 如果没有数据，尝试使用普通请求
                                try:
                                    # 重新创建client获取完整内容
                                    if proxies:
                                        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False, proxies=proxies) as client:
                                            response = await client.get(video_url, headers=headers)
                                    else:
                                        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                                            response = await client.get(video_url, headers=headers)
                                    
                                    print(f"Non-streaming response status: {response.status_code}")
                                    print(f"Non-streaming content length: {len(response.content)}")
                                    
                                    if not response.content:
                                        print("Non-streaming response content is empty")
                                        raise HTTPException(
                                            status_code=500,
                                            detail="视频内容为空"
                                        )
                                    
                                    # 构建响应头
                                    non_streaming_headers = {
                                        'Access-Control-Allow-Origin': '*',
                                        'Content-Disposition': f'attachment; filename="bilibili_video.mp4"',
                                        'Content-Length': str(len(response.content))
                                    }
                                    
                                    async def stream_content():
                                        yield response.content
                                    
                                    print("Returning Bilibili video content as bytes")
                                    return StreamingResponse(
                                        content=stream_content(),
                                        media_type=content_type,
                                        headers=non_streaming_headers
                                    )
                                except Exception as e:
                                    print(f"Non-streaming fallback failed: {e}")
                                    raise HTTPException(
                                        status_code=500,
                                        detail="无法获取视频内容"
                                    )
                            
                            # 如果有数据，继续使用流式传输
                            # 注意：不再添加Content-Length头，避免"Too little data"错误
                            print("First chunk received, using streaming transfer")
                            
                            async def stream_content():
                                total_bytes = 0
                                chunk_count = 0
                                try:
                                    # 先发送第一个chunk
                                    if first_chunk:
                                        total_bytes += len(first_chunk)
                                        chunk_count += 1
                                        print(f"Yielded first chunk, size: {len(first_chunk)}")
                                        yield first_chunk
                                    
                                    # 继续读取剩余的chunk
                                    async for chunk in response.aiter_bytes(chunk_size=8192):
                                        if chunk:
                                            total_bytes += len(chunk)
                                            chunk_count += 1
                                            if chunk_count % 10 == 0:  # 每10个chunk打印一次，避免日志过多
                                                print(f"Yielded {chunk_count} chunks, total bytes: {total_bytes}")
                                            yield chunk
                                    print(f"Stream completed successfully, total bytes: {total_bytes}, total chunks: {chunk_count}")
                                except httpx.StreamClosed as e:
                                    print(f"Stream closed by server, total bytes sent: {total_bytes}, chunks: {chunk_count}")
                                    # 继续完成流，不要中断
                                except Exception as e:
                                    print(f"Error reading stream: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    # 尝试继续，不要因为错误中断整个流程
                            
                            print("Starting to stream Bilibili video content")
                            return StreamingResponse(
                                content=stream_content(),
                                media_type=content_type,
                                headers=response_headers
                            )
                else:
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
                            
                            # 获取响应头中的Content-Type
                            content_type = response.headers.get('content-type', 'video/mp4')
                            print(f"Content-Type from response: {content_type}")
                            
                            # 构建响应头
                            response_headers = {
                                'Access-Control-Allow-Origin': '*',
                                'Content-Disposition': f'attachment; filename="bilibili_video.mp4"'
                            }
                            
                            # 先尝试读取第一个chunk，确保有数据可用
                            first_chunk = None
                            try:
                                async for chunk in response.aiter_bytes(chunk_size=8192):
                                    first_chunk = chunk
                                    break
                            except Exception as e:
                                print(f"Error reading first chunk: {e}")
                            
                            # 检查是否有数据
                            if not first_chunk:
                                print("No data received from server, falling back to non-streaming request")
                                # 如果没有数据，尝试使用普通请求
                                try:
                                    # 重新创建client获取完整内容
                                    async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                                        response = await client.get(video_url, headers=headers)
                                    
                                    print(f"Non-streaming response status: {response.status_code}")
                                    print(f"Non-streaming content length: {len(response.content)}")
                                    
                                    if not response.content:
                                        print("Non-streaming response content is empty")
                                        raise HTTPException(
                                            status_code=500,
                                            detail="视频内容为空"
                                        )
                                    
                                    # 构建响应头
                                    non_streaming_headers = {
                                        'Access-Control-Allow-Origin': '*',
                                        'Content-Disposition': f'attachment; filename="bilibili_video.mp4"',
                                        'Content-Length': str(len(response.content))
                                    }
                                    
                                    async def stream_content():
                                        yield response.content
                                    
                                    print("Returning Bilibili video content as bytes")
                                    return StreamingResponse(
                                        content=stream_content(),
                                        media_type=content_type,
                                        headers=non_streaming_headers
                                    )
                                except Exception as e:
                                    print(f"Non-streaming fallback failed: {e}")
                                    raise HTTPException(
                                        status_code=500,
                                        detail="无法获取视频内容"
                                    )
                            
                            # 如果有数据，继续使用流式传输
                            # 注意：不再添加Content-Length头，避免"Too little data"错误
                            print("First chunk received, using streaming transfer")
                            
                            async def stream_content():
                                total_bytes = 0
                                chunk_count = 0
                                try:
                                    # 先发送第一个chunk
                                    if first_chunk:
                                        total_bytes += len(first_chunk)
                                        chunk_count += 1
                                        print(f"Yielded first chunk, size: {len(first_chunk)}")
                                        yield first_chunk
                                    
                                    # 继续读取剩余的chunk
                                    async for chunk in response.aiter_bytes(chunk_size=8192):
                                        if chunk:
                                            total_bytes += len(chunk)
                                            chunk_count += 1
                                            if chunk_count % 10 == 0:  # 每10个chunk打印一次，避免日志过多
                                                print(f"Yielded {chunk_count} chunks, total bytes: {total_bytes}")
                                            yield chunk
                                    print(f"Stream completed successfully, total bytes: {total_bytes}, total chunks: {chunk_count}")
                                except httpx.StreamClosed as e:
                                    print(f"Stream closed by server, total bytes sent: {total_bytes}, chunks: {chunk_count}")
                                    # 继续完成流，不要中断
                                except Exception as e:
                                    print(f"Error reading stream: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    # 尝试继续，不要因为错误中断整个流程
                            
                            print("Starting to stream Bilibili video content")
                            return StreamingResponse(
                                content=stream_content(),
                                media_type=content_type,
                                headers=response_headers
                            )
            except Exception as e:
                print(f"Streaming failed: {e}")
                import traceback
                traceback.print_exc()
                # 如果流式读取失败，尝试使用普通请求
                try:
                    print("Falling back to non-streaming request")
                    # 根据是否有代理来创建不同的client
                    if proxies:
                        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False, proxies=proxies) as client:
                            response = await client.get(video_url, headers=headers)
                            print(f"Video stream response status: {response.status_code}")
                            print(f"Response content length: {len(response.content)}")
                            
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
                                'Content-Disposition': f'attachment; filename="bilibili_video.mp4"',
                                'Content-Length': str(len(response.content))
                            }
                            
                            async def stream_content():
                                yield response.content
                            
                            print("Returning Bilibili video content as bytes")
                            return StreamingResponse(
                                content=stream_content(),
                                media_type=content_type,
                                headers=response_headers
                            )
                    else:
                        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                            response = await client.get(video_url, headers=headers)
                            print(f"Video stream response status: {response.status_code}")
                            print(f"Response content length: {len(response.content)}")
                            
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
                                'Content-Disposition': f'attachment; filename="bilibili_video.mp4"',
                                'Content-Length': str(len(response.content))
                            }
                            
                            async def stream_content():
                                yield response.content
                            
                            print("Returning Bilibili video content as bytes")
                            return StreamingResponse(
                                content=stream_content(),
                                media_type=content_type,
                                headers=response_headers
                            )
                except Exception as e:
                    print(f"Failed to get video content: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"无法获取视频内容: {str(e)}"
                    )
        
        # 其他平台直接返回视频流
        # 根据是否有代理来创建不同的client
        if proxies:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False, proxies=proxies) as client:
                # 使用流式读取来避免内存问题
                try:
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
                        
                        # 获取响应头中的Content-Type
                        content_type = response.headers.get('content-type', 'video/mp4')
                        print(f"Content-Type from response: {content_type}")
                        
                        # 构建响应头
                        response_headers = {
                            'Access-Control-Allow-Origin': '*',
                            'Content-Disposition': f'attachment; filename="{platform}_video.mp4"'
                        }
                        
                        # 先尝试读取第一个chunk，确保有数据可用
                        first_chunk = None
                        try:
                            async for chunk in response.aiter_bytes(chunk_size=8192):
                                first_chunk = chunk
                                break
                        except Exception as e:
                            print(f"Error reading first chunk: {e}")
                        
                        # 检查是否有数据
                        if not first_chunk:
                            print("No data received from server, falling back to non-streaming request")
                            # 如果没有数据，尝试使用普通请求
                            try:
                                # 重新创建client获取完整内容
                                if proxies:
                                    async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False, proxies=proxies) as client:
                                        response = await client.get(video_url, headers=headers)
                                else:
                                    async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                                        response = await client.get(video_url, headers=headers)
                                
                                print(f"Non-streaming response status: {response.status_code}")
                                print(f"Non-streaming content length: {len(response.content)}")
                                
                                if not response.content:
                                    print("Non-streaming response content is empty")
                                    raise HTTPException(
                                        status_code=500,
                                        detail="视频内容为空"
                                    )
                                
                                # 构建响应头
                                non_streaming_headers = {
                                    'Access-Control-Allow-Origin': '*',
                                    'Content-Disposition': f'attachment; filename="{platform}_video.mp4"',
                                    'Content-Length': str(len(response.content))
                                }
                                
                                async def stream_content():
                                    yield response.content
                                
                                print(f"Returning {platform} video content as bytes")
                                return StreamingResponse(
                                    content=stream_content(),
                                    media_type=content_type,
                                    headers=non_streaming_headers
                                )
                            except Exception as e:
                                print(f"Non-streaming fallback failed: {e}")
                                raise HTTPException(
                                    status_code=500,
                                    detail="无法获取视频内容"
                                )
                        
                        # 如果有数据，继续使用流式传输
                        # 注意：不再添加Content-Length头，避免"Too little data"错误
                        print("First chunk received, using streaming transfer")
                        
                        async def stream_content():
                            total_bytes = 0
                            chunk_count = 0
                            try:
                                # 先发送第一个chunk
                                if first_chunk:
                                    total_bytes += len(first_chunk)
                                    chunk_count += 1
                                    print(f"Yielded first chunk, size: {len(first_chunk)}")
                                    yield first_chunk
                                
                                # 继续读取剩余的chunk
                                async for chunk in response.aiter_bytes(chunk_size=8192):
                                    if chunk:
                                        total_bytes += len(chunk)
                                        chunk_count += 1
                                        if chunk_count % 10 == 0:  # 每10个chunk打印一次，避免日志过多
                                            print(f"Yielded {chunk_count} chunks, total bytes: {total_bytes}")
                                        yield chunk
                                print(f"Stream completed successfully, total bytes: {total_bytes}, total chunks: {chunk_count}")
                            except httpx.StreamClosed as e:
                                print(f"Stream closed by server, total bytes sent: {total_bytes}, chunks: {chunk_count}")
                                # 继续完成流，不要中断
                            except Exception as e:
                                print(f"Error reading stream: {e}")
                                import traceback
                                traceback.print_exc()
                                # 尝试继续，不要因为错误中断整个流程
                        
                        # 返回视频流
                        return StreamingResponse(
                            content=stream_content(),
                            media_type=content_type,
                            headers=response_headers
                        )
                except Exception as e:
                    print(f"Streaming failed: {e}")
                    import traceback
                    traceback.print_exc()
                    # 如果流式读取失败，尝试使用普通请求
                    try:
                        response = await client.get(video_url, headers=headers)
                        print(f"Video stream response status: {response.status_code}")
                        print(f"Response content length: {len(response.content)}")
                        
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
                            'Content-Disposition': f'attachment; filename="{platform}_video.mp4"',
                            'Content-Length': str(len(response.content))
                        }
                        
                        async def stream_content():
                            yield response.content
                        
                        # 返回视频流
                        return StreamingResponse(
                            content=stream_content(),
                            media_type=content_type,
                            headers=response_headers
                        )
                    except Exception as e:
                        print(f"Failed to get video content: {e}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"无法获取视频内容: {str(e)}"
                        )
        else:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                # 使用流式读取来避免内存问题
                try:
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
                        
                        # 获取响应头中的Content-Type
                        content_type = response.headers.get('content-type', 'video/mp4')
                        print(f"Content-Type from response: {content_type}")
                        
                        # 构建响应头
                        response_headers = {
                            'Access-Control-Allow-Origin': '*',
                            'Content-Disposition': f'attachment; filename="{platform}_video.mp4"'
                        }
                        
                        # 先尝试读取第一个chunk，确保有数据可用
                        first_chunk = None
                        try:
                            async for chunk in response.aiter_bytes(chunk_size=8192):
                                first_chunk = chunk
                                break
                        except Exception as e:
                            print(f"Error reading first chunk: {e}")
                        
                        # 检查是否有数据
                        if not first_chunk:
                            print("No data received from server, falling back to non-streaming request")
                            # 如果没有数据，尝试使用普通请求
                            try:
                                # 重新创建client获取完整内容
                                async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
                                    response = await client.get(video_url, headers=headers)
                                
                                print(f"Non-streaming response status: {response.status_code}")
                                print(f"Non-streaming content length: {len(response.content)}")
                                
                                if not response.content:
                                    print("Non-streaming response content is empty")
                                    raise HTTPException(
                                        status_code=500,
                                        detail="视频内容为空"
                                    )
                                
                                # 构建响应头
                                non_streaming_headers = {
                                    'Access-Control-Allow-Origin': '*',
                                    'Content-Disposition': f'attachment; filename="{platform}_video.mp4"',
                                    'Content-Length': str(len(response.content))
                                }
                                
                                async def stream_content():
                                    yield response.content
                                
                                print(f"Returning {platform} video content as bytes")
                                return StreamingResponse(
                                    content=stream_content(),
                                    media_type=content_type,
                                    headers=non_streaming_headers
                                )
                            except Exception as e:
                                print(f"Non-streaming fallback failed: {e}")
                                raise HTTPException(
                                    status_code=500,
                                    detail="无法获取视频内容"
                                )
                        
                        # 如果有数据，继续使用流式传输
                        # 注意：不再添加Content-Length头，避免"Too little data"错误
                        print("First chunk received, using streaming transfer")
                        
                        async def stream_content():
                            total_bytes = 0
                            chunk_count = 0
                            try:
                                # 先发送第一个chunk
                                if first_chunk:
                                    total_bytes += len(first_chunk)
                                    chunk_count += 1
                                    print(f"Yielded first chunk, size: {len(first_chunk)}")
                                    yield first_chunk
                                
                                # 继续读取剩余的chunk
                                async for chunk in response.aiter_bytes(chunk_size=8192):
                                    if chunk:
                                        total_bytes += len(chunk)
                                        chunk_count += 1
                                        if chunk_count % 10 == 0:  # 每10个chunk打印一次，避免日志过多
                                            print(f"Yielded {chunk_count} chunks, total bytes: {total_bytes}")
                                        yield chunk
                                print(f"Stream completed successfully, total bytes: {total_bytes}, total chunks: {chunk_count}")
                            except httpx.StreamClosed as e:
                                print(f"Stream closed by server, total bytes sent: {total_bytes}, chunks: {chunk_count}")
                                # 继续完成流，不要中断
                            except Exception as e:
                                print(f"Error reading stream: {e}")
                                import traceback
                                traceback.print_exc()
                                # 尝试继续，不要因为错误中断整个流程
                        
                        # 返回视频流
                        return StreamingResponse(
                            content=stream_content(),
                            media_type=content_type,
                            headers=response_headers
                        )
                except Exception as e:
                    print(f"Streaming failed: {e}")
                    import traceback
                    traceback.print_exc()
                    # 如果流式读取失败，尝试使用普通请求
                    try:
                        response = await client.get(video_url, headers=headers)
                        print(f"Video stream response status: {response.status_code}")
                        print(f"Response content length: {len(response.content)}")
                        
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
                            'Content-Disposition': f'attachment; filename="{platform}_video.mp4"',
                            'Content-Length': str(len(response.content))
                        }
                        
                        async def stream_content():
                            yield response.content
                        
                        # 返回视频流
                        return StreamingResponse(
                            content=stream_content(),
                            media_type=content_type,
                            headers=response_headers
                        )
                    except Exception as e:
                        print(f"Failed to get video content: {e}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"无法获取视频内容: {str(e)}"
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