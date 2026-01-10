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

from crawlers.pipixia.web.web_crawler import PiPiXiaWebCrawler  # 导入皮皮虾Web爬虫


router = APIRouter()
PiPiXiaWebCrawler = PiPiXiaWebCrawler()


# 获取单个视频数据
@router.get("/fetch_one_video", response_model=ResponseModel, summary="获取单个视频数据/Get single video data")
async def fetch_one_video(request: Request,
                        video_id: str = Query(example="1234567890123456789", description="视频id/Video id")):
    """
    # [中文]
    ### 用途:
    - 获取单个视频数据
    ### 参数:
    - video_id: 视频id
    ### 返回:
    - 视频数据

    # [English]
    ### Purpose:
    - Get single video data
    ### Parameters:
    - video_id: Video id
    ### Return:
    - Video data

    # [示例/Example]
    video_id = "1234567890123456789"
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_one_video(video_id)
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
                           user_id: str = Query(example="123456789", description="用户id/User id")):
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
    user_id = "123456789"
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_user_profile(user_id)
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


# 获取用户发布的视频列表
@router.get("/fetch_user_published_videos", response_model=ResponseModel, summary="获取用户发布的视频列表/Get user published videos list")
async def fetch_user_published_videos(request: Request,
                                    user_id: str = Query(example="123456789", description="用户id/User id"),
                                    page: int = Query(default=1, description="页码/Page number"),
                                    count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户发布的视频列表
    ### 参数:
    - user_id: 用户id
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 用户发布的视频列表数据

    # [English]
    ### Purpose:
    - Get user published videos list
    ### Parameters:
    - user_id: User id
    - page: Page number
    - count: Number per page
    ### Return:
    - User published videos list data

    # [示例/Example]
    user_id = "123456789"
    page = 1
    count = 20
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_user_published_videos(user_id, page, count)
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


# 获取用户关注的视频列表
@router.get("/fetch_user_following_videos", response_model=ResponseModel, summary="获取用户关注的视频列表/Get user following videos list")
async def fetch_user_following_videos(request: Request,
                                    user_id: str = Query(example="123456789", description="用户id/User id"),
                                    page: int = Query(default=1, description="页码/Page number"),
                                    count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户关注的视频列表
    ### 参数:
    - user_id: 用户id
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 用户关注的视频列表数据

    # [English]
    ### Purpose:
    - Get user following videos list
    ### Parameters:
    - user_id: User id
    - page: Page number
    - count: Number per page
    ### Return:
    - User following videos list data

    # [示例/Example]
    user_id = "123456789"
    page = 1
    count = 20
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_user_following_videos(user_id, page, count)
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


# 获取推荐视频列表
@router.get("/fetch_recommended_videos", response_model=ResponseModel, summary="获取推荐视频列表/Get recommended videos list")
async def fetch_recommended_videos(request: Request,
                                 page: int = Query(default=1, description="页码/Page number"),
                                 count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取推荐视频列表
    ### 参数:
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 推荐视频列表数据

    # [English]
    ### Purpose:
    - Get recommended videos list
    ### Parameters:
    - page: Page number
    - count: Number per page
    ### Return:
    - Recommended videos list data

    # [示例/Example]
    page = 1
    count = 20
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_recommended_videos(page, count)
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


# 获取热门视频列表
@router.get("/fetch_hot_videos", response_model=ResponseModel, summary="获取热门视频列表/Get hot videos list")
async def fetch_hot_videos(request: Request,
                         page: int = Query(default=1, description="页码/Page number"),
                         count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取热门视频列表
    ### 参数:
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 热门视频列表数据

    # [English]
    ### Purpose:
    - Get hot videos list
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
        data = await PiPiXiaWebCrawler.fetch_hot_videos(page, count)
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


# 搜索视频
@router.get("/search_videos", response_model=ResponseModel, summary="搜索视频/Search videos")
async def search_videos(request: Request,
                      keyword: str = Query(example="美食", description="搜索关键词/Search keyword"),
                      page: int = Query(default=1, description="页码/Page number"),
                      count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 搜索视频
    ### 参数:
    - keyword: 搜索关键词
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 搜索结果数据

    # [English]
    ### Purpose:
    - Search videos
    ### Parameters:
    - keyword: Search keyword
    - page: Page number
    - count: Number per page
    ### Return:
    - Search results data

    # [示例/Example]
    keyword = "美食"
    page = 1
    count = 20
    """
    try:
        data = await PiPiXiaWebCrawler.search_videos(keyword, page, count)
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
                            url: str = Query(example="https://h5.pipix.com/s/123456789", description="视频URL/Video URL")):
    """
    # [中文]
    ### 用途:
    - 从URL中获取视频数据
    ### 参数:
    - url: 视频URL
    ### 返回:
    - 视频数据

    # [English]
    ### Purpose:
    - Get video data from URL
    ### Parameters:
    - url: Video URL
    ### Return:
    - Video data

    # [示例/Example]
    url = "https://h5.pipix.com/s/123456789"
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_video_from_url(url)
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
                            url: str = Query(example="https://h5.pipix.com/u/123456789", description="用户主页URL/User homepage URL")):
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
    url = "https://h5.pipix.com/u/123456789"
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_user_from_url(url)
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


# 获取视频评论列表
@router.get("/fetch_video_comments", response_model=ResponseModel, summary="获取视频评论列表/Get video comments list")
async def fetch_video_comments(request: Request,
                             video_id: str = Query(example="1234567890123456789", description="视频id/Video id"),
                             page: int = Query(default=1, description="页码/Page number"),
                             count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取视频评论列表
    ### 参数:
    - video_id: 视频id
    - page: 页码
    - count: 每页数量
    ### 返回:
    - 视频评论列表数据

    # [English]
    ### Purpose:
    - Get video comments list
    ### Parameters:
    - video_id: Video id
    - page: Page number
    - count: Number per page
    ### Return:
    - Video comments list data

    # [示例/Example]
    video_id = "1234567890123456789"
    page = 1
    count = 20
    """
    try:
        data = await PiPiXiaWebCrawler.fetch_video_comments(video_id, page, count)
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