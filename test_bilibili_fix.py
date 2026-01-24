import httpx
import asyncio
import json

async def test_bilibili_download():
    """测试Bilibili视频下载修复效果"""
    test_urls = [
        # 原始问题URL（包含空格和反引号）
        " `https://b23.tv/UzSQvAW` ",
        # 正常URL
        "https://b23.tv/UzSQvAW",
        # 其他测试URL
        "https://www.bilibili.com/video/BV1mG411n73c"
    ]
    
    async with httpx.AsyncClient() as client:
        for test_url in test_urls:
            print(f"\n测试URL: {test_url}")
            
            # 构建API请求
            api_url = "http://localhost:80/api/download"
            params = {
                "url": test_url,
                "with_watermark": "false",
                "prefix": "true"
            }
            
            try:
                # 发送请求
                print(f"发送请求到: {api_url}?{httpx.Request('GET', api_url, params=params).url.query}")
                response = await client.get(api_url, params=params, timeout=60.0)
                
                # 打印响应
                print(f"响应状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                
                # 检查响应内容类型
                content_type = response.headers.get('content-type', '')
                print(f"Content-Type: {content_type}")
                
                if 'application/json' in content_type:
                    # 响应是JSON
                    try:
                        data = response.json()
                        print("成功解析JSON响应")
                        print(f"响应内容: {json.dumps(data, ensure_ascii=False)}")
                        
                        if response.status_code == 200:
                            if "无水印" in data:
                                print("✓ 无水印视频下载成功")
                                print(f"  视频链接: {data.get('无水印')}")
                            else:
                                print("⚠ 响应中未找到无水印视频链接")
                        else:
                            print(f"✗ 请求失败: {response.status_code}")
                            print(f"错误信息: {data.get('message', '未知错误')}")
                    except Exception as e:
                        print(f"解析JSON响应失败: {e}")
                else:
                    # 响应不是JSON，可能是视频数据或其他二进制数据
                    content_length = len(response.content)
                    print(f"响应内容长度: {content_length} 字节")
                    print("响应不是JSON，可能是视频数据或其他二进制数据")
                    
                    # 检查是否是视频文件
                    if content_length > 1024 * 1024:  # 大于1MB
                        print("✓ 可能是视频文件")
                    else:
                        # 尝试打印前100个字符
                        try:
                            preview = response.content[:100].decode('utf-8', errors='replace')
                            print(f"响应预览: {preview}...")
                        except Exception as e:
                            print(f"无法预览响应内容: {e}")
                    
            except Exception as e:
                print(f"✗ 请求异常: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bilibili_download())
