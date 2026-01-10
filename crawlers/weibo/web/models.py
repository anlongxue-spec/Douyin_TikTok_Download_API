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
    id: str = Field(..., description="微博ID")


class UserProfile(BaseRequestModel):
    """获取用户资料的请求模型 (User Profile Request Model)"""
    id: str = Field(..., description="用户ID")


class UserVideos(BaseRequestModel):
    """获取用户视频列表的请求模型 (User Videos Request Model)"""
    id: str = Field(..., description="用户ID")
    page: Optional[int] = Field(1, description="页码")
    count: Optional[int] = Field(10, description="每页数量")


class SearchVideos(BaseRequestModel):
    """搜索视频的请求模型 (Search Videos Request Model)"""
    keyword: str = Field(..., description="搜索关键词")
    page: Optional[int] = Field(1, description="页码")
    count: Optional[int] = Field(20, description="每页数量")


class HotVideos(BaseRequestModel):
    """获取热门视频的请求模型 (Hot Videos Request Model)"""
    page: Optional[int] = Field(1, description="页码")
    count: Optional[int] = Field(20, description="每页数量")


class UserStatuses(BaseRequestModel):
    """获取用户微博列表的请求模型 (User Statuses Request Model)"""
    id: str = Field(..., description="用户ID")
    page: Optional[int] = Field(1, description="页码")
    feature: Optional[int] = Field(0, description="微博类型特征")


class ContainerRequest(BaseRequestModel):
    """容器请求模型 (Container Request Model)"""
    containerid: str = Field(..., description="容器ID")
    page: Optional[int] = Field(1, description="页码")


class VideoPlayInfo(BaseRequestModel):
    """获取视频播放信息的请求模型 (Video Play Info Request Model)"""
    mid: str = Field(..., description="微博MID")


class StatusDetail(BaseRequestModel):
    """获取微博详情的请求模型 (Status Detail Request Model)"""
    id: str = Field(..., description="微博ID")


class SearchUsers(BaseRequestModel):
    """搜索用户的请求模型 (Search Users Request Model)"""
    keyword: str = Field(..., description="搜索关键词")
    page: Optional[int] = Field(1, description="页码")


class SearchTopics(BaseRequestModel):
    """搜索话题的请求模型 (Search Topics Request Model)"""
    keyword: str = Field(..., description="搜索关键词")
    page: Optional[int] = Field(1, description="页码")