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


class WeiBoAPIEndpoints:
    """微博API端点类 (WeiBo API Endpoints Class)"""

    # 微博API基础URL
    BASE_URL = "https://m.weibo.cn"
    PC_BASE_URL = "https://weibo.com"

    # 微博API端点 (WeiBo API Endpoints)
    # 微博移动端API
    MOBILE_BASE = f"{BASE_URL}/api"
    # 微博PC端API
    PC_BASE = f"{PC_BASE_URL}/aj"

    # 微博视频API端点 (WeiBo Video API Endpoints)
    # 获取单个视频详情
    VIDEO_DETAIL = f"{MOBILE_BASE}/statuses/show?id={{}}".format
    # 获取微博用户主页视频
    USER_VIDEOS = f"{MOBILE_BASE}/container/getIndex?containerid={{}}".format
    # 获取热门视频
    HOT_VIDEOS = f"{MOBILE_BASE}/container/getIndex?containerid=106003type%3D61%26q%3D%E7%83%AD%E9%97%A8%E8%A7%86%E9%A2%91%26t%3D0".format
    # 获取搜索结果
    SEARCH_RESULTS = f"{MOBILE_BASE}/container/getIndex?containerid=100103type%3D61%26q%3D{{}}&page={{}}".format

    # 微博用户API端点 (WeiBo User API Endpoints)
    # 获取用户主页信息
    USER_PROFILE = f"{MOBILE_BASE}/users/show?id={{}}".format
    # 获取用户微博列表
    USER_STATUSES = f"{MOBILE_BASE}/statuses/user_timeline?id={{}}&page={{}}&feature=0".format
    # 获取用户视频列表
    USER_VIDEO_LIST = f"{MOBILE_BASE}/container/getIndex?containerid=107603{{}}_-_VIDEOS&page={{}}".format

    # 微博PC端API端点 (WeiBo PC API Endpoints)
    # 获取视频播放信息
    VIDEO_PLAY_INFO = f"{PC_BASE}/video/show?ajwvr=6&mid={{}}".format
    # 获取微博详情
    STATUS_DETAIL = f"{PC_BASE}/statuses/show?id={{}}&is_long_text=true".format

    # 微博搜索API端点 (WeiBo Search API Endpoints)
    # 搜索视频
    SEARCH_VIDEOS = f"{MOBILE_BASE}/container/getIndex?containerid=100103type%3D61%26q%3D{{}}&page={{}}".format
    # 搜索用户
    SEARCH_USERS = f"{MOBILE_BASE}/container/getIndex?containerid=100103type%3D2%26q%3D{{}}&page={{}}".format
    # 搜索话题
    SEARCH_TOPICS = f"{MOBILE_BASE}/container/getIndex?containerid=100103type%3D1%26q%3D{{}}&page={{}}".format