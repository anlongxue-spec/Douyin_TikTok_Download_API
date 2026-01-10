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


from pydantic import BaseModel, Field
from typing import Optional, List


class BaseRequestModel(BaseModel):
    """基础请求模型 (Base Request Model)"""
    class Config:
        # 允许从额外的字段中创建模型
        extra = "allow"
        # 允许字段名与模型属性名不同
        allow_population_by_field_name = True


class VideoDetail(BaseRequestModel):
    """获取单个视频详情的请求模型 (Video Detail Request Model)"""
    aweme_id: str = Field(..., description="视频ID")


class UserProfile(BaseRequestModel):
    """获取用户资料的请求模型 (User Profile Request Model)"""
    user_id: str = Field(..., description="用户ID")


class UserPublishedVideos(BaseRequestModel):
    """获取用户发布的视频列表的请求模型 (User Published Videos Request Model)"""
    user_id: str = Field(..., description="用户ID")
    cursor: Optional[int] = Field(0, description="游标")
    count: Optional[int] = Field(20, description="每页数量")


class UserLikedVideos(BaseRequestModel):
    """获取用户喜欢的视频列表的请求模型 (User Liked Videos Request Model)"""
    user_id: str = Field(..., description="用户ID")
    cursor: Optional[int] = Field(0, description="游标")
    count: Optional[int] = Field(20, description="每页数量")


class VideoComments(BaseRequestModel):
    """获取视频评论的请求模型 (Video Comments Request Model)"""
    aweme_id: str = Field(..., description="视频ID")
    cursor: Optional[int] = Field(0, description="游标")
    count: Optional[int] = Field(20, description="每页数量")


class RelatedVideos(BaseRequestModel):
    """获取相关视频的请求模型 (Related Videos Request Model)"""
    aweme_id: str = Field(..., description="视频ID")
    count: Optional[int] = Field(20, description="数量")


class RecommendedVideos(BaseRequestModel):
    """获取推荐视频的请求模型 (Recommended Videos Request Model)"""
    max_cursor: Optional[int] = Field(0, description="最大游标")
    count: Optional[int] = Field(20, description="每页数量")


class HotVideos(BaseRequestModel):
    """获取热门视频的请求模型 (Hot Videos Request Model)"""
    cursor: Optional[int] = Field(0, description="游标")
    count: Optional[int] = Field(20, description="每页数量")


class SearchVideos(BaseRequestModel):
    """搜索视频的请求模型 (Search Videos Request Model)"""
    keyword: str = Field(..., description="搜索关键词")
    offset: Optional[int] = Field(0, description="偏移量")
    count: Optional[int] = Field(20, description="每页数量")


class SearchUsers(BaseRequestModel):
    """搜索用户的请求模型 (Search Users Request Model)"""
    keyword: str = Field(..., description="搜索关键词")
    offset: Optional[int] = Field(0, description="偏移量")
    count: Optional[int] = Field(10, description="每页数量")


class CategoryVideos(BaseRequestModel):
    """获取分类下的视频列表的请求模型 (Category Videos Request Model)"""
    category_id: str = Field(..., description="分类ID")
    cursor: Optional[int] = Field(0, description="游标")
    count: Optional[int] = Field(20, description="每页数量")


class VideoPlayUrl(BaseRequestModel):
    """获取视频播放地址的请求模型 (Video Play Url Request Model)"""
    video_id: str = Field(..., description="视频ID")


class AppConfig(BaseRequestModel):
    """获取APP配置的请求模型 (App Config Request Model)"""
    fp: str = Field(..., description="设备指纹")
    iid: str = Field(..., description="设备ID")
    device_id: str = Field(..., description="设备标识")
    os_version: str = Field(..., description="操作系统版本")
    version_code: str = Field(..., description="应用版本号")
    device_type: str = Field(..., description="设备类型")
    device_brand: str = Field(..., description="设备品牌")
    aid: str = Field(..., description="应用ID")