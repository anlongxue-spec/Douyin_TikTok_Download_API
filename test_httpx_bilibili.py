import httpx
import asyncio

# 测试的B站视频资源URL
url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/07/99/35182479907/35182479907-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&oi=1928713262&nbs=1&uipk=5&os=estgoss&og=ali&platform=pc&trid=c4220326fee94eb4881ab3144442524u&mid=1563114089&deadline=1768120119&gen=playurlv3&upsig=dac3e6e2f2b865b8f948234e50e9c359&uparams=e,oi,nbs,uipk,os,og,platform,trid,mid,deadline,gen&bvc=vod&nettype=0&bw=926070&f=u_0_0&qn_dyeid=22af4d47587cc89d002dbee669634317&agrr=1&buvid=439EB233-5D03-3E32-702A-5CB95A60614A57594infoc&build=0&dl=0&orderid=0,3"

# 读取B站的配置文件
import yaml
import os
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawlers', 'bilibili', 'web', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# 获取B站的请求头
bili_headers = config['TokenManager']['bilibili']['headers']

# 测试不同的请求方式
async def test_bilibili_url():
    # 测试1: 不使用请求头
    print("\n测试1: 不使用请求头")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url, timeout=10, follow_redirects=True)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                print("  ✓ 成功访问")
            else:
                print(f"  ✗ 访问失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")
    
    # 测试2: 使用B站的请求头
    print("\n测试2: 使用B站的请求头")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url, headers=bili_headers, timeout=10, follow_redirects=True)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                print("  ✓ 成功访问")
                # 检查Content-Length
                if "content-length" in response.headers:
                    print(f"  内容长度: {response.headers['content-length']} 字节")
            else:
                print(f"  ✗ 访问失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")
    
    # 测试3: 使用流式请求（模拟服务器端行为）
    print("\n测试3: 使用流式请求")
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, headers=bili_headers, timeout=10) as response:
                print(f"  状态码: {response.status_code}")
                if response.status_code == 200:
                    print("  ✓ 成功访问")
                    # 读取前几个字节
                    first_chunk = await response.aiter_bytes().__anext__()
                    print(f"  接收到的第一个数据块大小: {len(first_chunk)} 字节")
                else:
                    print(f"  ✗ 访问失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")
    
    # 测试4: 模拟fetch_data_stream函数的行为
    print("\n测试4: 模拟fetch_data_stream函数的行为")
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, headers=bili_headers, timeout=10) as response:
                print(f"  状态码: {response.status_code}")
                if response.status_code != 200:
                    print(f"  ✗ 访问失败: 状态码 {response.status_code}")
                    return
                
                # 读取前10KB数据
                total_bytes = 0
                async for chunk in response.aiter_bytes():
                    total_bytes += len(chunk)
                    if total_bytes > 10240:  # 只读取前10KB
                        break
                
                print(f"  ✓ 成功读取 {total_bytes} 字节数据")
                print("  模拟fetch_data_stream函数成功")
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_bilibili_url())
