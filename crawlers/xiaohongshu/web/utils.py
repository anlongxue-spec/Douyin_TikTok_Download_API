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


class NoteIdFetcher:
    """小红书笔记ID获取器 (XiaoHongShu Note ID Fetcher)"""
    
    @staticmethod
    def extract_note_id_from_url(url: str) -> str:
        """
        从小红书笔记URL中提取note_id
        Extract note_id from XiaoHongShu note URL
        
        Args:
            url (str): 小红书笔记URL
            
        Returns:
            str: 提取到的note_id
        """
        # 匹配小红书笔记URL的正则表达式
        patterns = [
            r"explore/([a-zA-Z0-9-]+)",  # 标准格式
            r"note/([a-zA-Z0-9-]+)",  # 另一种格式
            r"([a-zA-Z0-9-]{32})"  # 直接匹配32位字符的note_id
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""


class UserIdFetcher:
    """小红书用户ID获取器 (XiaoHongShu User ID Fetcher)"""
    
    @staticmethod
    def extract_user_id_from_url(url: str) -> str:
        """
        从小红书用户主页URL中提取user_id
        Extract user_id from XiaoHongShu user homepage URL
        
        Args:
            url (str): 小红书用户主页URL
            
        Returns:
            str: 提取到的user_id
        """
        # 匹配小红书用户主页URL的正则表达式
        pattern = r"user/profile/([a-zA-Z0-9-]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return ""


class URLUtils:
    """URL工具类 (URL Utilities Class)"""
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        标准化小红书URL
        Normalize XiaoHongShu URL
        
        Args:
            url (str): 原始URL
            
        Returns:
            str: 标准化后的URL
        """
        # 移除可能的参数
        url = re.sub(r"\?.*$", "", url)
        # 确保URL以/结尾
        if not url.endswith("/"):
            url = url + r"/"
        return url

    @staticmethod
    def is_valid_note_url(url: str) -> bool:
        """
        检查是否为有效的小红书笔记URL
        Check if it's a valid XiaoHongShu note URL
        
        Args:
            url (str): 待检查的URL
            
        Returns:
            bool: 是否为有效的笔记URL
        """
        patterns = [
            r"^https?://www\.xiaohongshu\.com/explore/",
            r"^https?://www\.xiaohongshu\.com/note/",
            r"^https?://xhslink\.com/"
        ]
        
        for pattern in patterns:
            if re.match(pattern, url):
                return True
        return False

    @staticmethod
    def is_valid_user_url(url: str) -> bool:
        """
        检查是否为有效的小红书用户URL
        Check if it's a valid XiaoHongShu user URL
        
        Args:
            url (str): 待检查的URL
            
        Returns:
            bool: 是否为有效的用户URL
        """
        pattern = r"^https?://www\.xiaohongshu\.com/user/profile/"
        return re.match(pattern, url) is not None


class DataParser:
    """数据解析工具类 (Data Parser Utility Class)"""
    
    @staticmethod
    def parse_video_url(data: dict) -> str:
        """
        从笔记数据中解析视频URL
        Parse video URL from note data
        
        Args:
            data (dict): 笔记数据
            
        Returns:
            str: 视频URL
        """
        if "note" in data:
            note = data["note"]
            if "video" in note and "media" in note["video"]:
                return note["video"]["media"]["stream"]
        return ""

    @staticmethod
    def parse_image_urls(data: dict) -> list:
        """
        从笔记数据中解析图片URL列表
        Parse image URLs from note data
        
        Args:
            data (dict): 笔记数据
            
        Returns:
            list: 图片URL列表
        """
        urls = []
        if "note" in data:
            note = data["note"]
            if "images" in note:
                for img in note["images"]:
                    if "url" in img:
                        urls.append(img["url"])
        return urls