# ==============================================================================
# Copyright (C) 2021 Evil0ctal
#
# This file is part of the Douyin_TikTok_Download_API project.
#
# This project is licensed under the Apache License 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


import re
from typing import Optional, Dict, Any


class VideoIdFetcher:
    """视频ID获取器 (Video ID Fetcher)"""

    @staticmethod
    def extract_video_id_from_url(url: str) -> Optional[str]:
        """
        从皮皮虾URL中提取视频ID
        Extract video ID from PiPiXia URL
        
        Args:
            url (str): 皮皮虾视频URL
            
        Returns:
            Optional[str]: 视频ID，如果无法提取则返回None
        """
        # 定义正则表达式
        patterns = [
            # H5页面URL格式
            r"pipix\.com/item/video/([\w-]+)",
            r"h5\.pipix\.com/item/video/([\w-]+)",
            r"h5\.pipix\.com/s/([\w-]+)",
            r"pipix\.com/s/([\w-]+)",
            # 分享链接格式
            r"share\.pipix\.com/s/([\w-]+)",
            r"share\.pipix\.com/video/([\w-]+)",
            r"pipixshare\.com/s/([\w-]+)",
            # URL参数格式
            r"aweme_id=([\w-]+)",
            r"video_id=([\w-]+)",
        ]

        # 遍历所有正则表达式
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None


class UserIdFetcher:
    """用户ID获取器 (User ID Fetcher)"""

    @staticmethod
    def extract_user_id_from_url(url: str) -> Optional[str]:
        """
        从用户主页URL中提取用户ID
        Extract user ID from user profile URL
        
        Args:
            url (str): 用户主页URL
            
        Returns:
            Optional[str]: 用户ID，如果无法提取则返回None
        """
        # 定义正则表达式
        patterns = [
            # 用户主页URL格式
            r"pipix\.com/user/profile/([\w-]+)",
            r"h5\.pipix\.com/user/profile/([\w-]+)",
            r"h5\.pipix\.com/u/([\w-]+)",
            r"pipix\.com/u/([\w-]+)",
            # URL参数格式
            r"user_id=([\w-]+)",
            r"uid=([\w-]+)",
        ]

        # 遍历所有正则表达式
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None


class URLUtils:
    """URL工具类 (URL Utilities)"""

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        标准化URL
        Normalize URL
        
        Args:
            url (str): 原始URL
            
        Returns:
            str: 标准化后的URL
        """
        # 移除URL中的多余参数
        url = re.sub(r"(&_t=\d+")|(&_t=\d+)|(_t=\d+)", "", url)
        # 移除URL末尾的斜杠
        url = url.rstrip("/")
        # 将短链接转换为标准链接
        url = re.sub(r"pipixshare\.com", "share.pipix.com", url)
        return url

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL是否为有效的皮皮虾URL
        Validate if the URL is a valid PiPiXia URL
        
        Args:
            url (str): URL
            
        Returns:
            bool: 如果是有效的皮皮虾URL则返回True，否则返回False
        """
        # 定义正则表达式
        pattern = r"^(https?://)?(h5\.)?(share\.)?(pipixshare\.)?pipix\.(com|cn)/.*$"
        return bool(re.match(pattern, url))


class DataParser:
    """数据解析工具 (Data Parser)"""

    @staticmethod
    def extract_video_urls(data: Dict[str, Any]) -> Dict[str, str]:
        """
        从皮皮虾数据中提取视频URL
        Extract video URLs from PiPiXia data
        
        Args:
            data (Dict[str, Any]): 皮皮虾数据
            
        Returns:
            Dict[str, str]: 包含不同质量视频URL的字典
        """
        video_urls = {}

        try:
            # 检查是否包含视频数据
            if "aweme_detail" in data:
                aweme = data["aweme_detail"]
            elif "aweme" in data:
                aweme = data["aweme"]
            else:
                aweme = data

            # 提取视频播放地址
            if "video" in aweme and "play_addr" in aweme["video"]:
                play_addr = aweme["video"]["play_addr"]
                # 获取不同质量的视频URL
                if "url_list" in play_addr:
                    urls = play_addr["url_list"]
                    if urls:
                        # 通常第一个URL是最高质量
                        video_urls["hd"] = urls[0]
                        for i, url in enumerate(urls[1:], 1):
                            video_urls[f"quality_{i}"] = url

            # 检查是否有其他视频地址
            if "download_addr" in aweme.get("video", {}):
                download_addr = aweme["video"]["download_addr"]
                if "url_list" in download_addr:
                    video_urls["download"] = download_addr["url_list"][0]

        except Exception as e:
            print(f"提取视频URL时出错: {e}")

        return video_urls

    @staticmethod
    def extract_images(data: Dict[str, Any]) -> list:
        """
        从皮皮虾数据中提取图片URL
        Extract image URLs from PiPiXia data
        
        Args:
            data (Dict[str, Any]): 皮皮虾数据
            
        Returns:
            list: 图片URL列表
        """
        images = []

        try:
            # 检查是否包含图片数据
            if "aweme_detail" in data:
                aweme = data["aweme_detail"]
            elif "aweme" in data:
                aweme = data["aweme"]
            else:
                aweme = data

            # 检查是否为图片类型内容
            if aweme.get("aweme_type") == 2:  # 2表示图片类型
                if "images" in aweme:
                    for img in aweme["images"]:
                        if "url_list" in img:
                            # 获取最高质量的图片URL
                            images.append(img["url_list"][0])

        except Exception as e:
            print(f"提取图片URL时出错: {e}")

        return images

    @staticmethod
    def parse_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析用户数据
        Parse user data
        
        Args:
            data (Dict[str, Any]): 用户原始数据
            
        Returns:
            Dict[str, Any]: 解析后的用户数据
        """
        user_info = {}

        try:
            # 检查数据结构
            if "user" in data:
                user = data["user"]
            elif "user_info" in data:
                user = data["user_info"]
            elif "aweme_detail" in data and "author" in data["aweme_detail"]:
                user = data["aweme_detail"]["author"]
            else:
                user = data

            # 提取用户信息
            user_info = {
                "id": user.get("uid"),
                "short_id": user.get("short_id"),
                "unique_id": user.get("unique_id"),
                "nickname": user.get("nickname"),
                "avatar_url": user.get("avatar_thumb", {}).get("url_list", [""])[0],
                "signature": user.get("signature"),
                "following_count": user.get("following_count"),
                "follower_count": user.get("follower_count"),
                "total_favorited": user.get("total_favorited"),
                "aweme_count": user.get("aweme_count"),
                "favoriting_count": user.get("favoriting_count"),
                "verified": user.get("verified"),
                "verified_reason": user.get("verified_reason"),
            }
        except Exception as e:
            print(f"解析用户数据时出错: {e}")

        return user_info

    @staticmethod
    def parse_video_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析视频数据
        Parse video data
        
        Args:
            data (Dict[str, Any]): 视频原始数据
            
        Returns:
            Dict[str, Any]: 解析后的视频数据
        """
        video_info = {}

        try:
            # 检查数据结构
            if "aweme_detail" in data:
                aweme = data["aweme_detail"]
            elif "aweme" in data:
                aweme = data["aweme"]
            else:
                aweme = data

            # 基本信息
            video_info["id"] = aweme.get("aweme_id")
            video_info["short_id"] = aweme.get("short_id")
            video_info["desc"] = aweme.get("desc")
            video_info["create_time"] = aweme.get("create_time")
            video_info["duration"] = aweme.get("video", {}).get("duration")
            video_info["cover_url"] = aweme.get("video", {}).get("cover", {}).get("url_list", [""])[0]
            video_info["width"] = aweme.get("video", {}).get("width")
            video_info["height"] = aweme.get("video", {}).get("height")

            # 统计信息
            video_info["statistics"] = {
                "digg_count": aweme.get("statistics", {}).get("digg_count"),
                "share_count": aweme.get("statistics", {}).get("share_count"),
                "comment_count": aweme.get("statistics", {}).get("comment_count"),
                "play_count": aweme.get("statistics", {}).get("play_count"),
                "collect_count": aweme.get("statistics", {}).get("collect_count"),
            }

            # 用户信息
            video_info["author"] = DataParser.parse_user_data(aweme)

            # 视频URL
            video_info["video_urls"] = DataParser.extract_video_urls(aweme)

            # 图片URL (如果是图片类型)
            video_info["images"] = DataParser.extract_images(aweme)

            # 音乐信息
            if "music" in aweme:
                music = aweme["music"]
                video_info["music"] = {
                    "id": music.get("id"),
                    "title": music.get("title"),
                    "author": music.get("author"),
                    "play_url": music.get("play_url", {}).get("url_list", [""])[0],
                    "cover_url": music.get("cover_thumb", {}).get("url_list", [""])[0],
                }

        except Exception as e:
            print(f"解析视频数据时出错: {e}")

        return video_info