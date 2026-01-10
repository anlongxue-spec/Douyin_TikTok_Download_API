#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书API调试脚本
XiaoHongShu API debugging script
"""

import asyncio
import httpx
import json

async def test_xiaohongshu_api():
    """
    测试小红书API端点
    Test XiaoHongShu API endpoints
    """
    print("=== 测试小红书API端点 ===")
    
    # 测试URL和参数
    note_id = "67703823000000000251a047"
    
    # 原始API端点
    original_url = f"https://www.xiaohongshu.com/api/sns/v1/note/detail?note_id={note_id}&image_formats=jpg&webpage_id="
    
    # 尝试不同的API端点
    test_endpoints = [
        f"https://www.xiaohongshu.com/api/sns/v1/note/detail?note_id={note_id}",
        f"https://www.xiaohongshu.com/api/sns/web/v1/note/detail?note_id={note_id}",
        f"https://www.xiaohongshu.com/api/v1/note/detail?note_id={note_id}",
        f"https://www.xiaohongshu.com/explore/{note_id}"  # 网页版
    ]
    
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.xiaohongshu.com/",
        "Cookie": "",  # 可以尝试添加一个有效的Cookie
        "Content-Type": "application/json",
        "Origin": "https://www.xiaohongshu.com"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 测试原始API端点
        print(f"\n测试原始API端点: {original_url}")
        try:
            response = await client.get(original_url, headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text[:1000]}...")
        except Exception as e:
            print(f"请求失败: {type(e).__name__}: {e}")
        
        # 测试其他可能的API端点
        for endpoint in test_endpoints:
            print(f"\n测试API端点: {endpoint}")
            try:
                response = await client.get(endpoint, headers=headers)
                print(f"状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                print(f"响应内容: {response.text[:1000]}...")
            except Exception as e:
                print(f"请求失败: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_xiaohongshu_api())
