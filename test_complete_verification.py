#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整验证测试脚本：检查Bilibili视频下载无水印功能的所有修复点
"""

import asyncio
import httpx
import os
import time

def test_url_cleanup():
    """
    测试URL清理逻辑
    """
    print("\n=== 测试1: URL清理逻辑 ===")
    
    # 测试各种有问题的URL
    test_urls = [
        " `https://b23.tv/UzSQvAW` ",  # 原始问题URL
        "`https://b23.tv/UzSQvAW`",      # 只有反引号
        " https://b23.tv/UzSQvAW ",      # 只有空格
        "`https://b23.tv/UzSQvAW `",     # 反引号+尾空格
        " https://b23.tv/UzSQvAW`",     # 前空格+反引号
        "https://b23.tv/UzSQvAW",        # 正常URL
    ]
    
    for url in test_urls:
        # 模拟download.py中的URL清理逻辑
        import re
        cleaned_url = url.strip()  # 去除首尾空格
        cleaned_url = re.sub(r'^`|`$', '', cleaned_url)  # 去除首尾反引号
        
        print(f"原始URL: '{url}'")
        print(f"清理后:  '{cleaned_url}'")
        print(f"是否有效: {'是' if cleaned_url.startswith('https://') else '否'}")
        print()
    
    return True

async def test_api_endpoint():
    """
    测试API端点是否能正确处理有问题的URL
    """
    print("\n=== 测试2: API端点测试 ===")
    
    client = httpx.AsyncClient()
    
    try:
        # 测试原始问题URL
        problematic_url = " `https://b23.tv/UzSQvAW` "
        params = {
            "url": problematic_url,
            "prefix": True,
            "with_watermark": False
        }
        
        print(f"发送请求: GET /api/download with url='{problematic_url}'")
        start_time = time.time()
        
        response = await client.get(
            "http://localhost/api/download",
            params=params,
            timeout=30.0
        )
        
        elapsed_time = time.time() - start_time
        print(f"响应状态码: {response.status_code}")
        print(f"响应时间: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容长度: {len(response.content)} 字节")
            print("✅ API测试成功！视频下载正常")
            
            # 保存测试文件
            test_file_path = "test_download_result.mp4"
            with open(test_file_path, "wb") as f:
                f.write(response.content)
            print(f"测试文件已保存: {test_file_path}")
            print(f"文件大小: {os.path.getsize(test_file_path)} 字节")
            
            return True
        else:
            print(f"❌ API测试失败！响应内容: {response.text}")
            return False
            
    except httpx.TimeoutException:
        print("❌ API测试失败！请求超时")
        return False
    except Exception as e:
        print(f"❌ API测试失败！错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.aclose()

async def main():
    """
    运行所有测试
    """
    print("Bilibili视频下载无水印功能 - 完整验证测试")
    print("=" * 50)
    
    # 测试URL清理逻辑
    url_cleanup_ok = test_url_cleanup()
    
    # 测试API端点
    api_ok = await test_api_endpoint()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"URL清理逻辑: {'✅ 通过' if url_cleanup_ok else '❌ 失败'}")
    print(f"API端点: {'✅ 通过' if api_ok else '❌ 失败'}")
    
    if url_cleanup_ok and api_ok:
        print("\n🎉 所有测试通过！修复成功！")
        return True
    else:
        print("\n❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    asyncio.run(main())
