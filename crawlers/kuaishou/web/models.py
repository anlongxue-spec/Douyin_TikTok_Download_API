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


from pydantic import BaseModel


class BaseRequestModel(BaseModel):
    """基础请求模型 (Base Request Model)"""
    pass


class VideoDetail(BaseRequestModel):
    """视频详情请求模型 (Video Detail Request Model)"""
    photoId: str
    page: int = 1


class UserProfile(BaseRequestModel):
    """用户资料请求模型 (User Profile Request Model)"""
    userId: str


class UserWorks(BaseRequestModel):
    """用户作品请求模型 (User Works Request Model)"""
    userId: str
    pcursor: str = ""
    count: int = 20


class UserLikes(BaseRequestModel):
    """用户喜欢请求模型 (User Likes Request Model)"""
    userId: str
    pcursor: str = ""
    count: int = 20


class UserCollections(BaseRequestModel):
    """用户收藏请求模型 (User Collections Request Model)"""
    userId: str
    pcursor: str = ""
    count: int = 20