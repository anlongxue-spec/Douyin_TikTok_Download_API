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


import asyncio  # 异步I/O
import os  # 系统操作
import yaml  # 配置文件
from urllib.parse import urlencode  # URL编码

# 基础爬虫客户端和小红书API端点
from crawlers.base_crawler import BaseCrawler
from crawlers.xiaohongshu.web.endpoints import XiaoHongShuAPIEndpoints
# 小红书接口数据请求模型
from crawlers.xiaohongshu.web.models import (
    BaseRequestModel, UserProfile, UserNotes,
    UserLikes, NoteDetail, NoteComments, SearchNotes
)
# 小红书应用的工具类
from crawlers.xiaohongshu.web.utils import (
    NoteIdFetcher,  # 笔记ID获取
    UserIdFetcher,  # 用户ID获取
    URLUtils,  # URL工具类
    DataParser  # 数据解析工具
)

# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class XiaoHongShuWebCrawler:
    """小红书网页版爬虫类 (XiaoHongShu Web Crawler Class)"""

    # 从配置文件中获取小红书的请求头
    async def get_xiaohongshu_headers(self):
        """
        获取小红书的请求头
        Get XiaoHongShu request headers
        
        Returns:
            dict: 包含headers和proxies的字典
        """
        xiaohongshu_config = config["TokenManager"]["xiaohongshu"]
        kwargs = {
            "headers": {
                "Accept-Language": xiaohongshu_config["headers"]["Accept-Language"],
                "User-Agent": xiaohongshu_config["headers"]["User-Agent"],
                "Referer": xiaohongshu_config["headers"]["Referer"],
                "Cookie": xiaohongshu_config["headers"]["Cookie"],
                "Content-Type": "application/json",
                "Origin": "https://www.xiaohongshu.com"
            },
            "proxies": {"http://": xiaohongshu_config["proxies"]["http"], "https://": xiaohongshu_config["proxies"]["https"]},
        }
        return kwargs

    # 获取单个笔记数据
    async def fetch_one_note(self, note_id: str):
        """
        获取单个笔记数据
        Get single note data
        
        Args:
            note_id (str): 笔记ID
            
        Returns:
            dict: 笔记数据
        """
        # 获取小红书的请求头
        kwargs = await self.get_xiaohongshu_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求参数
            params = NoteDetail(note_id=note_id).dict()
            
            # 构建请求URL
            endpoint = f"{XiaoHongShuAPIEndpoints.NOTE_INFO}?{urlencode(params)}"
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取用户资料
    async def fetch_user_profile(self, user_id: str):
        """
        获取用户资料
        Get user profile data
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            dict: 用户资料数据
        """
        # 获取小红书的请求头
        kwargs = await self.get_xiaohongshu_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求参数
            params = UserProfile(user_id=user_id).dict()
            
            # 构建请求URL
            endpoint = f"{XiaoHongShuAPIEndpoints.USER_INFO}?{urlencode(params)}"
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取用户笔记数据
    async def fetch_user_notes(self, user_id: str, cursor: str = "", limit: int = 20):
        """
        获取用户笔记数据
        Get user notes data
        
        Args:
            user_id (str): 用户ID
            cursor (str): 分页游标
            limit (int): 每页数量
            
        Returns:
            dict: 用户笔记数据
        """
        # 获取小红书的请求头
        kwargs = await self.get_xiaohongshu_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求参数
            params = UserNotes(user_id=user_id, cursor=cursor, limit=limit).dict()
            
            # 构建请求URL
            endpoint = f"{XiaoHongShuAPIEndpoints.USER_NOTES}?{urlencode(params)}"
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取用户喜欢笔记数据
    async def fetch_user_likes(self, user_id: str, cursor: str = "", limit: int = 20):
        """
        获取用户喜欢笔记数据
        Get user likes data
        
        Args:
            user_id (str): 用户ID
            cursor (str): 分页游标
            limit (int): 每页数量
            
        Returns:
            dict: 用户喜欢笔记数据
        """
        # 获取小红书的请求头
        kwargs = await self.get_xiaohongshu_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求参数
            params = UserLikes(user_id=user_id, cursor=cursor, limit=limit).dict()
            
            # 构建请求URL
            endpoint = f"{XiaoHongShuAPIEndpoints.USER_LIKES}?{urlencode(params)}"
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取笔记评论数据
    async def fetch_note_comments(self, note_id: str, cursor: str = "", limit: int = 20):
        """
        获取笔记评论数据
        Get note comments data
        
        Args:
            note_id (str): 笔记ID
            cursor (str): 分页游标
            limit (int): 每页数量
            
        Returns:
            dict: 笔记评论数据
        """
        # 获取小红书的请求头
        kwargs = await self.get_xiaohongshu_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求参数
            params = NoteComments(note_id=note_id, cursor=cursor, limit=limit).dict()
            
            # 构建请求URL
            endpoint = f"{XiaoHongShuAPIEndpoints.NOTE_COMMENTS}?{urlencode(params)}"
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 从URL中提取笔记ID并获取笔记数据
    async def fetch_note_from_url(self, url: str):
        """
        从URL中提取笔记ID并获取笔记数据
        Extract note ID from URL and get note data
        
        Args:
            url (str): 小红书笔记URL
            
        Returns:
            dict: 笔记数据
        """
        # 标准化URL
        url = URLUtils.normalize_url(url)
        
        # 从URL中提取笔记ID
        note_id = NoteIdFetcher.extract_note_id_from_url(url)
        if not note_id:
            raise ValueError("无法从URL中提取笔记ID")
        
        # 获取笔记数据
        return await self.fetch_one_note(note_id)

    # 从URL中提取用户ID并获取用户资料
    async def fetch_user_from_url(self, url: str):
        """
        从URL中提取用户ID并获取用户资料
        Extract user ID from URL and get user profile
        
        Args:
            url (str): 小红书用户主页URL
            
        Returns:
            dict: 用户资料数据
        """
        # 标准化URL
        url = URLUtils.normalize_url(url)
        
        # 从URL中提取用户ID
        user_id = UserIdFetcher.extract_user_id_from_url(url)
        if not user_id:
            raise ValueError("无法从URL中提取用户ID")
        
        # 获取用户资料
        return await self.fetch_user_profile(user_id)