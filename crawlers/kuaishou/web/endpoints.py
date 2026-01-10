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


class KuaiShouAPIEndpoints:
    """快手API端点定义类 (KuaiShou API Endpoints Definition Class)"""

    # 基础URL (Base URLs)
    BASE_URL = "https://www.kuaishou.com"
    API_BASE_URL = "https://www.kuaishou.com/graphql"
    PC_BASE_URL = "https://pc.kuaishou.com"
    SHORT_VIDEO_BASE_URL = "https://short-video.kuaishou.com"

    # 视频相关API端点 (Video Related API Endpoints)
    VIDEO_DETAIL = f"{BASE_URL}/short-video"
    VIDEO_INFO = f"{API_BASE_URL}/"
    VIDEO_PLAY_URL = lambda self, video_id: f"{self.PC_BASE_URL}/rest/video/playUrl/{video_id}"
    VIDEO_COMMENTS = lambda self, video_id, pcursor="": f"{self.PC_BASE_URL}/rest/comment/list?eid={video_id}&pcursor={pcursor}"
    RELATED_VIDEOS = lambda self, video_id: f"{self.PC_BASE_URL}/rest/feed/relatedVideo/{video_id}"

    # 用户相关API端点 (User Related API Endpoints)
    USER_HOME = f"{BASE_URL}/profile"
    USER_INFO = f"{API_BASE_URL}/"
    USER_WORKS = f"{API_BASE_URL}/"
    USER_LIKES = f"{API_BASE_URL}/"
    USER_COLLECTIONS = f"{API_BASE_URL}/"
    USER_PROFILE = lambda self, user_id: f"{self.PC_BASE_URL}/rest/user/profile/{user_id}"
    USER_VIDEOS = lambda self, user_id, pcursor="": f"{self.PC_BASE_URL}/rest/feed/profile/{user_id}?pcursor={pcursor}"
    USER_LIKED_VIDEOS = lambda self, user_id, pcursor="": f"{self.PC_BASE_URL}/rest/feed/liked/{user_id}?pcursor={pcursor}"
    USER_FOLLOWS = lambda self, user_id, pcursor="": f"{self.PC_BASE_URL}/rest/follow/list?userId={user_id}&pcursor={pcursor}"
    USER_FANS = lambda self, user_id, pcursor="": f"{self.PC_BASE_URL}/rest/follow/fansList?userId={user_id}&pcursor={pcursor}"

    # 推荐和热门API端点 (Recommended and Hot API Endpoints)
    RECOMMENDED_VIDEOS = lambda self, pcursor="": f"{self.PC_BASE_URL}/rest/feed/hot?pcursor={pcursor}"
    HOT_VIDEOS = lambda self, category_id="", pcursor="": f"{self.PC_BASE_URL}/rest/feed/hot?categoryId={category_id}&pcursor={pcursor}"
    CATEGORIES = lambda self: f"{self.PC_BASE_URL}/rest/category/list"

    # 搜索API端点 (Search API Endpoints)
    SEARCH_VIDEOS = lambda self, keyword, pcursor="": f"{self.PC_BASE_URL}/rest/search/feed?keyword={keyword}&pcursor={pcursor}"
    SEARCH_USERS = lambda self, keyword, pcursor="": f"{self.PC_BASE_URL}/rest/search/user?keyword={keyword}&pcursor={pcursor}"

    # 短视频API端点 (Short Video API Endpoints)
    SHORT_VIDEO_DETAIL = lambda self, video_id: f"{self.SHORT_VIDEO_BASE_URL}/rest/note/info?photoId={video_id}"
    SHORT_VIDEO_PLAY_URL = lambda self, video_id: f"{self.SHORT_VIDEO_BASE_URL}/rest/note/playUrl?photoId={video_id}"

    # H5相关URL (H5 Related URLs)
    H5_VIDEO_URL = lambda self, video_id: f"https://h5.kuaishou.com/short-video/{video_id}"
    H5_USER_URL = lambda self, user_id: f"https://h5.kuaishou.com/profile/{user_id}"