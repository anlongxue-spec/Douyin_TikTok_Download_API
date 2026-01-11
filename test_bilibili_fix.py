import asyncio
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.endpoints.download import fetch_data_stream
from fastapi import Request

class MockRequest:
    """模拟 FastAPI Request 对象"""
    async def is_disconnected(self):
        return False

async def test_bilibili_download():
    # 测试的B站视频资源URL
    url = "https://upos-sz-estgoss.bilivideo.com/upgcxcode/07/99/35182479907/35182479907-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&oi=1928713262&nbs=1&uipk=5&os=estgoss&og=ali&platform=pc&trid=c4220326fee94eb4881ab3144442524u&mid=1563114089&deadline=1768120119&gen=playurlv3&upsig=dac3e6e2f2b865b8f948234e50e9c359&uparams=e,oi,nbs,uipk,os,og,platform,trid,mid,deadline,gen&bvc=vod&nettype=0&bw=926070&f=u_0_0&qn_dyeid=22af4d47587cc89d002dbee669634317&agrr=1&buvid=439EB233-5D03-3E32-702A-5CB95A60614A57594infoc&build=0&dl=0&orderid=0,3"
    
    # 读取B站的配置文件
    import yaml
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawlers', 'bilibili', 'web', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    # 获取B站的请求头
    headers = config['TokenManager']['bilibili']['headers']
    
    # 创建临时文件
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix='.m4s', delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    
    try:
        # 测试下载
        print("开始测试B站视频资源下载...")
        print(f"URL: {url}")
        print(f"临时文件: {temp_file_path}")
        
        mock_request = MockRequest()
        success = await fetch_data_stream(url, mock_request, headers=headers, file_path=temp_file_path)
        
        if success:
            print("\n✓ 下载成功！")
            
            # 验证文件
            if os.path.exists(temp_file_path):
                file_size = os.path.getsize(temp_file_path)
                print(f"  文件大小: {file_size} 字节")
                if file_size > 0:
                    print("  文件不为空")
                else:
                    print("  文件为空")
        else:
            print("\n✗ 下载失败！")
            
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"\n清理临时文件: {temp_file_path}")

if __name__ == "__main__":
    asyncio.run(test_bilibili_download())
