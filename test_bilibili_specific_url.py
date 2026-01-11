import asyncio
import httpx
import aiofiles
import os
import tempfile

# 测试特定的Bilibili资源URL
test_url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/07/99/35182479907/35182479907-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&oi=1928713262&nbs=1&uipk=5&os=estgoss&og=ali&platform=pc&trid=c4220326fee94eb4881ab3144442524u&mid=1563114089&deadline=1768120119&gen=playurlv3&upsig=dac3e6e2f2b865b8f948234e50e9c359&uparams=e,oi,nbs,uipk,os,og,platform,trid,mid,deadline,gen&bvc=vod&nettype=0&bw=926070&f=u_0_0&qn_dyeid=22af4d47587cc89d002dbee669634317&agrr=1&buvid=439EB233-5D03-3E32-702A-5CB95A60614A57594infoc&build=0&dl=0&orderid=0,3"

# Bilibili请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/',
    'Origin': 'https://www.bilibili.com'
}

async def test_specific_url_download():
    print(f"测试URL: {test_url}")
    print(f"请求头: {headers}")
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        try:
            # 先发送HEAD请求获取文件信息
            head_response = await client.head(test_url, headers=headers)
            print(f"\nHEAD请求状态码: {head_response.status_code}")
            print(f"HEAD响应头: {dict(head_response.headers)}")
            
            # 获取Content-Length
            content_length = head_response.headers.get('content-length')
            if content_length:
                print(f"预期文件大小: {int(content_length)} 字节")
            
            # 发送GET请求下载文件
            print("\n开始下载文件...")
            async with client.stream('GET', test_url, headers=headers) as response:
                response.raise_for_status()
                print(f"GET请求状态码: {response.status_code}")
                
                # 创建临时文件
                temp_dir = tempfile.gettempdir()
                file_name = os.path.basename(test_url.split('?')[0])
                temp_file_path = os.path.join(temp_dir, file_name)
                
                # 写入文件
                total_bytes = 0
                async with aiofiles.open(temp_file_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await f.write(chunk)
                        total_bytes += len(chunk)
                        print(f"已下载: {total_bytes} 字节", end='\r')
                
                print(f"\n\n下载完成，实际大小: {total_bytes} 字节")
                
                # 验证文件完整性
                if os.path.exists(temp_file_path):
                    actual_size = os.path.getsize(temp_file_path)
                    print(f"文件系统中大小: {actual_size} 字节")
                    
                    if content_length:
                        expected_size = int(content_length)
                        size_diff = abs(actual_size - expected_size)
                        print(f"大小差异: {size_diff} 字节")
                        
                        if size_diff <= 1024:
                            print("✓ 文件大小在容错范围内")
                        else:
                            print(f"✗ 文件大小差异过大: {size_diff} 字节 > 1024 字节")
                    else:
                        print("⚠ 无法获取预期文件大小")
                    
                    # 检查文件是否为空
                    if actual_size == 0:
                        print("✗ 下载的文件为空")
                    else:
                        print(f"✓ 文件下载成功，大小: {actual_size} 字节")
                else:
                    print("✗ 文件未下载成功")
                
                # 清理临时文件
                try:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                        print("✓ 临时文件已清理")
                except Exception as e:
                    print(f"⚠ 清理临时文件失败: {e}")
                    
        except httpx.HTTPStatusError as e:
            print(f"✗ HTTP错误: {e.response.status_code} - {e.response.reason_phrase}")
            print(f"响应头: {dict(e.response.headers)}")
        except httpx.RequestError as e:
            print(f"✗ 请求错误: {e}")
        except asyncio.TimeoutError:
            print(f"✗ 请求超时")
        except Exception as e:
            print(f"✗ 未知错误: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_specific_url_download())
