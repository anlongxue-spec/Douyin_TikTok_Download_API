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

from typing import List

from fastapi import APIRouter, Body, Query, Request, HTTPException  # 导入FastAPI组件
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel  # 导入响应模型

from crawlers.weibo.web.web_crawler import WeiBoWebCrawler  # 导入微博Web爬虫


router = APIRouter()
WeiBoWebCrawler = WeiBoWebCrawler()


# 获取单个视频数据
@router.get("/fetch_one_video", response_model=ResponseModel, summary="获取单个视频数据/Get single video data")
async def fetch_one_video(request: Request,
                        weibo_id: str = Query(example="4985234567890123456", description="微博id/Weibo id")):
    """
    # [中文]
    ### 用途:
    - 获取单个视频数据
    ### 参数:
    - weibo_id: 微博id
    ### 返回:
    - 视频数据

    # [English]
    ### Purpose:
    - Get single video data
    ### Parameters:
    - weibo_id: Weibo id
    ### Return:
    - Video data

    # [示例/Example]
    weibo_id = "4985234567890123456"
    """
    try:
        data = await WeiBoWebCrawler.fetch_one_video(weibo_id)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 获取用户主页数据
@router.get("/fetch_user_profile", response_model=ResponseModel, summary="获取用户主页数据/Get user profile data")
async def fetch_user_profile(request: Request,
                           user_id: str = Query(example="1234567890", description="用户id/User id")):
    """
    # [中文]
    ### 用途:
    - 获取用户主页数据
    ### 参数:
    - user_id: 用户id
    ### 返回:
    - 用户主页数据

    # [English]
    ### Purpose:
    - Get user profile data
    ### Parameters:
    - user_id: User id
    ### Return:
    - User profile data

    # [示例/Example]
    user_id = "1234567890"
    """
    try:
        data = await WeiBoWebCrawler.fetch_user_profile(user_id)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 获取用户视频列表
@router.get("/fetch_user_videos", response_model=ResponseModel, summary="获取用户视频列表/Get user videos list")
async def fetch_user_videos(request: Request,
                         user_id: str = Query(example="1234567890", description="用户id/User id"),
                         page: int = Query(default=1, description="页码/Page number"),
                         count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户视频列表
    ### 参数:
    - user_id: 用户id
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 用户视频列表数据

    # [English]
    ### Purpose:
    - Get user videos list
    ### Parameters:
    - user_id: User id
    - page: Page number
    - count: Number per page
    ### Return:
    - User videos list data

    # [示例/Example]
    user_id = "1234567890"
    page = 1
    count = 20
    """
    try:
        data = await WeiBoWebCrawler.fetch_user_videos(user_id, page, count)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 获取热门视频
@router.get("/fetch_hot_videos", response_model=ResponseModel, summary="获取热门视频/Get hot videos")
async def fetch_hot_videos(request: Request,
                         page: int = Query(default=1, description="页码/Page number"),
                         count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取热门视频
    ### 参数:
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 热门视频列表数据

    # [English]
    ### Purpose:
    - Get hot videos
    ### Parameters:
    - page: Page number
    - count: Number per page
    ### Return:
    - Hot videos list data

    # [示例/Example]
    page = 1
    count = 20
    """
    try:
        data = await WeiBoWebCrawler.fetch_hot_videos(page, count)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 获取用户状态
@router.get("/fetch_user_statuses", response_model=ResponseModel, summary="获取用户状态/Get user statuses")
async def fetch_user_statuses(request: Request,
                            user_id: str = Query(example="1234567890", description="用户id/User id"),
                            page: int = Query(default=1, description="页码/Page number"),
                            count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户状态
    ### 参数:
    - user_id: 用户id
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 用户状态列表数据

    # [English]
    ### Purpose:
    - Get user statuses
    ### Parameters:
    - user_id: User id
    - page: Page number
    - count: Number per page
    ### Return:
    - User statuses list data

    # [示例/Example]
    user_id = "1234567890"
    page = 1
    count = 20
    """
    try:
        data = await WeiBoWebCrawler.fetch_user_statuses(user_id, page, count)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 搜索微博
@router.get("/search_weibo", response_model=ResponseModel, summary="搜索微博/Search weibo")
async def search_weibo(request: Request,
                     keyword: str = Query(example="抖音", description="搜索关键词/Search keyword"),
                     page: int = Query(default=1, description="页码/Page number"),
                     count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 搜索微博
    ### 参数:
    - keyword: 搜索关键词
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 搜索结果数据

    # [English]
    ### Purpose:
    - Search weibo
    ### Parameters:
    - keyword: Search keyword
    - page: Page number
    - count: Number per page
    ### Return:
    - Search results data

    # [示例/Example]
    keyword = "抖音"
    page = 1
    count = 20
    """
    try:
        data = await WeiBoWebCrawler.search_weibo(keyword, page, count)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 从URL中获取视频数据
@router.get("/fetch_video_from_url", response_model=ResponseModel, summary="从URL中获取视频数据/Get video data from URL")
async def fetch_video_from_url(request: Request,
                            url: str = Query(example="https://weibo.com/1234567890/LhA12345678", description="微博URL/Weibo URL")):
    """
    # [中文]
    ### 用途:
    - 从URL中获取视频数据
    ### 参数:
    - url: 微博URL
    ### 返回:
    - 视频数据

    # [English]
    ### Purpose:
    - Get video data from URL
    ### Parameters:
    - url: Weibo URL
    ### Return:
    - Video data

    # [示例/Example]
    url = "https://weibo.com/1234567890/LhA12345678"
    """
    try:
        data = await WeiBoWebCrawler.fetch_video_from_url(url)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())


# 从URL中获取用户数据
@router.get("/fetch_user_from_url", response_model=ResponseModel, summary="从URL中获取用户数据/Get user data from URL")
async def fetch_user_from_url(request: Request,
                            url: str = Query(example="https://weibo.com/1234567890", description="用户主页URL/User homepage URL")):
    """
    # [中文]
    ### 用途:
    - 从URL中获取用户数据
    ### 参数:
    - url: 用户主页URL
    ### 返回:
    - 用户数据

    # [English]
    ### Purpose:
    - Get user data from URL
    ### Parameters:
    - url: User homepage URL
    ### Return:
    - User data

    # [示例/Example]
    url = "https://weibo.com/1234567890"
    """
    try:
        data = await WeiBoWebCrawler.fetch_user_from_url(url)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())