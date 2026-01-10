#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手无水印视频下载功能测试脚本
Kuaishou watermark-free video download test script
"""

import asyncio
import httpx
import json
import os
from crawlers.hybrid.hybrid_crawler import HybridCrawler

# 测试用快手视频URL
test_url = "https://v.kuaishou.com/n5T01Jd1"

async def test_video_extraction():
    """
    测试视频URL提取功能
    Test video URL extraction functionality
    """
    print("=== 测试1: 视频URL提取功能 ===")
    try:
        hybrid_crawler = HybridCrawler()
        data = await hybrid_crawler.hybrid_parsing_single_video(test_url, minimal=True)
        
        print(f"平台: {data.get('platform')}")
        print(f"视频ID: {data.get('video_id')}")
        print(f"作者昵称: {data.get('author_name')}")
        print(f"视频描述: {data.get('desc')}")
        print(f"有水印视频URL: {data.get('wm_video_url')}")
        print(f"无水印视频URL: {data.get('nwm_video_url')}")
        
        # 检查视频URL是否存在
        if data.get('nwm_video_url'):
            print("✅ 成功提取到无水印视频URL")
            return data.get('nwm_video_url')
        else:
            print("❌ 未能提取到无水印视频URL")
            return None
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_api_response():
    """
    测试API响应结构
    Test API response structure
    """
    print("\n=== 测试2: API响应结构检查 ===")
    try:
        hybrid_crawler = HybridCrawler()
        data = await hybrid_crawler.hybrid_parsing_single_video(test_url, minimal=True)
        
        # 检查所有必要字段是否存在
        required_fields = [
            'platform', 'video_id', 'author_name', 'desc', 
            'wm_video_url', 'nwm_video_url', 'author_id'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 缺少必要字段: {missing_fields}")
        else:
            print("✅ 所有必要字段都已包含")
        
        # 检查video_data结构
        if 'video_data' in data:
            video_data = data['video_data']
            print(f"video_data结构: {list(video_data.keys())}")
            if all(key in video_data for key in ['wm_video_url', 'nwm_video_url']):
                print("✅ video_data结构正确")
            else:
                print("❌ video_data结构不完整")
        else:
            print("❌ 缺少video_data字段")
            
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

async def test_video_download(video_url):
    """
    测试视频下载功能
    Test video download functionality
    """
    if not video_url:
        print("\n=== 测试3: 视频下载功能 ===")
        print("❌ 无法测试下载功能，因为没有视频URL")
        return
    
    print(f"\n=== 测试3: 视频下载功能 ===")
    print(f"测试下载URL: {video_url}")
    
    try:
        # 创建HybridCrawler实例获取请求头
        hybrid_crawler = HybridCrawler()
        headers = await hybrid_crawler.KuaiShouWebCrawler.get_kuaishou_headers()
        
        print(f"使用请求头: {headers['headers']}")
        
        # 测试视频URL是否可访问
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 先发送HEAD请求检查URL是否有效
            head_response = await client.head(video_url, headers=headers['headers'])
            print(f"HEAD请求状态码: {head_response.status_code}")
            
            if head_response.status_code == 200:
                print("✅ 视频URL可访问")
                
                # 测试获取视频数据（获取一小部分）
                print("测试获取视频数据...")
                response = await client.get(video_url, headers=headers['headers'], timeout=30.0, stream=True)
                
                # 只读取前10KB数据验证
                content = await response.aread(10240)
                print(f"✅ 成功获取视频数据，已读取 {len(content)} 字节")
                
                # 检查内容类型
                content_type = response.headers.get('content-type')
                print(f"视频内容类型: {content_type}")
                
                if content_type and 'video' in content_type:
                    print("✅ 确认是视频文件")
                    return True
                else:
                    print("❌ 不是视频文件")
                    return False
            else:
                print(f"❌ 视频URL不可访问，状态码: {head_response.status_code}")
                return False
    except httpx.RequestError as e:
        print(f"❌ 请求错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_download_api():
    """
    测试下载API端点
    Test download API endpoint
    """
    print("\n=== 测试4: 下载API端点测试 ===")
    try:
        # 测试通过API端点下载
        api_url = f"http://localhost:8000/api/download?url={test_url}&with_watermark=false"
        print(f"测试API端点: {api_url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(api_url)
            
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 检查响应内容类型
                content_type = response.headers.get('content-type')
                if content_type and 'video' in content_type:
                    print("✅ API端点成功返回视频文件")
                    # 保存一小部分视频验证
                    with open("test_kuaishou_video.mp4", "wb") as f:
                        f.write(response.content[:102400])  # 保存前100KB
                    print(f"✅ 已保存测试视频文件 (100KB)")
                    return True
                else:
                    print(f"❌ API返回的不是视频文件，内容类型: {content_type}")
                    print(f"API响应内容: {response.text[:500]}...")
                    return False
            else:
                print(f"❌ API端点请求失败")
                print(f"API响应内容: {response.text}")
                return False
    except httpx.RequestError as e:
        print(f"❌ API请求错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """
    主测试函数
    Main test function
    """
    print("开始测试快手无水印视频下载功能...")
    print(f"测试URL: {test_url}")
    print("=" * 50)
    
    # 运行所有测试
    video_url = await test_video_extraction()
    await test_api_response()
    await test_video_download(video_url)
    await test_download_api()
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
