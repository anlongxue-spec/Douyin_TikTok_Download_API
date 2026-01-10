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


class NoteDetail(BaseRequestModel):
    """笔记详情请求模型 (Note Detail Request Model)"""
    note_id: str
    image_formats: str = "jpg"
    webpage_id: str = ""


class UserProfile(BaseRequestModel):
    """用户资料请求模型 (User Profile Request Model)"""
    user_id: str
    source: str = "web"


class UserNotes(BaseRequestModel):
    """用户笔记请求模型 (User Notes Request Model)"""
    user_id: str
    cursor: str = ""
    limit: int = 20
    image_formats: str = "jpg"
    source: str = "web"


class UserLikes(BaseRequestModel):
    """用户喜欢请求模型 (User Likes Request Model)"""
    user_id: str
    cursor: str = ""
    limit: int = 20
    image_formats: str = "jpg"
    source: str = "web"


class NoteComments(BaseRequestModel):
    """笔记评论请求模型 (Note Comments Request Model)"""
    note_id: str
    cursor: str = ""
    limit: int = 20
    image_formats: str = "jpg"
    source: str = "web"


class SearchNotes(BaseRequestModel):
    """搜索笔记请求模型 (Search Notes Request Model)"""
    keyword: str
    sort: str = "general"
    page: int = 1
    page_size: int = 20
    image_formats: str = "jpg"
    source: str = "web"