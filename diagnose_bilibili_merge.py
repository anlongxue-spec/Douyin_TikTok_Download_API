import asyncio
import os
import subprocess
import tempfile
import httpx

from crawlers.hybrid.hybrid_crawler import HybridCrawler

HybridCrawler = HybridCrawler()

async def diagnose_bilibili_merge():
    """诊断Bilibili音视频合并失败的原因"""
    
    # 测试链接
    test_url = "https://b23.tv/UzSQvAW"
    print(f"诊断测试链接: {test_url}")
    
    try:
        # 步骤1: 解析视频数据
        print("\n步骤1: 解析视频数据...")
        data = await HybridCrawler.hybrid_parsing_single_video(test_url, minimal=False)
        platform = data.get('platform')
        video_data = data.get('video_data', {})
        
        if platform != 'bilibili':
            print(f"❌ 视频平台不是Bilibili: {platform}")
            return
        
        print(f"✅ 平台: {platform}")
        print(f"✅ 视频数据获取成功")
        
        # 步骤2: 获取视频和音频URL
        print("\n步骤2: 获取视频和音频URL...")
        video_url = video_data.get('nwm_video_url_HQ')
        audio_url = video_data.get('audio_url')
        
        print(f"视频URL: {video_url[:100]}...")
        print(f"音频URL: {audio_url[:100]}...")
        
        if not video_url:
            print("❌ 未找到无水印视频URL")
            return
        if not audio_url:
            print("❌ 未找到音频URL")
            return
        
        # 步骤3: 测试视频下载
        print("\n步骤3: 测试视频下载...")
        headers = await HybridCrawler.BilibiliWebCrawler.get_bilibili_headers()
        headers = headers['headers']
        
        async def test_download(url, file_path, desc):
            """测试单个文件下载"""
            try:
                print(f"开始下载{desc}...")
                async with httpx.AsyncClient(timeout=httpx.Timeout(30.0), follow_redirects=True) as client:
                    async with client.stream('GET', url, headers=headers) as response:
                        response.raise_for_status()
                        
                        total_bytes = 0
                        async with open(file_path, 'wb') as f:
                            async for chunk in response.aiter_bytes(chunk_size=8192):
                                await f.write(chunk)
                                total_bytes += len(chunk)
                                print(f"已下载: {total_bytes} 字节", end='\r')
                        
                        print(f"\n✅ {desc}下载成功，大小: {total_bytes} 字节")
                        return True
            except Exception as e:
                print(f"\n❌ {desc}下载失败: {e}")
                return False
        
        # 创建临时目录
        temp_dir = tempfile.gettempdir()
        video_temp_path = os.path.join(temp_dir, "test_video.m4v")
        audio_temp_path = os.path.join(temp_dir, "test_audio.m4a")
        output_path = os.path.join(temp_dir, "test_output.mp4")
        
        print(f"临时视频文件: {video_temp_path}")
        print(f"临时音频文件: {audio_temp_path}")
        print(f"输出文件: {output_path}")
        
        # 下载视频和音频
        video_downloaded = await test_download(video_url, video_temp_path, "视频")
        audio_downloaded = await test_download(audio_url, audio_temp_path, "音频")
        
        if not video_downloaded or not audio_downloaded:
            print("❌ 下载失败，无法继续测试")
            return
        
        # 步骤4: 检查FFmpeg
        print("\n步骤4: 检查FFmpeg...")
        
        # 尝试多种方式获取FFmpeg路径
        ffmpeg_path = None
        
        # 方法1: 从配置文件获取
        try:
            import yaml
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                ffmpeg_path = config.get('API').get('FFmpeg_Path')
                print(f"配置文件中的FFmpeg路径: {ffmpeg_path}")
        except Exception as e:
            print(f"从配置文件获取FFmpeg路径失败: {e}")
        
        # 方法2: 使用硬编码路径
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            ffmpeg_path = r"C:\Program Files (x86)\iflyrecClient\resources\tj_B1\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
            print(f"尝试硬编码FFmpeg路径: {ffmpeg_path}")
        
        # 方法3: 检查系统环境变量
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            try:
                result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True)
                if result.returncode == 0:
                    ffmpeg_path = result.stdout.strip().split('\n')[0]
                    print(f"从系统环境变量获取FFmpeg路径: {ffmpeg_path}")
            except Exception as e:
                print(f"从系统环境变量获取FFmpeg路径失败: {e}")
        
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            print("❌ 未找到FFmpeg可执行文件")
            return
        
        print(f"✅ FFmpeg路径: {ffmpeg_path}")
        
        # 测试FFmpeg版本
        try:
            result = subprocess.run([ffmpeg_path, '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                # 修复f-string反斜杠语法错误
                version_output = result.stdout.splitlines()[0]
                print(f"FFmpeg版本: {version_output}")
            else:
                # 修复f-string反斜杠语法错误
                stderr_output = result.stderr.splitlines()[0]
                print(f"FFmpeg版本检查失败: {stderr_output}")
        except Exception as e:
            print(f"FFmpeg版本检查异常: {e}")
            return
        
        # 步骤5: 测试FFmpeg合并
        print("\n步骤5: 测试FFmpeg合并...")
        
        ffmpeg_cmd = [
            ffmpeg_path, '-y',
            '-i', video_temp_path,
            '-i', audio_temp_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'mp4',
            output_path
        ]
        
        print(f"执行FFmpeg命令: {' '.join(ffmpeg_cmd)}")
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
            print(f"\nFFmpeg返回码: {result.returncode}")
            
            if result.stdout:
                print(f"FFmpeg stdout: {result.stdout}")
            if result.stderr:
                print(f"FFmpeg stderr: {result.stderr}")
            
            if result.returncode == 0:
                print("\n✅ FFmpeg合并成功")
                if os.path.exists(output_path):
                    output_size = os.path.getsize(output_path)
                    print(f"输出文件大小: {output_size} 字节")
            else:
                print("\n❌ FFmpeg合并失败")
        except subprocess.TimeoutExpired:
            print("\n❌ FFmpeg执行超时")
        except Exception as e:
            print(f"\n❌ FFmpeg执行异常: {e}")
        
        # 清理临时文件
        print("\n清理临时文件...")
        for file_path in [video_temp_path, audio_temp_path, output_path]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
        
        print("\n诊断完成")
        
    except Exception as e:
        print(f"\n❌ 诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_bilibili_merge())
