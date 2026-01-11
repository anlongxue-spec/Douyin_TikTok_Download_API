import requests
import time

# 测试的B站视频资源URL
url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/07/99/35182479907/35182479907-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&oi=1928713262&nbs=1&uipk=5&os=estgoss&og=ali&platform=pc&trid=c4220326fee94eb4881ab3144442524u&mid=1563114089&deadline=1768120119&gen=playurlv3&upsig=dac3e6e2f2b865b8f948234e50e9c359&uparams=e,oi,nbs,uipk,os,og,platform,trid,mid,deadline,gen&bvc=vod&nettype=0&bw=926070&f=u_0_0&qn_dyeid=22af4d47587cc89d002dbee669634317&agrr=1&buvid=439EB233-5D03-3E32-702A-5CB95A60614A57594infoc&build=0&dl=0&orderid=0,3"

# 检查URL是否过期
deadline = 1768120119
current_time = time.time()
print(f"URL过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(deadline))}")
print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")
print(f"URL是否过期: {current_time > deadline}")

# 测试1: 不使用请求头
print("\n测试1: 不使用请求头访问")
try:
    response = requests.get(url, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)[:5]}")
    print(f"响应内容长度: {len(response.content)} 字节")
except Exception as e:
    print(f"请求失败: {e}")

# 测试2: 使用B站的请求头
print("\n测试2: 使用B站的请求头访问")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Origin": "https://www.bilibili.com",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)[:5]}")
    print(f"响应内容长度: {len(response.content)} 字节")
except Exception as e:
    print(f"请求失败: {e}")

# 测试3: 检查URL参数
print("\n测试3: 检查URL参数")
print(f"URL长度: {len(url)}")
print(f"URL包含必要参数: {'e=' in url and 'oi=' in url and 'upsig=' in url}")
