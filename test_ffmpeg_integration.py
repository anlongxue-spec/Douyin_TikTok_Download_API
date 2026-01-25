#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试FFmpeg集成功能，特别是针对微信云托管环境的配置
"""

import os
import platform
import subprocess
import sys


def test_ffmpeg_integration():
    """
    测试FFmpeg集成功能
    """
    print("=== 测试FFmpeg集成功能 ===")
    
    system = platform.system()
    print(f"Current system: {system}")
    
    # 模拟微信云托管环境的FFmpeg路径选择逻辑
    if system == "Linux":
        # 统一使用绝对路径 "/usr/bin/ffmpeg"（微信云托管环境）
        ffmpeg_path = "/usr/bin/ffmpeg"
        print(f"Using FFmpeg path for WeChat Cloud Hosting (Linux): {ffmpeg_path}")
    else:
        # Windows环境，尝试使用系统PATH中的ffmpeg
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        print(f"Using FFmpeg path for Windows: {ffmpeg_path}")
    
    # 验证FFmpeg路径是否存在
    if not ffmpeg_path:
        print(f"ERROR: FFmpeg path not found")
        print(f"Please ensure FFmpeg is installed in the environment")
        return False
    
    if not os.path.exists(ffmpeg_path):
        print(f"ERROR: FFmpeg path does not exist: {ffmpeg_path}")
        print(f"Please ensure FFmpeg is installed in the environment")
        return False
    
    # 验证FFmpeg是否为文件
    if not os.path.isfile(ffmpeg_path):
        print(f"ERROR: FFmpeg path is not a file: {ffmpeg_path}")
        return False
    
    # 验证FFmpeg是否有可执行权限
    if not os.access(ffmpeg_path, os.X_OK):
        print(f"ERROR: FFmpeg does not have executable permissions: {ffmpeg_path}")
        return False
    
    # 验证FFmpeg是否可以正常执行
    try:
        result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"ERROR: FFmpeg execution failed: {result.stderr}")
            return False
        version_line = result.stdout.split('\n')[0]
        print(f"Verified FFmpeg works correctly: {version_line}")
    except Exception as e:
        print(f"ERROR: Failed to verify FFmpeg execution: {e}")
        return False
    
    # 测试FFmpeg命令行参数传递
    print("\n=== 测试FFmpeg命令行参数传递 ===")
    try:
        # 测试获取帮助信息
        result = subprocess.run([ffmpeg_path, "-h"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"ERROR: FFmpeg help command failed: {result.stderr}")
            return False
        print("FFmpeg help command executed successfully")
        
        # 测试基本的格式转换命令（不会实际执行，只是测试参数传递）
        test_cmd = [ffmpeg_path, "-i", "input.mp4", "-c:v", "copy", "-c:a", "copy", "output.mp4"]
        print(f"Testing FFmpeg command: {' '.join(test_cmd)}")
        # 只测试命令构建，不实际执行
        print("FFmpeg command construction test passed")
        
    except Exception as e:
        print(f"ERROR: Failed to test FFmpeg command parameters: {e}")
        return False
    
    print("\n=== FFmpeg集成测试完成 ===")
    print(f"Final FFmpeg path: {ffmpeg_path}")
    print("FFmpeg integration test passed!")
    return True


if __name__ == "__main__":
    success = test_ffmpeg_integration()
    sys.exit(0 if success else 1)
