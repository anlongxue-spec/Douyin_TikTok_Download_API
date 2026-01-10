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
from urllib.parse import quote_plus, urlencode  # URL编码

# 基础爬虫客户端和微博API端点
from crawlers.base_crawler import BaseCrawler
from crawlers.weibo.web.endpoints import WeiBoAPIEndpoints
# 微博接口数据请求模型
from crawlers.weibo.web.models import (
    BaseRequestModel, VideoDetail, UserProfile,
    UserVideos, SearchVideos, HotVideos,
    UserStatuses, ContainerRequest, VideoPlayInfo
)
# 微博应用的工具类
from crawlers.weibo.web.utils import (
    WeiBoIdFetcher,  # 微博ID获取
    UserIdFetcher,  # 用户ID获取
    URLUtils,  # URL工具类
    DataParser  # 数据解析工具
)

# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class WeiBoWebCrawler:
    """微博网页版爬虫类 (WeiBo Web Crawler Class)"""

    # 从配置文件中获取微博的请求头
    async def get_weibo_headers(self):
        """
        获取微博的请求头
        Get WeiBo request headers
        
        Returns:
            dict: 包含headers和proxies的字典
        """
        weibo_config = config["TokenManager"]["weibo"]
        kwargs = {
            "headers": {
                "Accept-Language": weibo_config["headers"]["Accept-Language"],
                "User-Agent": weibo_config["headers"]["User-Agent"],
                "Referer": weibo_config["headers"]["Referer"],
                "Cookie": weibo_config["headers"]["Cookie"],
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            "proxies": {"http://": weibo_config["proxies"]["http"], "https://": weibo_config["proxies"]["https"]},
        }
        return kwargs

    # 获取单个视频详情
    async def fetch_one_video(self, weibo_id: str):
        """
        获取单个视频详情
        Get single video detail
        
        Args:
            weibo_id (str): 微博ID
            
        Returns:
            dict: 视频详情数据
        """
        # 获取微博的请求头
        kwargs = await self.get_weibo_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = WeiBoAPIEndpoints.VIDEO_DETAIL(weibo_id)
            
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
        # 获取微博的请求头
        kwargs = await self.get_weibo_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = WeiBoAPIEndpoints.USER_PROFILE(user_id)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取用户视频列表
    async def fetch_user_videos(self, user_id: str, page: int = 1):
        """
        获取用户视频列表
        Get user videos list
        
        Args:
            user_id (str): 用户ID
            page (int): 页码
            
        Returns:
            dict: 用户视频列表数据
        """
        # 获取微博的请求头
        kwargs = await self.get_weibo_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建容器ID (微博用户视频列表的containerid)
            containerid = f"107603{user_id}_-_VIDEOS"
            # 构建请求URL
            endpoint = WeiBoAPIEndpoints.USER_VIDEOS(containerid)
            endpoint += f"&page={page}"
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取热门视频
    async def fetch_hot_videos(self, page: int = 1):
        """
        获取热门视频
        Get hot videos
        
        Args:
            page (int): 页码
            
        Returns:
            dict: 热门视频数据
        """
        # 获取微博的请求头
        kwargs = await self.get_weibo_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = WeiBoAPIEndpoints.HOT_VIDEOS
            endpoint += f"&page={page}"
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 搜索视频
    async def search_videos(self, keyword: str, page: int = 1):
        """
        搜索视频
        Search videos
        
        Args:
            keyword (str): 搜索关键词
            page (int): 页码
            
        Returns:
            dict: 搜索结果数据
        """
        # URL编码关键词
        encoded_keyword = quote_plus(keyword)
        # 获取微博的请求头
        kwargs = await self.get_weibo_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = WeiBoAPIEndpoints.SEARCH_VIDEOS(encoded_keyword, page)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取微博PC端视频播放信息
    async def fetch_video_play_info(self, mid: str):
        """
        获取微博PC端视频播放信息
        Get PC video play info
        
        Args:
            mid (str): 微博MID
            
        Returns:
            dict: 视频播放信息
        """
        # 获取微博的请求头
        kwargs = await self.get_weibo_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = WeiBoAPIEndpoints.VIDEO_PLAY_INFO(mid)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 从URL中提取微博ID并获取视频详情
    async def fetch_video_from_url(self, url: str):
        """
        从URL中提取微博ID并获取视频详情
        Extract weibo ID from URL and get video detail
        
        Args:
            url (str): 微博视频URL
            
        Returns:
            dict: 视频详情数据
        """
        # 标准化URL
        url = URLUtils.normalize_url(url)
        
        # 从URL中提取微博ID
        weibo_id = WeiBoIdFetcher.extract_weibo_id_from_url(url)
        if not weibo_id:
            raise ValueError("无法从URL中提取微博ID")
        
        # 获取视频详情
        return await self.fetch_one_video(weibo_id)

    # 从URL中提取用户ID并获取用户资料
    async def fetch_user_from_url(self, url: str):
        """
        从URL中提取用户ID并获取用户资料
        Extract user ID from URL and get user profile
        
        Args:
            url (str): 微博用户主页URL
            
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

    # 从URL中提取用户ID并获取用户视频列表
    async def fetch_user_videos_from_url(self, url: str, page: int = 1):
        """
        从URL中提取用户ID并获取用户视频列表
        Extract user ID from URL and get user videos list
        
        Args:
            url (str): 微博用户主页URL
            page (int): 页码
            
        Returns:
            dict: 用户视频列表数据
        """
        # 标准化URL
        url = URLUtils.normalize_url(url)
        
        # 从URL中提取用户ID
        user_id = UserIdFetcher.extract_user_id_from_url(url)
        if not user_id:
            raise ValueError("无法从URL中提取用户ID")
        
        # 获取用户视频列表
        return await self.fetch_user_videos(user_id, page)