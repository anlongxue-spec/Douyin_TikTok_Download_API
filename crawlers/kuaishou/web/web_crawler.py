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
import httpx  # HTTP客户端

# 基础爬虫客户端和快手API端点
from crawlers.base_crawler import BaseCrawler
from crawlers.kuaishou.web.endpoints import KuaiShouAPIEndpoints
# 快手接口数据请求模型
from crawlers.kuaishou.web.models import (
    BaseRequestModel, UserProfile, UserWorks,
    UserLikes, UserCollections, VideoDetail
)
# 快手应用的工具类
from crawlers.kuaishou.web.utils import (
    PhotoIdFetcher,  # 视频ID获取
    UserIdFetcher,  # 用户ID获取
    URLUtils,  # URL工具类
    GraphQLQueryBuilder  # GraphQL查询构建器
)

# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class KuaiShouWebCrawler:
    """快手网页版爬虫类 (KuaiShou Web Crawler Class)"""

    # 从配置文件中获取快手的请求头
    async def get_kuaishou_headers(self):
        """
        获取快手的请求头
        Get KuaiShou request headers
        
        Returns:
            dict: 包含headers和proxies的字典
        """
        kuaishou_config = config["TokenManager"]["kuaishou"]
        
        # 处理代理配置
        proxies = kuaishou_config["proxies"]
        http_proxy = proxies["http"]
        https_proxy = proxies["https"]
        
        # 如果代理值为空，则不使用代理
        proxy_dict = None
        if http_proxy or https_proxy:
            proxy_dict = {
                "http://": http_proxy,
                "https://": https_proxy
            }
        
        kwargs = {
            "headers": {
                "Accept-Language": kuaishou_config["headers"]["Accept-Language"],
                "User-Agent": kuaishou_config["headers"]["User-Agent"],
                "Referer": kuaishou_config["headers"]["Referer"],
                "Cookie": kuaishou_config["headers"]["Cookie"],
                "Content-Type": "application/json",
                "Origin": "https://www.kuaishou.com"
            },
            "proxies": proxy_dict,
        }
        return kwargs

    # 获取单个视频数据
    async def fetch_one_video(self, photo_id: str):
        """
        获取单个视频数据
        Get single video data
        
        Args:
            photo_id (str): 视频ID
            
        Returns:
            dict: 视频数据
        """
        # 获取快手的请求头
        kwargs = await self.get_kuaishou_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建GraphQL查询
            query = GraphQLQueryBuilder.build_video_detail_query(photo_id)
            variables = {
                "photoId": photo_id,
                "type": "play",
                "webPageArea": ""
            }
            
            # 构建请求数据
            data = {
                "operationName": "videoDetail",
                "variables": variables,
                "query": query
            }
            
            print(f"\n发送GraphQL请求:")
            print(f"URL: {KuaiShouAPIEndpoints.API_BASE_URL}")
            print(f"Headers: {kwargs['headers']}")
            print(f"请求数据: {data}")
            
            # 发送请求
            try:
                response = await crawler.fetch_post_json(KuaiShouAPIEndpoints.API_BASE_URL, data=data)
                print(f"响应数据: {response}")
                return response
            except Exception as e:
                print(f"请求失败: {type(e).__name__}: {e}")
                raise

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
        # 获取快手的请求头
        kwargs = await self.get_kuaishou_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建GraphQL查询
            query = GraphQLQueryBuilder.build_user_profile_query(user_id)
            variables = {
                "userId": user_id,
                "pcursor": "",
                "page": 1,
                "webPageArea": ""
            }
            
            # 构建请求数据
            data = {
                "operationName": "userProfile",
                "variables": variables,
                "query": query
            }
            
            # 发送请求
            response = await crawler.fetch_post_json(KuaiShouAPIEndpoints.API_BASE_URL, data=data)
        return response

    # 获取用户作品数据
    async def fetch_user_works(self, user_id: str, pcursor: str = "", count: int = 20):
        """
        获取用户作品数据
        Get user works data
        
        Args:
            user_id (str): 用户ID
            pcursor (str): 分页游标
            count (int): 每页数量
            
        Returns:
            dict: 用户作品数据
        """
        # 获取快手的请求头
        kwargs = await self.get_kuaishou_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建GraphQL查询
            query = GraphQLQueryBuilder.build_user_works_query()
            variables = {
                "userId": user_id,
                "pcursor": pcursor,
                "page": 1,
                "webPageArea": ""
            }
            
            # 构建请求数据
            data = {
                "operationName": "visionProfilePhotoList",
                "variables": variables,
                "query": query
            }
            
            # 发送请求
            response = await crawler.fetch_post_json(KuaiShouAPIEndpoints.API_BASE_URL, data=data)
        return response

    # 获取用户喜欢作品数据
    async def fetch_user_likes(self, user_id: str, pcursor: str = "", count: int = 20):
        """
        获取用户喜欢作品数据
        Get user likes data
        
        Args:
            user_id (str): 用户ID
            pcursor (str): 分页游标
            count (int): 每页数量
            
        Returns:
            dict: 用户喜欢作品数据
        """
        # 获取快手的请求头
        kwargs = await self.get_kuaishou_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 构建GraphQL查询
            query = GraphQLQueryBuilder.build_user_likes_query()
            variables = {
                "userId": user_id,
                "pcursor": pcursor,
                "page": 1,
                "webPageArea": ""
            }
            
            # 构建请求数据
            data = {
                "operationName": "visionProfileLikedPhotoList",
                "variables": variables,
                "query": query
            }
            
            # 发送请求
            response = await crawler.fetch_post_json(KuaiShouAPIEndpoints.API_BASE_URL, data=data)
        return response

    # 从URL中提取视频ID并获取视频数据
    async def fetch_video_from_url(self, url: str):
        """
        从URL中提取视频ID并获取视频数据
        Extract video ID from URL and get video data
        
        Args:
            url (str): 快手视频URL
            
        Returns:
            dict: 视频数据
        """
        # 标准化URL
        url = URLUtils.normalize_url(url)
        
        # 检查是否为短链接
        if URLUtils.is_short_url(url):
            # 使用httpx获取短链接的完整URL
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url)
                full_url = str(response.url)
        else:
            full_url = url
        
        # 从完整URL中提取视频ID
        photo_id = PhotoIdFetcher.extract_photo_id_from_url(full_url)
        if not photo_id:
            raise ValueError("无法从URL中提取视频ID")
        
        # 获取视频数据
        return await self.fetch_one_video(photo_id)

    # 从URL中提取用户ID并获取用户资料
    async def fetch_user_from_url(self, url: str):
        """
        从URL中提取用户ID并获取用户资料
        Extract user ID from URL and get user profile
        
        Args:
            url (str): 快手用户主页URL
            
        Returns:
            dict: 用户资料数据
        """
        # 从URL中提取用户ID
        user_id = UserIdFetcher.extract_user_id_from_url(url)
        if not user_id:
            raise ValueError("无法从URL中提取用户ID")
        
        # 获取用户资料
        return await self.fetch_user_profile(user_id)