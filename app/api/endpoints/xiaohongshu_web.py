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

from crawlers.xiaohongshu.web.web_crawler import XiaoHongShuWebCrawler  # 导入小红书Web爬虫


router = APIRouter()
XiaoHongShuWebCrawler = XiaoHongShuWebCrawler()


# 获取单个笔记数据
@router.get("/fetch_one_note", response_model=ResponseModel, summary="获取单个笔记数据/Get single note data")
async def fetch_one_note(request: Request,
                        note_id: str = Query(example="64d7e4b9000000002703c757", description="笔记id/Note id")):
    """
    # [中文]
    ### 用途:
    - 获取单个笔记数据
    ### 参数:
    - note_id: 笔记id
    ### 返回:
    - 笔记数据

    # [English]
    ### Purpose:
    - Get single note data
    ### Parameters:
    - note_id: Note id
    ### Return:
    - Note data

    # [示例/Example]
    note_id = "64d7e4b9000000002703c757"
    """
    try:
        data = await XiaoHongShuWebCrawler.fetch_one_note(note_id)
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
                           user_id: str = Query(example="64d7e4b9000000002703c757", description="用户id/User id")):
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
    user_id = "64d7e4b9000000002703c757"
    """
    try:
        data = await XiaoHongShuWebCrawler.fetch_user_profile(user_id)
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


# 获取用户笔记列表
@router.get("/fetch_user_notes", response_model=ResponseModel, summary="获取用户笔记列表/Get user notes list")
async def fetch_user_notes(request: Request,
                         user_id: str = Query(example="64d7e4b9000000002703c757", description="用户id/User id"),
                         page: int = Query(default=1, description="页码/Page number"),
                         page_size: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户笔记列表
    ### 参数:
    - user_id: 用户id
    - page: 页码
    - page_size: 每页数量
    ### 返回:
    - 用户笔记列表数据

    # [English]
    ### Purpose:
    - Get user notes list
    ### Parameters:
    - user_id: User id
    - page: Page number
    - page_size: Number per page
    ### Return:
    - User notes list data

    # [示例/Example]
    user_id = "64d7e4b9000000002703c757"
    page = 1
    page_size = 20
    """
    try:
        data = await XiaoHongShuWebCrawler.fetch_user_notes(user_id, page, page_size)
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


# 获取用户喜欢的笔记列表
@router.get("/fetch_user_likes", response_model=ResponseModel, summary="获取用户喜欢的笔记列表/Get user liked notes list")
async def fetch_user_likes(request: Request,
                         user_id: str = Query(example="64d7e4b9000000002703c757", description="用户id/User id"),
                         page: int = Query(default=1, description="页码/Page number"),
                         page_size: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户喜欢的笔记列表
    ### 参数:
    - user_id: 用户id
    - page: 页码
    - page_size: 每页数量
    ### 返回:
    - 用户喜欢的笔记列表数据

    # [English]
    ### Purpose:
    - Get user liked notes list
    ### Parameters:
    - user_id: User id
    - page: Page number
    - page_size: Number per page
    ### Return:
    - User liked notes list data

    # [示例/Example]
    user_id = "64d7e4b9000000002703c757"
    page = 1
    page_size = 20
    """
    try:
        data = await XiaoHongShuWebCrawler.fetch_user_likes(user_id, page, page_size)
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


# 获取笔记评论
@router.get("/fetch_note_comments", response_model=ResponseModel, summary="获取笔记评论/Get note comments")
async def fetch_note_comments(request: Request,
                            note_id: str = Query(example="64d7e4b9000000002703c757", description="笔记id/Note id"),
                            cursor: int = Query(default=0, description="游标/Cursor"),
                            count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取笔记评论
    ### 参数:
    - note_id: 笔记id
    - cursor: 游标
    - count: 每页数量
    ### 返回:
    - 笔记评论数据

    # [English]
    ### Purpose:
    - Get note comments
    ### Parameters:
    - note_id: Note id
    - cursor: Cursor
    - count: Number per page
    ### Return:
    - Note comments data

    # [示例/Example]
    note_id = "64d7e4b9000000002703c757"
    cursor = 0
    count = 20
    """
    try:
        data = await XiaoHongShuWebCrawler.fetch_note_comments(note_id, cursor, count)
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


# 从URL中获取笔记数据
@router.get("/fetch_note_from_url", response_model=ResponseModel, summary="从URL中获取笔记数据/Get note data from URL")
async def fetch_note_from_url(request: Request,
                            url: str = Query(example="https://www.xiaohongshu.com/explore/64d7e4b9000000002703c757", description="笔记URL/Note URL")):
    """
    # [中文]
    ### 用途:
    - 从URL中获取笔记数据
    ### 参数:
    - url: 笔记URL
    ### 返回:
    - 笔记数据

    # [English]
    ### Purpose:
    - Get note data from URL
    ### Parameters:
    - url: Note URL
    ### Return:
    - Note data

    # [示例/Example]
    url = "https://www.xiaohongshu.com/explore/64d7e4b9000000002703c757"
    """
    try:
        data = await XiaoHongShuWebCrawler.fetch_note_from_url(url)
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
                            url: str = Query(example="https://www.xiaohongshu.com/user/profile/64d7e4b9000000002703c757", description="用户主页URL/User homepage URL")):
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
    url = "https://www.xiaohongshu.com/user/profile/64d7e4b9000000002703c757"
    """
    try:
        data = await XiaoHongShuWebCrawler.fetch_user_from_url(url)
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