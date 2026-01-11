import requests

# 测试的B站视频资源URL
url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/07/99/35182479907/35182479907-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&oi=1928713262&nbs=1&uipk=5&os=estgoss&og=ali&platform=pc&trid=c4220326fee94eb4881ab3144442524u&mid=1563114089&deadline=1768120119&gen=playurlv3&upsig=dac3e6e2f2b865b8f948234e50e9c359&uparams=e,oi,nbs,uipk,os,og,platform,trid,mid,deadline,gen&bvc=vod&nettype=0&bw=926070&f=u_0_0&qn_dyeid=22af4d47587cc89d002dbee669634317&agrr=1&buvid=439EB233-5D03-3E32-702A-5CB95A60614A57594infoc&build=0&dl=0&orderid=0,3"

# 测试不同的Referer值
test_referers = [
    # 空Referer
    None,
    # 配置文件中的Referer
    "https://space.bilibili.com/",
    # 通用B站Referer
    "https://www.bilibili.com/",
    # 具体视频页面的Referer
    "https://www.bilibili.com/video/BV1E8ijBeEvx/",
    # 其他网站的Referer
    "https://www.example.com/"
]

# 基础请求头
base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

for i, referer in enumerate(test_referers):
    print(f"\n测试 {i+1}: Referer = {referer}")
    
    # 复制基础请求头
    headers = base_headers.copy()
    
    # 添加Referer（如果有）
    if referer:
        headers["Referer"] = referer
    
    try:
        # 发送HEAD请求，只获取响应头
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✓ 成功访问")
            # 检查Content-Length
            if "Content-Length" in response.headers:
                print(f"  内容长度: {response.headers['Content-Length']} 字节")
        else:
            print(f"  ✗ 访问失败: 状态码 {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")
