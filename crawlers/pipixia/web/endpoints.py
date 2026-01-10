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


class PiPiXiaAPIEndpoints:
    """皮皮虾API端点类 (PiPiXia API Endpoints Class)"""

    # 皮皮虾API基础URL
    BASE_URL = "https://is.snssdk.com"
    H5_BASE_URL = "https://h5.pipix.com"

    # 皮皮虾API端点 (PiPiXia API Endpoints)
    # 视频相关API
    # 获取单个视频详情
    VIDEO_DETAIL = f"{BASE_URL}/aweme/v1/aweme/detail/?aweme_id={{}}".format
    # 获取视频评论
    VIDEO_COMMENTS = f"{BASE_URL}/aweme/v1/comment/list/?aweme_id={{}}&cursor={{}}&count={{}}".format
    # 获取相关视频
    RELATED_VIDEOS = f"{BASE_URL}/aweme/v1/aweme/related/?aweme_id={{}}&count={{}}".format
    # 获取视频播放地址
    VIDEO_PLAY_URL = f"{BASE_URL}/aweme/v1/play/?video_id={{}}&vr_type=0&is_play_url=1&source=PackSourceEnum_PUBLISH".format

    # 用户相关API
    # 获取用户主页信息
    USER_PROFILE = f"{BASE_URL}/aweme/v1/user/profile/?user_id={{}}".format
    # 获取用户发布的视频列表
    USER_PUBLISHED_VIDEOS = f"{BASE_URL}/aweme/v1/aweme/post/?user_id={{}}&cursor={{}}&count={{}}".format
    # 获取用户喜欢的视频列表
    USER_LIKED_VIDEOS = f"{BASE_URL}/aweme/v1/aweme/favorite/?user_id={{}}&cursor={{}}&count={{}}".format

    # 推荐相关API
    # 获取推荐视频
    RECOMMENDED_VIDEOS = f"{BASE_URL}/aweme/v1/feed/?type=0&max_cursor={{}}&count={{}}".format
    # 获取热门视频
    HOT_VIDEOS = f"{BASE_URL}/aweme/v1/hot/search/video/list/?cursor={{}}&count={{}}".format

    # 搜索相关API
    # 搜索视频
    SEARCH_VIDEOS = f"{BASE_URL}/aweme/v1/search/item/?keyword={{}}&offset={{}}&count={{}}".format
    # 搜索用户
    SEARCH_USERS = f"{BASE_URL}/aweme/v1/search/user/?keyword={{}}&offset={{}}&count={{}}".format

    # 分类相关API
    # 获取视频分类列表
    VIDEO_CATEGORIES = f"{BASE_URL}/aweme/v1/category/list/".format
    # 获取分类下的视频列表
    CATEGORY_VIDEOS = f"{BASE_URL}/aweme/v1/aweme/category/?category_id={{}}&cursor={{}}&count={{}}".format

    # H5相关API
    # H5视频详情页
    H5_VIDEO_DETAIL = f"{H5_BASE_URL}/item/video/{{}}".format
    # H5用户主页
    H5_USER_PROFILE = f"{H5_BASE_URL}/user/profile/{{}}".format

    # 其他API
    # 获取APP配置
    APP_CONFIG = f"{BASE_URL}/aweme/v1/config/?fp={{}}&iid={{}}&device_id={{}}&os_version={{}}&app_name=aweme&version_code={{}}&device_type={{}}&device_brand={{}}&aid={{}}".format