#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试FFmpeg在微信云托管环境中的集成
"""

import os
import subprocess
import sys


def test_ffmpeg_cloud_integration():
    """
    测试微信云托管环境中的FFmpeg集成
    """
    print("=== 测试微信云托管环境中的FFmpeg集成 ===")
    
    # 统一使用绝对路径 "/usr/bin/ffmpeg"（微信云托管环境）
    ffmpeg_path = "/usr/bin/ffmpeg"
    print(f"Using FFmpeg path for WeChat Cloud Hosting: {ffmpeg_path}")
    
    # 验证FFmpeg路径是否存在
    if not os.path.exists(ffmpeg_path):
        print(f"ERROR: FFmpeg path does not exist: {ffmpeg_path}")
        print(f"Please ensure FFmpeg is installed in the cloud hosting environment")
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
    
    print(f"Final FFmpeg path: {ffmpeg_path}")
    print("FFmpeg integration test passed!")
    return True


if __name__ == "__main__":
    success = test_ffmpeg_cloud_integration()
    sys.exit(0 if success else 1)
