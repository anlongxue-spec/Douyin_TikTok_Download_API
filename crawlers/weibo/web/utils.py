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


class WeiBoIdFetcher:
    """微博ID获取器 (WeiBo ID Fetcher)"""

    @staticmethod
    def extract_weibo_id_from_url(url: str) -> Optional[str]:
        """
        从微博URL中提取微博ID
        Extract weibo ID from weibo URL
        
        Args:
            url (str): 微博URL
            
        Returns:
            Optional[str]: 微博ID，如果无法提取则返回None
        """
        # 定义正则表达式
        patterns = [
            # 移动端URL格式
            r"weibo\.cn/\d+/([\d]+)",
            r"m\.weibo\.cn/detail/([\d]+)",
            r"m\.weibo\.cn/status/([\d]+)",
            # PC端URL格式
            r"weibo\.com/\d+/([\w]+)",
            r"weibo\.com/\w+/([\d]+)",
            r"weibo\.com/u/\d+/([\d]+)",
        ]

        # 遍历所有正则表达式
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # 如果没有匹配到，尝试从URL参数中提取
        id_param = re.search(r"id=([\d]+)", url)
        if id_param:
            return id_param.group(1)

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
            # 数字ID格式
            r"weibo\.cn/u/([\d]+)",
            r"m\.weibo\.cn/u/([\d]+)",
            r"weibo\.com/u/([\d]+)",
            r"weibo\.com/([\d]+)",
            # 个性化域名格式
            r"weibo\.com/([a-zA-Z0-9_-]+)",
            r"m\.weibo\.cn/u/([a-zA-Z0-9_-]+)",
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
        return url

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL是否为有效的微博URL
        Validate if the URL is a valid weibo URL
        
        Args:
            url (str): URL
            
        Returns:
            bool: 如果是有效的微博URL则返回True，否则返回False
        """
        # 定义正则表达式
        pattern = r"^(https?://)?(www\.)?(m\.)?weibo\.(com|cn)/.*$"
        return bool(re.match(pattern, url))


class DataParser:
    """数据解析工具 (Data Parser)"""

    @staticmethod
    def extract_video_urls(data: Dict[str, Any]) -> Dict[str, str]:
        """
        从微博数据中提取视频URL
        Extract video URLs from weibo data
        
        Args:
            data (Dict[str, Any]): 微博数据
            
        Returns:
            Dict[str, str]: 包含不同质量视频URL的字典
        """
        video_urls = {}

        try:
            # 检查是否包含视频数据
            if "page_info" in data and "media_info" in data["page_info"]:
                media_info = data["page_info"]["media_info"]
                
                # 提取不同质量的视频URL
                if "stream_url_hd" in media_info:
                    video_urls["hd"] = media_info["stream_url_hd"]
                if "stream_url" in media_info:
                    video_urls["sd"] = media_info["stream_url"]
                if "mp4_720p_mp4" in media_info:
                    video_urls["720p"] = media_info["mp4_720p_mp4"]
                if "mp4_hd_mp4" in media_info:
                    video_urls["hd"] = media_info["mp4_hd_mp4"]
                if "mp4_sd_mp4" in media_info:
                    video_urls["sd"] = media_info["mp4_sd_mp4"]
            # 检查是否包含video数据
            elif "video" in data:
                video = data["video"]
                if "stream_url" in video:
                    video_urls["sd"] = video["stream_url"]
        except Exception as e:
            print(f"提取视频URL时出错: {e}")

        return video_urls

    @staticmethod
    def extract_images(data: Dict[str, Any]) -> list:
        """
        从微博数据中提取图片URL
        Extract image URLs from weibo data
        
        Args:
            data (Dict[str, Any]): 微博数据
            
        Returns:
            list: 图片URL列表
        """
        images = []

        try:
            # 检查是否包含图片数据
            if "pics" in data:
                for pic in data["pics"]:
                    if "large" in pic:
                        images.append(pic["large"]["url"])
                    else:
                        images.append(pic["url"])
            # 检查是否包含page_info
            elif "page_info" in data and "pics" in data["page_info"]:
                for pic in data["page_info"]["pics"]:
                    if "large" in pic:
                        images.append(pic["large"]["url"])
                    else:
                        images.append(pic["url"])
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
            # 检查是否包含user数据
            if "user" in data:
                user = data["user"]
                user_info = {
                    "id": user.get("id"),
                    "screen_name": user.get("screen_name"),
                    "name": user.get("name"),
                    "description": user.get("description"),
                    "profile_image_url": user.get("profile_image_url"),
                    "profile_url": user.get("profile_url"),
                    "followers_count": user.get("followers_count"),
                    "friends_count": user.get("friends_count"),
                    "statuses_count": user.get("statuses_count"),
                    "favourites_count": user.get("favourites_count"),
                    "verified": user.get("verified"),
                    "verified_reason": user.get("verified_reason"),
                    "gender": user.get("gender"),
                    "created_at": user.get("created_at"),
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
            # 基本信息
            video_info["id"] = data.get("id")
            video_info["mid"] = data.get("mid")
            video_info["text"] = data.get("text")
            video_info["created_at"] = data.get("created_at")
            video_info["source"] = data.get("source")
            video_info["attitudes_count"] = data.get("attitudes_count")
            video_info["comments_count"] = data.get("comments_count")
            video_info["reposts_count"] = data.get("reposts_count")

            # 用户信息
            video_info["user"] = DataParser.parse_user_data(data)

            # 视频URL
            video_info["video_urls"] = DataParser.extract_video_urls(data)

            # 图片URL
            video_info["images"] = DataParser.extract_images(data)

        except Exception as e:
            print(f"解析视频数据时出错: {e}")

        return video_info