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


class XiaoHongShuAPIEndpoints:
    """小红书API端点类 (XiaoHongShu API Endpoints Class)"""
    
    # 小红书基础URL (XiaoHongShu Base URL)
    BASE_URL = "https://www.xiaohongshu.com"
    
    # 笔记详情页 (Note Detail Page)
    NOTE_DETAIL = f"{BASE_URL}/explore"
    
    # 用户主页 (User Homepage)
    USER_HOME = f"{BASE_URL}/user/profile"
    
    # API基础URL (API Base URL)
    API_BASE_URL = "https://www.xiaohongshu.com/api/sns/v1"
    
    # 笔记信息API (Note Information API)
    NOTE_INFO = f"{API_BASE_URL}/note/detail"
    
    # 用户信息API (User Information API)
    USER_INFO = f"{API_BASE_URL}/user/profile"
    
    # 用户笔记API (User Notes API)
    USER_NOTES = f"{API_BASE_URL}/user/posted"
    
    # 用户喜欢API (User Likes API)
    USER_LIKES = f"{API_BASE_URL}/user/liked"
    
    # 搜索API (Search API)
    SEARCH = f"{BASE_URL}/api/sns/v1/search/notes"
    
    # 推荐笔记API (Recommended Notes API)
    RECOMMENDED_NOTES = f"{BASE_URL}/api/sns/v1/feed"
    
    # 视频播放URL API (Video Play URL API)
    VIDEO_PLAY_URL = f"{BASE_URL}/api/sns/web/v1/feed"
    
    # 笔记评论API (Note Comments API)
    NOTE_COMMENTS = f"{API_BASE_URL}/comment/list"