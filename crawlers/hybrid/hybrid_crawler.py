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
# 　　　　 　　  ＿＿
# 　　　 　　 ／＞　　フ
# 　　　 　　| 　_　 _ l
# 　 　　 　／` ミ＿xノ
# 　　 　 /　　　 　 |       Feed me Stars ⭐ ️
# 　　　 /　 ヽ　　 ﾉ
# 　 　 │　　|　|　|
# 　／￣|　　 |　|　|
# 　| (￣ヽ＿_ヽ_)__)
# 　＼二つ
# ==============================================================================
#
# Contributor Link:
# - https://github.com/Evil0ctal
#
# ==============================================================================

import asyncio
import re
import httpx

from crawlers.douyin.web.web_crawler import DouyinWebCrawler  # 导入抖音Web爬虫
from crawlers.tiktok.web.web_crawler import TikTokWebCrawler  # 导入TikTok Web爬虫
from crawlers.tiktok.app.app_crawler import TikTokAPPCrawler  # 导入TikTok App爬虫
from crawlers.bilibili.web.web_crawler import BilibiliWebCrawler  # 导入Bilibili Web爬虫
from crawlers.kuaishou.web.web_crawler import KuaiShouWebCrawler  # 导入快手Web爬虫
from crawlers.xiaohongshu.web.web_crawler import XiaoHongShuWebCrawler  # 导入小红书Web爬虫


class HybridCrawler:
    def __init__(self):
        self.DouyinWebCrawler = DouyinWebCrawler()
        self.TikTokWebCrawler = TikTokWebCrawler()
        self.TikTokAPPCrawler = TikTokAPPCrawler()
        self.BilibiliWebCrawler = BilibiliWebCrawler()
        self.KuaiShouWebCrawler = KuaiShouWebCrawler()
        self.XiaoHongShuWebCrawler = XiaoHongShuWebCrawler()

    async def get_bilibili_bv_id(self, url: str) -> str:
        """
        从 Bilibili URL 中提取 BV 号，支持短链重定向
        """
        # 如果是 b23.tv 短链，需要重定向获取真实URL
        if "b23.tv" in url:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, follow_redirects=True)
                url = str(response.url)
        
        # 从URL中提取BV号
        bv_pattern = r'(?:video\/|\/)(BV[A-Za-z0-9]+)'
        match = re.search(bv_pattern, url)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Cannot extract BV ID from URL: {url}")

    async def get_weibo_headers(self):
        """获取微博的headers"""
        return {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Referer": "https://weibo.com/",
                "Cookie": "SUB=_2AkMVpM6Xf8NxqwJRmP4TzmPgaoyH-jyYsmR9An7uJhMyAxgv7X9jqmgMbt-R6ARqFk7m9bA1wL0Cye20xT6cFgJ34e0H",
                "X-Requested-With": "XMLHttpRequest"
            }
        }

    async def hybrid_parsing_single_video(self, url: str, minimal: bool = False):
        # 解析抖音视频/Parse Douyin video
        if "douyin" in url:
            platform = "douyin"
            aweme_id = await self.DouyinWebCrawler.get_aweme_id(url)
            data = await self.DouyinWebCrawler.fetch_one_video(aweme_id)
            data = data.get("aweme_detail")
            # $.aweme_detail.aweme_type
            aweme_type = data.get("aweme_type")
        # 解析TikTok视频/Parse TikTok video
        elif "tiktok" in url:
            platform = "tiktok"
            aweme_id = await self.TikTokWebCrawler.get_aweme_id(url)

            # 2024-09-14: Switch to TikTokAPPCrawler instead of TikTokWebCrawler
            # data = await self.TikTokWebCrawler.fetch_one_video(aweme_id)
            # data = data.get("itemInfo").get("itemStruct")

            data = await self.TikTokAPPCrawler.fetch_one_video(aweme_id)
            # $.imagePost exists if aweme_type is photo
            aweme_type = data.get("aweme_type")
        # 解析Bilibili视频/Parse Bilibili video
        elif "bilibili" in url or "b23.tv" in url:
            platform = "bilibili"
            aweme_id = await self.get_bilibili_bv_id(url)  # BV号作为统一的video_id
            response = await self.BilibiliWebCrawler.fetch_one_video(aweme_id)
            data = response.get('data', {})  # 提取data部分
            # Bilibili只有视频类型，aweme_type设为0(video)
            aweme_type = 0
        # 解析快手视频/Parse Kuaishou video
        elif "kuaishou" in url:
            platform = "kuaishou"
            # 使用快手爬虫的fetch_video_from_url方法处理视频URL
            response = await self.KuaiShouWebCrawler.fetch_video_from_url(url)
            # 提取视频数据
            vision_video_detail = response.get('data', {}).get('visionVideoDetail', {})
            # 提取author和photo信息
            author = vision_video_detail.get('author', {})
            photo = vision_video_detail.get('photo', {})
            # 构建统一的数据格式
            data = {
                'author': author,
                'photo': photo,
                # 添加platform字段以便后续处理
                'platform': 'kuaishou'
            }
            # 快手视频类型，设为0(video)
            aweme_type = 0
        # 解析小红书视频/Parse XiaoHongShu video
        elif "xiaohongshu" in url or "xhslink" in url:
            platform = "xiaohongshu"
            
            try:
                # 尝试使用API方法处理视频URL
                response = await self.XiaoHongShuWebCrawler.fetch_note_from_url(url)
                # 提取笔记数据
                data = response.get('data', {})
            except Exception as e:
                print(f"小红书API调用失败: {e}")
                print("尝试通过HTML解析获取视频数据...")
                
                # 使用HTML解析作为备用方案
                import httpx
                import json
                
                # 处理短链接重定向
                if "xhslink.com" in url:
                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        response = await client.get(url)
                        url = str(response.url)
                
                # 获取HTML内容
                async with httpx.AsyncClient() as client:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                        "Referer": "https://www.xiaohongshu.com/"
                    }
                    response = await client.get(url, headers=headers)
                    html_content = response.text
                
                # 提取INITIAL_STATE
                # 使用更灵活的正则表达式，匹配从window.__INITIAL_STATE__开始到下一个window.或</script>标签结束
                pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?})(?=window\.|</script>|$)'  
                match = re.search(pattern, html_content, re.DOTALL)
                
                # 初始化data变量
                data = {'note': {}}
                
                if match:
                    initial_state_str = match.group(1)
                    # 修复JSON中的undefined值
                    initial_state_str = initial_state_str.replace('undefined', 'null')
                    
                    try:
                        initial_state = json.loads(initial_state_str)
                        
                        # 从INITIAL_STATE中提取note数据
                        # 检查多种可能的笔记数据路径
                        html_note = {}
                        note_found = False
                        
                        # 路径1: note.noteDetailMap
                        if 'note' in initial_state and 'noteDetailMap' in initial_state['note']:
                            note_detail_map = initial_state['note']['noteDetailMap']
                            if note_detail_map:
                                # 获取第一个笔记数据
                                note_id, note_detail = next(iter(note_detail_map.items()))
                                html_note = note_detail.get('note', {})
                                note_found = True
                                print(f"成功从HTML中提取笔记数据: {note_id}")
                        # 路径2: common.noteDetailMap
                        elif 'common' in initial_state and 'noteDetailMap' in initial_state['common']:
                            note_detail_map = initial_state['common']['noteDetailMap']
                            if note_detail_map:
                                # 获取第一个笔记数据
                                note_id, note_detail = next(iter(note_detail_map.items()))
                                html_note = note_detail.get('note', {})
                                note_found = True
                                print(f"成功从HTML中提取笔记数据: {note_id}")
                        # 路径3: 直接的note路径
                        elif 'note' in initial_state:
                            html_note = initial_state.get('note', {})
                            note_found = True
                            print(f"成功从HTML中提取笔记数据")
                        
                        if note_found:
                            # 保持与API响应相同的结构
                            data = {'note': html_note}
                        else:
                            print("未找到笔记数据")
                    except json.JSONDecodeError as e:
                        print(f"JSON解析失败: {e}")
                else:
                    print("未找到INITIAL_STATE")
            
            # 小红书只有视频，设为0(video)
            aweme_type = 0
        # 解析微博视频/Parse Weibo video
        elif "weibo" in url or "t.cn" in url:
            platform = "weibo"
            
            # 提取视频ID
            video_id = ""
            # 从URL中提取视频ID
            fid_pattern = r'fid=1034:([a-zA-Z0-9]+)'
            fid_match = re.search(fid_pattern, url)
            if fid_match:
                video_id = fid_match.group(1)
            elif "tv/show/" in url:
                # 处理格式为https://weibo.com/tv/show/1034:5245644953288730的URL
                show_pattern = r'tv/show/1034:([a-zA-Z0-9]+)'
                show_match = re.search(show_pattern, url)
                if show_match:
                    video_id = show_match.group(1)
            
            if not video_id:
                # 尝试处理短链接
                if "t.cn" in url:
                    import httpx
                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        response = await client.get(url)
                        final_url = str(response.url)
                        # 从重定向后的URL中提取视频ID
                        show_match = re.search(r'tv/show/1034:([a-zA-Z0-9]+)', final_url)
                        if show_match:
                            video_id = show_match.group(1)
                        else:
                            fid_match = re.search(r'fid=1034:([a-zA-Z0-9]+)', final_url)
                            if fid_match:
                                video_id = fid_match.group(1)
            
            if not video_id:
                raise ValueError("无法从URL中提取微博视频ID")
            
            # 调用微博视频播放API
            import httpx
            import json
            direct_api_url = f"https://weibo.com/tv/api/component?page=/tv/show/{video_id}&type=mp4"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Referer": "https://weibo.com/",
                "Cookie": "SUB=_2AkMVpM6Xf8NxqwJRmP4TzmPgaoyH-jyYsmR9An7uJhMyAxgv7X9jqmgMbt-R6ARqFk7m9bA1wL0Cye20xT6cFgJ34e0H",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest"
            }
            payload = {
                "data": json.dumps({
                    "Component_Play_Playinfo": {
                        "oid": f"1034:{video_id}",
                        "plid": "",
                        "quality": 4,
                        "isHttps": 1,
                        "cType": 12
                    }
                })
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(direct_api_url, headers=headers, data=payload)
                api_data = json.loads(response.text)
                
                if api_data.get("code") != "100000":
                    raise ValueError(f"微博API调用失败: {api_data.get('msg')}")
                
                # 提取视频数据
                data = api_data["data"]["Component_Play_Playinfo"]
            
            # 微博只有视频，设为0(video)
            aweme_type = 0
        else:
            raise ValueError("hybrid_parsing_single_video: Cannot judge the video source from the URL.")

        # 检查是否需要返回最小数据/Check if minimal data is required
        if not minimal:
            return data

        # 如果是最小数据，处理数据/If it is minimal data, process the data
        url_type_code_dict = {
            # common
            0: 'video',
            # Douyin
            2: 'image',
            4: 'video',
            68: 'image',
            # TikTok
            51: 'video',
            55: 'video',
            58: 'video',
            61: 'video',
            150: 'image'
        }
        # 判断链接类型/Judge link type
        url_type = url_type_code_dict.get(aweme_type, 'video')
        # print(f"url_type: {url_type}")

        """
        以下为(视频||图片)数据处理的四个方法,如果你需要自定义数据处理请在这里修改.
        The following are four methods of (video || image) data processing. 
        If you need to customize data processing, please modify it here.
        """

        """
        创建已知数据字典(索引相同)，稍后使用.update()方法更新数据
        Create a known data dictionary (index the same), 
        and then use the .update() method to update the data
        """

        # 根据平台适配字段映射
        if platform == 'bilibili':
            result_data = {
                'type': url_type,
                'platform': platform,
                'video_id': aweme_id,
                'desc': data.get("title"),  # Bilibili使用title
                'create_time': data.get("pubdate"),  # Bilibili使用pubdate
                'author': data.get("owner"),  # Bilibili使用owner
                'music': None,  # Bilibili没有音乐信息
                'statistics': data.get("stat"),  # Bilibili使用stat
                'cover_data': {},  # 将在各平台处理中填充
                'hashtags': None,  # Bilibili没有hashtags概念
            }
        elif platform == 'kuaishou':
            author_info = data.get("author", {})
            result_data = {
                'type': url_type,
                'platform': platform,
                'video_id': data.get("photo", {}).get("id"),  # 快手使用photo.id作为视频ID
                'desc': data.get("photo", {}).get("caption"),  # 快手使用photo.caption作为视频描述
                'create_time': data.get("photo", {}).get("timestamp"),  # 快手使用photo.timestamp作为创建时间
                'author_id': author_info.get("id"),  # 作者ID
                'author_name': author_info.get("name"),  # 作者昵称
                'author': author_info,  # 保留原始作者信息
                'music': None,  # 快手没有音乐信息
                'statistics': {
                    'likeCount': data.get("photo", {}).get("likeCount"),
                    'viewCount': data.get("photo", {}).get("viewCount")
                },  # 快手统计信息
                'cover_data': {},  # 将在各平台处理中填充
                'hashtags': None,  # 快手没有hashtags概念
                # 预定义视频下载链接字段
                'wm_video_url': None,
                'nwm_video_url': None
            }
        elif platform == 'xiaohongshu':
            note_data = data  # 小红书的数据直接是note_data
            note = note_data.get("note", {})
            author_info = note.get("user", {})
            result_data = {
                'type': url_type,
                'platform': platform,
                'video_id': note.get("noteId"),  # 小红书使用noteId作为视频ID
                'desc': note.get("desc"),  # 小红书使用desc作为视频描述
                'create_time': note.get("time"),  # 小红书使用time作为创建时间
                'author_id': author_info.get("userId"),  # 作者ID
                'author_name': author_info.get("nickname"),  # 作者昵称
                'author': author_info,  # 保留原始作者信息
                'music': None,  # 小红书没有音乐信息
                'statistics': {
                    'likeCount': note.get("interactInfo", {}).get("likedCount"),
                    'commentCount': note.get("interactInfo", {}).get("commentCount"),
                    'shareCount': note.get("interactInfo", {}).get("shareCount"),
                    'collectedCount': note.get("interactInfo", {}).get("collectedCount")
                },  # 小红书统计信息
                'cover_data': {},  # 将在各平台处理中填充
                'hashtags': None,  # 小红书没有hashtags概念
                # 预定义视频下载链接字段
                'wm_video_url': None,
                'nwm_video_url': None
            }
        elif platform == 'weibo':
            # 微博数据处理
            result_data = {
                'type': url_type,
                'platform': platform,
                'video_id': data.get("media_id", ""),  # 微博使用media_id作为视频ID
                'desc': data.get("title", ""),  # 微博使用title作为视频描述
                'create_time': data.get("real_date", 0),  # 微博使用real_date作为创建时间
                'author_id': data.get("author_id", ""),  # 作者ID
                'author_name': data.get("nickname", ""),  # 作者昵称
                'author': {
                    'uid': data.get("author_id", ""),
                    'nickname': data.get("nickname", ""),
                    'avatar': data.get("avatar", ""),
                    'verified': data.get("verified", False),
                    'verified_reason': data.get("verified_reason", "")
                },  # 保留原始作者信息
                'music': None,  # 微博没有直接的音乐信息
                'statistics': {
                    'likeCount': data.get("attitudes_count", 0),
                    'commentCount': data.get("comments_count", 0),
                    'shareCount': data.get("reposts_count", 0),
                    'viewCount': data.get("play_count", 0)
                },  # 微博统计信息
                'cover_data': {},  # 将在各平台处理中填充
                'hashtags': [],  # 微博有话题标签
                # 预定义视频下载链接字段
                'wm_video_url': None,
                'nwm_video_url': None
            }
            
            # 提取话题标签
            if "text" in data:
                hashtag_pattern = re.compile(r'#([^#\s]+)#')
                hashtags = hashtag_pattern.findall(data["text"])
                if hashtags:
                    result_data['hashtags'] = []
                    for index, tag in enumerate(hashtags):
                        result_data['hashtags'].append({
                            'name': tag,
                            'type': 0
                        })
        else:
            author_info = data.get("author", {})
            result_data = {
                'type': url_type,
                'platform': platform,
                'video_id': aweme_id,  # 统一使用video_id字段，内容可能是aweme_id或bv_id
                'desc': data.get("desc"),
                'create_time': data.get("create_time"),
                'author_id': author_info.get("uid"),  # 作者ID
                'author_name': author_info.get("nickname"),  # 作者昵称
                'author': author_info,  # 保留原始作者信息
                'music': data.get("music"),
                'statistics': data.get("statistics"),
                'cover_data': {},  # 将在各平台处理中填充
                'hashtags': data.get('text_extra'),
                # 预定义视频下载链接字段
                'wm_video_url': None,
                'nwm_video_url': None
            }
        # 创建一个空变量，稍后使用.update()方法更新数据/Create an empty variable and use the .update() method to update the data
        api_data = None
        # 判断链接类型并处理数据/Judge link type and process data
        # 抖音数据处理/Douyin data processing
        if platform == 'douyin':
            # 填充封面数据
            result_data['cover_data'] = {
                'cover': data.get("video", {}).get("cover"),
                'origin_cover': data.get("video", {}).get("origin_cover"),
                'dynamic_cover': data.get("video", {}).get("dynamic_cover")
            }
            # 抖音视频数据处理/Douyin video data processing
            if url_type == 'video':
                # 将信息储存在字典中/Store information in a dictionary
                uri = data['video']['play_addr']['uri']
                wm_video_url_HQ = data['video']['play_addr']['url_list'][0]
                wm_video_url = f"https://aweme.snssdk.com/aweme/v1/playwm/?video_id={uri}&radio=1080p&line=0"
                nwm_video_url_HQ = wm_video_url_HQ.replace('playwm', 'play')
                nwm_video_url = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={uri}&ratio=1080p&line=0"
                
                # 将视频下载链接直接添加到result_data中
                result_data['wm_video_url'] = wm_video_url
                result_data['nwm_video_url'] = nwm_video_url
                
                api_data = {
                    'video_data':
                        {
                            'wm_video_url': wm_video_url,
                            'wm_video_url_HQ': wm_video_url_HQ,
                            'nwm_video_url': nwm_video_url,
                            'nwm_video_url_HQ': nwm_video_url_HQ
                        }
                }
            # 抖音图片数据处理/Douyin image data processing
            elif url_type == 'image':
                # 无水印图片列表/No watermark image list
                no_watermark_image_list = []
                # 有水印图片列表/With watermark image list
                watermark_image_list = []
                # 遍历图片列表/Traverse image list
                for i in data['images']:
                    no_watermark_image_list.append(i['url_list'][0])
                    watermark_image_list.append(i['download_url_list'][0])
                api_data = {
                    'image_data':
                        {
                            'no_watermark_image_list': no_watermark_image_list,
                            'watermark_image_list': watermark_image_list
                        }
                }
        # TikTok数据处理/TikTok data processing
        elif platform == 'tiktok':
            # 填充封面数据
            result_data['cover_data'] = {
                'cover': data.get("video", {}).get("cover"),
                'origin_cover': data.get("video", {}).get("origin_cover"),
                'dynamic_cover': data.get("video", {}).get("dynamic_cover")
            }
            # TikTok视频数据处理/TikTok video data processing
            if url_type == 'video':
                # 将信息储存在字典中/Store information in a dictionary
                # wm_video = data['video']['downloadAddr']
                # wm_video = data['video']['download_addr']['url_list'][0]
                wm_video = (
                    data.get('video', {})
                    .get('download_addr', {})
                    .get('url_list', [None])[0]
                )
                nwm_video = data['video']['play_addr']['url_list'][0]

                # 将视频下载链接直接添加到result_data中
                result_data['wm_video_url'] = wm_video
                result_data['nwm_video_url'] = nwm_video

                api_data = {
                    'video_data':
                        {
                            'wm_video_url': wm_video,
                            'wm_video_url_HQ': wm_video,
                            # 'nwm_video_url': data['video']['playAddr'],
                            'nwm_video_url': nwm_video,
                            # 'nwm_video_url_HQ': data['video']['bitrateInfo'][0]['PlayAddr']['UrlList'][0]
                            'nwm_video_url_HQ': data['video']['bit_rate'][0]['play_addr']['url_list'][0]
                        }
                }
            # TikTok图片数据处理/TikTok image data processing
            elif url_type == 'image':
                # 无水印图片列表/No watermark image list
                no_watermark_image_list = []
                # 有水印图片列表/With watermark image list
                watermark_image_list = []
                for i in data['image_post_info']['images']:
                    no_watermark_image_list.append(i['display_image']['url_list'][0])
                    watermark_image_list.append(i['owner_watermark_image']['url_list'][0])
                api_data = {
                    'image_data':
                        {
                            'no_watermark_image_list': no_watermark_image_list,
                            'watermark_image_list': watermark_image_list
                        }
                }
        # Bilibili数据处理/Bilibili data processing
        elif platform == 'bilibili':
            # 填充封面数据
            result_data['cover_data'] = {
                'cover': data.get("pic"),  # Bilibili使用pic作为封面
                'origin_cover': data.get("pic"),
                'dynamic_cover': data.get("pic")
            }
            # Bilibili只有视频，直接处理视频数据
            if url_type == 'video':
                # 尝试从数据中直接提取视频URL（适用于开源解析引擎返回的数据）
                video_url = None
                audio_url = None
                nwm_video_url_HQ = None
                
                # 检查是否有直接的视频URL字段
                if 'video_url' in data:
                    potential_url = data.get('video_url')
                    # 验证是否为视频URL（检查文件扩展名）
                    if potential_url and any(ext in potential_url.lower() for ext in ['.mp4', '.flv', '.avi', '.mov', '.wmv', '.mkv']):
                        video_url = potential_url
                        nwm_video_url_HQ = video_url
                elif 'videoUrl' in data:
                    potential_url = data.get('videoUrl')
                    # 验证是否为视频URL（检查文件扩展名）
                    if potential_url and any(ext in potential_url.lower() for ext in ['.mp4', '.flv', '.avi', '.mov', '.wmv', '.mkv']):
                        video_url = potential_url
                        nwm_video_url_HQ = video_url
                elif 'url' in data:
                    potential_url = data.get('url')
                    # 验证是否为视频URL（检查文件扩展名）
                    if potential_url and any(ext in potential_url.lower() for ext in ['.mp4', '.flv', '.avi', '.mov', '.wmv', '.mkv']):
                        video_url = potential_url
                        nwm_video_url_HQ = video_url
                
                # 如果没有直接的视频URL，尝试使用Bilibili API获取
                if not video_url:
                    # 获取视频播放地址需要额外调用API
                    cid = data.get('cid')  # 获取cid
                    # 如果没有cid，尝试重新获取视频详情
                    if not cid:
                        try:
                            # 重新获取视频详情，尝试获取cid
                            video_detail = await self.BilibiliWebCrawler.fetch_one_video(aweme_id)
                            cid = video_detail.get('data', {}).get('cid')
                        except Exception as e:
                            print(f"Failed to get cid for Bilibili video: {e}")
                    
                    if cid:
                        # 获取播放链接，cid需要转换为字符串
                        playurl_data = await self.BilibiliWebCrawler.fetch_video_playurl(aweme_id, str(cid))
                        # 从播放数据中提取URL
                        dash = playurl_data.get('data', {}).get('dash', {})
                        video_list = dash.get('video', [])
                        audio_list = dash.get('audio', [])
                        
                        # 选择最高质量的视频流
                        # 按视频分辨率(宽*高)从高到低排序
                        sorted_video_list = sorted(video_list, 
                                                  key=lambda x: (x.get('width', 0) * x.get('height', 0), x.get('bandwidth', 0)), 
                                                  reverse=True) if video_list else []
                        
                        # 按音频带宽从高到低排序
                        sorted_audio_list = sorted(audio_list, key=lambda x: x.get('bandwidth', 0), reverse=True) if audio_list else []
                        
                        # 选择最高质量的视频和音频
                        video_url = sorted_video_list[0].get('baseUrl') if sorted_video_list else None
                        audio_url = sorted_audio_list[0].get('baseUrl') if sorted_audio_list else None
                        
                        # 选择次高质量的视频作为无水印HQ链接（如果有多个质量）
                        nwm_video_url_HQ = sorted_video_list[1].get('baseUrl') if len(sorted_video_list) > 1 else video_url
                
                # 将视频下载链接直接添加到result_data中，与抖音格式保持一致
                result_data['wm_video_url'] = video_url  # Bilibili没有水印概念
                result_data['nwm_video_url'] = video_url  # Bilibili没有水印概念
                
                # 构建api_data
                if video_url:
                    api_data = {
                        'video_data': {
                            'wm_video_url': video_url,  # Bilibili没有水印概念
                            'wm_video_url_HQ': video_url,  # Bilibili没有水印概念
                            'nwm_video_url': video_url,  # 无水印链接
                            'nwm_video_url_HQ': nwm_video_url_HQ,  # 无水印高清链接
                            'audio_url': audio_url,  # Bilibili音视频分离
                            'cid': data.get('cid'),  # 保存cid供后续使用
                        }
                    }
                else:
                    api_data = {
                        'video_data': {
                            'wm_video_url': None,
                            'wm_video_url_HQ': None,
                            'nwm_video_url': None,
                            'nwm_video_url_HQ': None,
                            'audio_url': None,
                            'error': 'Failed to get video URL for Bilibili video'
                        }
                    }
        # 小红书数据处理/XiaoHongShu data processing
        elif platform == 'xiaohongshu':
            note = data.get("note", {})
            # 填充封面数据
            cover_url = ""
            # 尝试从imageList获取封面
            if "imageList" in note and note["imageList"]:
                cover_url = note["imageList"][0].get("urlDefault", "")
            # 如果没有imageList，尝试从video的thumbnail获取封面
            elif "video" in note and "image" in note["video"]:
                cover_url = note["video"]["image"].get("thumbnailFileid", "")
                if cover_url and not cover_url.startswith("http"):
                    # 如果是thumbnailFileid格式，转换为完整URL
                    cover_url = f"http://sns-webpic-qc.xhscdn.com/frame/110/0/{cover_url}"
            result_data['cover_data'] = {
                'cover': cover_url,
                'origin_cover': cover_url,
                'dynamic_cover': cover_url
            }
            # 小红书只有视频，直接处理视频数据
            if url_type == 'video':
                # 从视频数据中提取视频URL
                video_url = ""
                if "video" in note and "media" in note["video"]:
                    media = note["video"]["media"]
                    if "stream" in media:
                        stream = media["stream"]
                        # 小红书视频URL存储在stream.h264[0].masterUrl中
                        if isinstance(stream, dict) and "h264" in stream and stream["h264"]:
                            video_url = stream["h264"][0].get("masterUrl", "")
                        elif isinstance(stream, str):
                            video_url = stream
                
                # 将视频下载链接直接添加到result_data中，与抖音格式保持一致
                result_data['wm_video_url'] = video_url
                result_data['nwm_video_url'] = video_url  # 小红书视频URL通常已无水印
                
                # 模拟抖音的视频数据结构，包含所有相关字段
                wm_video_url = video_url
                wm_video_url_HQ = video_url
                nwm_video_url = video_url  # 小红书视频URL通常已无水印
                nwm_video_url_HQ = video_url
                
                # 保持api_data结构与抖音完全一致
                api_data = {
                    'video_data': {
                        'wm_video_url': wm_video_url,
                        'wm_video_url_HQ': wm_video_url_HQ,
                        'nwm_video_url': nwm_video_url,
                        'nwm_video_url_HQ': nwm_video_url_HQ
                    }
                }
        # 快手数据处理/Kuaishou data processing
        elif platform == 'kuaishou':
            # 获取封面URL
            cover_url = data.get("photo", {}).get("coverUrl")
            # 填充封面数据，与抖音格式保持一致
            result_data['cover_data'] = {
                'cover': {
                    'height': 640,
                    'uri': cover_url.split('/')[-1].split('?')[0],
                    'url_list': [cover_url, cover_url],
                    'width': 360
                },
                'origin_cover': {
                    'height': 640,
                    'uri': cover_url.split('/')[-1].split('?')[0],
                    'url_list': [cover_url, cover_url],
                    'width': 360
                },
                'dynamic_cover': {
                    'height': 720,
                    'uri': cover_url.split('/')[-1].split('?')[0],
                    'url_list': [cover_url, cover_url],
                    'width': 720
                }
            }
            # 从视频描述中提取hashtags
            caption = data.get("photo", {}).get("caption", "")
            if caption:
                # 匹配#话题标签
                hashtag_pattern = re.compile(r'#([^#\s]+)')
                hashtags = hashtag_pattern.findall(caption)
                if hashtags:
                    result_data['hashtags'] = []
                    for index, tag in enumerate(hashtags):
                        # 查找标签在描述中的位置
                        start_pos = caption.find(f"#{tag}")
                        end_pos = start_pos + len(tag) + 1
                        result_data['hashtags'].append({
                            'caption_end': end_pos,
                            'caption_start': start_pos,
                            'end': end_pos,
                            'sec_uid': f"kuaishou_hashtag_{index}",
                            'start': start_pos,
                            'type': 0,
                            'user_id': "0"
                        })
            # 快手只有视频，直接处理视频数据
            if url_type == 'video':
                # 从API响应中提取视频URL
                photo_data = data.get('photo', {})
                
                # 使用正确的字段名获取视频URL
                video_url = photo_data.get('photoUrl')
                
                # 将视频下载链接直接添加到result_data中，与抖音格式保持一致
                result_data['wm_video_url'] = video_url
                result_data['nwm_video_url'] = video_url  # 快手视频URL通常已无水印
                
                # 模拟抖音的视频数据结构，包含所有相关字段
                wm_video_url = video_url
                wm_video_url_HQ = video_url
                nwm_video_url = video_url  # 快手视频URL通常已无水印
                nwm_video_url_HQ = video_url
                
                # 保持api_data结构与抖音完全一致
                api_data = {
                    'video_data': {
                        'wm_video_url': wm_video_url,
                        'wm_video_url_HQ': wm_video_url_HQ,
                        'nwm_video_url': nwm_video_url,
                        'nwm_video_url_HQ': nwm_video_url_HQ
                    }
                }
        # 微博数据处理/Weibo data processing
        elif platform == 'weibo':
            # 填充封面数据
            cover_url = data.get("cover_image", "")
            # 确保封面URL格式正确（添加协议）
            if cover_url and cover_url.startswith("//"):
                cover_url = f"https:{cover_url}"
            # 强制将HTTP转换为HTTPS以提高兼容性
            if cover_url and cover_url.startswith("http:"):
                cover_url = cover_url.replace("http:", "https:")
            result_data['cover_data'] = {
                'cover': cover_url,
                'origin_cover': cover_url,
                'dynamic_cover': cover_url
            }
            
            # 微博只有视频，直接处理视频数据
            if url_type == 'video':
                # 从视频数据中提取视频URL
                video_url = ""
                wm_video_url = ""
                nwm_video_url = ""
                wm_video_url_HQ = ""
                nwm_video_url_HQ = ""
                
                # 从urls字段中提取视频URL
                if "urls" in data and isinstance(data["urls"], dict):
                    # 获取720P高清视频URL
                    if "高清 720P" in data["urls"]:
                        nwm_video_url_HQ = data["urls"]["高清 720P"]
                    elif "标清 480P" in data["urls"]:
                        nwm_video_url_HQ = data["urls"]["标清 480P"]
                    
                    # 获取标清视频URL（作为备用）
                    if "标清 480P" in data["urls"]:
                        nwm_video_url = data["urls"]["标清 480P"]
                    
                    # 如果没有找到其他URL，使用stream_url
                    if not nwm_video_url_HQ and "stream_url" in data:
                        nwm_video_url_HQ = data["stream_url"]
                        nwm_video_url = data["stream_url"]
                
                # 确保视频URL格式正确（添加协议）
                if nwm_video_url and nwm_video_url.startswith("//"):
                    nwm_video_url = f"https:{nwm_video_url}"
                if nwm_video_url_HQ and nwm_video_url_HQ.startswith("//"):
                    nwm_video_url_HQ = f"https:{nwm_video_url_HQ}"
                
                # 强制将HTTP转换为HTTPS以提高兼容性
                if nwm_video_url and nwm_video_url.startswith("http:"):
                    nwm_video_url = nwm_video_url.replace("http:", "https:")
                if nwm_video_url_HQ and nwm_video_url_HQ.startswith("http:"):
                    nwm_video_url_HQ = nwm_video_url_HQ.replace("http:", "https:")
                
                # 微博视频URL通常已无水印，但为了保持与其他平台一致，我们将其同时赋值给两个字段
                result_data['wm_video_url'] = nwm_video_url_HQ
                result_data['nwm_video_url'] = nwm_video_url_HQ
                
                # 模拟抖音的视频数据结构，包含所有相关字段
                wm_video_url = nwm_video_url_HQ
                wm_video_url_HQ = nwm_video_url_HQ
                
                # 保持api_data结构与抖音完全一致
                api_data = {
                    'video_data': {
                        'wm_video_url': wm_video_url,
                        'wm_video_url_HQ': wm_video_url_HQ,
                        'nwm_video_url': nwm_video_url_HQ,
                        'nwm_video_url_HQ': nwm_video_url_HQ
                    }
                }
        # 更新数据/Update data
        result_data.update(api_data)
        return result_data

    async def main(self):
        # 测试混合解析单一视频接口/Test hybrid parsing single video endpoint
        # url = "https://v.douyin.com/L4FJNR3/"
        # url = "https://www.tiktok.com/@taylorswift/video/7359655005701311786"
        # url = "https://www.tiktok.com/@flukegk83/video/7360734489271700753"
        # url = "https://www.tiktok.com/@minecraft/photo/7369296852669205791"
        url = "https://v.kuaishou.com/n5T01Jd1"
        minimal = True
        result = await self.hybrid_parsing_single_video(url, minimal=minimal)
        print(result)

        # 占位
        pass


if __name__ == '__main__':
    # 实例化混合爬虫/Instantiate hybrid crawler
    hybird_crawler = HybridCrawler()
    # 运行测试代码/Run test code
    asyncio.run(hybird_crawler.main())
