from typing import List

from fastapi import APIRouter, Body, Query, Request, HTTPException  # 导入FastAPI组件
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel  # 导入响应模型

from crawlers.kuaishou.web.web_crawler import KuaiShouWebCrawler  # 导入快手Web爬虫


router = APIRouter()
KuaiShouWebCrawler = KuaiShouWebCrawler()


# 获取单个视频数据
@router.get("/fetch_one_video", response_model=ResponseModel, summary="获取单个视频数据/Get single video data")
async def fetch_one_video(request: Request,
                          photo_id: str = Query(example="3xq4b56789012345678901234567890", description="视频id/Video id")):
    """
    # [中文]
    ### 用途:
    - 获取单个视频数据
    ### 参数:
    - photo_id: 视频id
    ### 返回:
    - 视频数据

    # [English]
    ### Purpose:
    - Get single video data
    ### Parameters:
    - photo_id: Video id
    ### Return:
    - Video data

    # [示例/Example]
    photo_id = "3xq4b56789012345678901234567890"
    """
    try:
        data = await KuaiShouWebCrawler.fetch_one_video(photo_id)
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


# 获取用户资料数据
@router.get("/fetch_user_profile", response_model=ResponseModel, summary="获取用户资料数据/Get user profile data")
async def fetch_user_profile(request: Request,
                           user_id: str = Query(example="3xq4b5678901234567890", description="用户id/User id")):
    """
    # [中文]
    ### 用途:
    - 获取用户资料数据
    ### 参数:
    - user_id: 用户id
    ### 返回:
    - 用户资料数据

    # [English]
    ### Purpose:
    - Get user profile data
    ### Parameters:
    - user_id: User id
    ### Return:
    - User profile data

    # [示例/Example]
    user_id = "3xq4b5678901234567890"
    """
    try:
        data = await KuaiShouWebCrawler.fetch_user_profile(user_id)
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


# 获取用户作品数据
@router.get("/fetch_user_works", response_model=ResponseModel, summary="获取用户作品数据/Get user works data")
async def fetch_user_works(request: Request,
                         user_id: str = Query(example="3xq4b5678901234567890", description="用户id/User id"),
                         pcursor: str = Query(default="", description="分页游标/Pagination cursor"),
                         count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户作品数据
    ### 参数:
    - user_id: 用户id
    - pcursor: 分页游标
    - count: 每页数量
    ### 返回:
    - 用户作品数据

    # [English]
    ### Purpose:
    - Get user works data
    ### Parameters:
    - user_id: User id
    - pcursor: Pagination cursor
    - count: Number per page
    ### Return:
    - User works data

    # [示例/Example]
    user_id = "3xq4b5678901234567890"
    pcursor = ""
    count = 20
    """
    try:
        data = await KuaiShouWebCrawler.fetch_user_works(user_id, pcursor, count)
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


# 获取用户喜欢作品数据
@router.get("/fetch_user_likes", response_model=ResponseModel, summary="获取用户喜欢作品数据/Get user likes data")
async def fetch_user_likes(request: Request,
                         user_id: str = Query(example="3xq4b5678901234567890", description="用户id/User id"),
                         pcursor: str = Query(default="", description="分页游标/Pagination cursor"),
                         count: int = Query(default=20, description="每页数量/Number per page")):
    """
    # [中文]
    ### 用途:
    - 获取用户喜欢作品数据
    ### 参数:
    - user_id: 用户id
    - pcursor: 分页游标
    - count: 每页数量
    ### 返回:
    - 用户喜欢作品数据

    # [English]
    ### Purpose:
    - Get user likes data
    ### Parameters:
    - user_id: User id
    - pcursor: Pagination cursor
    - count: Number per page
    ### Return:
    - User likes data

    # [示例/Example]
    user_id = "3xq4b5678901234567890"
    pcursor = ""
    count = 20
    """
    try:
        data = await KuaiShouWebCrawler.fetch_user_likes(user_id, pcursor, count)
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


# 从URL获取视频数据
@router.get("/fetch_video_from_url", response_model=ResponseModel, summary="从URL获取视频数据/Get video data from URL")
async def fetch_video_from_url(request: Request,
                             url: str = Query(example="https://v.kuaishou.com/abcdef", description="快手视频URL/KuaiShou video URL")):
    """
    # [中文]
    ### 用途:
    - 从URL获取视频数据
    ### 参数:
    - url: 快手视频URL
    ### 返回:
    - 视频数据

    # [English]
    ### Purpose:
    - Get video data from URL
    ### Parameters:
    - url: KuaiShou video URL
    ### Return:
    - Video data

    # [示例/Example]
    url = "https://v.kuaishou.com/abcdef"
    """
    try:
        data = await KuaiShouWebCrawler.fetch_video_from_url(url)
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


# 从URL获取用户资料数据
@router.get("/fetch_user_from_url", response_model=ResponseModel, summary="从URL获取用户资料数据/Get user profile from URL")
async def fetch_user_from_url(request: Request,
                            url: str = Query(example="https://www.kuaishou.com/u/abcdef123456", description="快手用户主页URL/KuaiShou user homepage URL")):
    """
    # [中文]
    ### 用途:
    - 从URL获取用户资料数据
    ### 参数:
    - url: 快手用户主页URL
    ### 返回:
    - 用户资料数据

    # [English]
    ### Purpose:
    - Get user profile from URL
    ### Parameters:
    - url: KuaiShou user homepage URL
    ### Return:
    - User profile data

    # [示例/Example]
    url = "https://www.kuaishou.com/u/abcdef123456"
    """
    try:
        data = await KuaiShouWebCrawler.fetch_user_from_url(url)
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