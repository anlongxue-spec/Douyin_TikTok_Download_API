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

# 基础爬虫客户端和皮皮虾API端点
from crawlers.base_crawler import BaseCrawler
from crawlers.pipixia.web.endpoints import PiPiXiaAPIEndpoints
# 皮皮虾接口数据请求模型
from crawlers.pipixia.web.models import (
    BaseRequestModel, VideoDetail, UserProfile,
    UserPublishedVideos, UserLikedVideos,
    VideoComments, RelatedVideos, RecommendedVideos,
    HotVideos, SearchVideos, VideoPlayUrl
)
# 皮皮虾应用的工具类
from crawlers.pipixia.web.utils import (
    VideoIdFetcher,  # 视频ID获取
    UserIdFetcher,  # 用户ID获取
    URLUtils,  # URL工具类
    DataParser  # 数据解析工具
)

# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class PiPiXiaWebCrawler:
    """皮皮虾网页版爬虫类 (PiPiXia Web Crawler Class)"""

    # 从配置文件中获取皮皮虾的请求头
    async def get_pipixia_headers(self):
        """
        获取皮皮虾的请求头
        Get PiPiXia request headers
        
        Returns:
            dict: 包含headers和proxies的字典
        """
        pipixia_config = config["TokenManager"]["pipixia"]
        kwargs = {
            "headers": {
                "Accept-Language": pipixia_config["headers"]["Accept-Language"],
                "User-Agent": pipixia_config["headers"]["User-Agent"],
                "Referer": pipixia_config["headers"]["Referer"],
                "Cookie": pipixia_config["headers"]["Cookie"],
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            "proxies": {"http://": pipixia_config["proxies"]["http"], "https://": pipixia_config["proxies"]["https"]},
        }
        return kwargs

    # 获取单个视频详情
    async def fetch_one_video(self, aweme_id: str):
        """
        获取单个视频详情
        Get single video detail
        
        Args:
            aweme_id (str): 视频ID
            
        Returns:
            dict: 视频详情数据
        """
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.VIDEO_DETAIL(aweme_id)
            
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
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.USER_PROFILE(user_id)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取用户发布的视频列表
    async def fetch_user_published_videos(self, user_id: str, cursor: int = 0, count: int = 20):
        """
        获取用户发布的视频列表
        Get user published videos list
        
        Args:
            user_id (str): 用户ID
            cursor (int): 游标
            count (int): 每页数量
            
        Returns:
            dict: 用户发布的视频列表数据
        """
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.USER_PUBLISHED_VIDEOS(user_id, cursor, count)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取用户喜欢的视频列表
    async def fetch_user_liked_videos(self, user_id: str, cursor: int = 0, count: int = 20):
        """
        获取用户喜欢的视频列表
        Get user liked videos list
        
        Args:
            user_id (str): 用户ID
            cursor (int): 游标
            count (int): 每页数量
            
        Returns:
            dict: 用户喜欢的视频列表数据
        """
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.USER_LIKED_VIDEOS(user_id, cursor, count)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取视频评论
    async def fetch_video_comments(self, aweme_id: str, cursor: int = 0, count: int = 20):
        """
        获取视频评论
        Get video comments
        
        Args:
            aweme_id (str): 视频ID
            cursor (int): 游标
            count (int): 每页数量
            
        Returns:
            dict: 视频评论数据
        """
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.VIDEO_COMMENTS(aweme_id, cursor, count)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取相关视频
    async def fetch_related_videos(self, aweme_id: str, count: int = 20):
        """
        获取相关视频
        Get related videos
        
        Args:
            aweme_id (str): 视频ID
            count (int): 数量
            
        Returns:
            dict: 相关视频数据
        """
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.RELATED_VIDEOS(aweme_id, count)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取推荐视频
    async def fetch_recommended_videos(self, max_cursor: int = 0, count: int = 20):
        """
        获取推荐视频
        Get recommended videos
        
        Args:
            max_cursor (int): 最大游标
            count (int): 每页数量
            
        Returns:
            dict: 推荐视频数据
        """
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.RECOMMENDED_VIDEOS(max_cursor, count)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 搜索视频
    async def search_videos(self, keyword: str, offset: int = 0, count: int = 20):
        """
        搜索视频
        Search videos
        
        Args:
            keyword (str): 搜索关键词
            offset (int): 偏移量
            count (int): 每页数量
            
        Returns:
            dict: 搜索结果数据
        """
        # URL编码关键词
        encoded_keyword = quote_plus(keyword)
        # 获取皮皮虾的请求头
        kwargs = await self.get_pipixia_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建请求URL
            endpoint = PiPiXiaAPIEndpoints.SEARCH_VIDEOS(encoded_keyword, offset, count)
            
            # 发送请求
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 从URL中提取视频ID并获取视频详情
    async def fetch_video_from_url(self, url: str):
        """
        从URL中提取视频ID并获取视频详情
        Extract video ID from URL and get video detail
        
        Args:
            url (str): 皮皮虾视频URL
            
        Returns:
            dict: 视频详情数据
        """
        # 标准化URL
        url = URLUtils.normalize_url(url)
        
        # 从URL中提取视频ID
        video_id = VideoIdFetcher.extract_video_id_from_url(url)
        if not video_id:
            raise ValueError("无法从URL中提取视频ID")
        
        # 获取视频详情
        return await self.fetch_one_video(video_id)

    # 从URL中提取用户ID并获取用户资料
    async def fetch_user_from_url(self, url: str):
        """
        从URL中提取用户ID并获取用户资料
        Extract user ID from URL and get user profile
        
        Args:
            url (str): 皮皮虾用户主页URL
            
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

    # 从URL中提取用户ID并获取用户发布的视频列表
    async def fetch_user_published_videos_from_url(self, url: str, cursor: int = 0, count: int = 20):
        """
        从URL中提取用户ID并获取用户发布的视频列表
        Extract user ID from URL and get user published videos list
        
        Args:
            url (str): 皮皮虾用户主页URL
            cursor (int): 游标
            count (int): 每页数量
            
        Returns:
            dict: 用户发布的视频列表数据
        """
        # 标准化URL
        url = URLUtils.normalize_url(url)
        
        # 从URL中提取用户ID
        user_id = UserIdFetcher.extract_user_id_from_url(url)
        if not user_id:
            raise ValueError("无法从URL中提取用户ID")
        
        # 获取用户发布的视频列表
        return await self.fetch_user_published_videos(user_id, cursor, count)