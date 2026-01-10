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


import re


class PhotoIdFetcher:
    """快手视频ID获取器 (KuaiShou Photo ID Fetcher)"""
    
    @staticmethod
    def extract_photo_id_from_url(url: str) -> str:
        """
        从快手视频URL中提取photoId
        Extract photoId from KuaiShou video URL
        
        Args:
            url (str): 快手视频URL
            
        Returns:
            str: 提取到的photoId
        """
        # 匹配快手视频URL的正则表达式
        pattern = r"short-video/([a-zA-Z0-9]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return ""


class UserIdFetcher:
    """快手用户ID获取器 (KuaiShou User ID Fetcher)"""
    
    @staticmethod
    def extract_user_id_from_url(url: str) -> str:
        """
        从快手用户主页URL中提取userId
        Extract userId from KuaiShou user homepage URL
        
        Args:
            url (str): 快手用户主页URL
            
        Returns:
            str: 提取到的userId
        """
        # 匹配快手用户主页URL的正则表达式
        pattern = r"profile/([a-zA-Z0-9_]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return ""


class GraphQLQueryBuilder:
    """GraphQL查询构建器 (GraphQL Query Builder)"""
    
    @staticmethod
    def build_video_detail_query(photo_id: str) -> str:
        """
        构建视频详情的GraphQL查询
        Build GraphQL query for video detail
        
        Args:
            photo_id (str): 视频ID
            
        Returns:
            str: GraphQL查询字符串
        """
        return f"""
        query videoDetail($photoId: String, $type: String, $page: Int, $webPageArea: String) {
          visionVideoDetail(photoId: $photoId, type: $type, page: $page, webPageArea: $webPageArea) {
            status
            type
            author {
              id
              name
              headerUrl
              following
              follower
            }
            photo {
              id
              duration
              caption
              likeCount
              playCount
              commentCount
              shareCount
              timestamp
              coverUrl
              mainUrl
              tags {
                name
              }
            }
          }
        }
        """
    
    @staticmethod
    def build_user_profile_query(user_id: str) -> str:
        """
        构建用户资料的GraphQL查询
        Build GraphQL query for user profile
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            str: GraphQL查询字符串
        """
        return f"""
        query userProfile($userId: String, $pcursor: String, $page: Int, $webPageArea: String) {
          visionProfile(userId: $userId, pcursor: $pcursor, page: $page, webPageArea: $webPageArea) {
            status
            user {
              id
              name
              headerUrl
              bio
              following
              follower
              photo
              likedPhoto
              photoPublished
            }
          }
        }
        """
    
    @staticmethod
    def build_user_works_query() -> str:
        """
        构建用户作品的GraphQL查询
        Build GraphQL query for user works
        
        Returns:
            str: GraphQL查询字符串
        """
        return f"""
        query visionProfilePhotoList($userId: String, $pcursor: String, $page: Int, $webPageArea: String) {
          visionProfilePhotoList(userId: $userId, pcursor: $pcursor, page: $page, webPageArea: $webPageArea) {
            result
            llsid
            pcursor
            hasMore
            list {
              id
              duration
              caption
              likeCount
              playCount
              commentCount
              shareCount
              timestamp
              coverUrl
              mainUrl
              tags {
                name
              }
            }
          }
        }
        """
    
    @staticmethod
    def build_user_likes_query() -> str:
        """
        构建用户喜欢的GraphQL查询
        Build GraphQL query for user likes
        
        Returns:
            str: GraphQL查询字符串
        """
        return f"""
        query visionProfileLikedPhotoList($userId: String, $pcursor: String, $page: Int, $webPageArea: String) {
          visionProfileLikedPhotoList(userId: $userId, pcursor: $pcursor, page: $page, webPageArea: $webPageArea) {
            result
            llsid
            pcursor
            hasMore
            list {
              id
              duration
              caption
              likeCount
              playCount
              commentCount
              shareCount
              timestamp
              coverUrl
              mainUrl
              tags {
                name
              }
            }
          }
        }
        """