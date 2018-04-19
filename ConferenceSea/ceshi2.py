# coding=utf-8
import requests
from lxml import etree
import random
from User_Agent import User_Agent
from config import logger
class Spider:
    def find_speaker(self, id=5973):
        # 查找每个会议的发言人
        # view_all的链接
        post_data = {
            "orgSpeakersData": "ok",
            "spr_type": "organizer_speaker",
            "organizer_id": id,
            "conftype": "Speaking At Organizer's Conferences"
        }
        post_url = "https://www.emedevents.com/view-all"
        times = 1
        headers={}
        headers['User-Agent'] = random.choice(User_Agent)
        self.headers = headers
        session = requests.session()
        while times < 4:
            times += 1
            try:
                response = session.post(post_url, data=post_data, headers=headers, timeout=10)
                break
            except Exception as e:
                logger.error(e)
                response = None
                # logger.error(self.thread_name + "读取页%d失败" % self.page)
        if not response:
            return
        else:
            speaker_url_list = self.gain_speaker_list(response)
            page = 1
            url = "https://www.emedevents.com/conferences/searchViewMore"
            # 请求下一页的数据
            while True:
                data = {
                    "resultData": "",
                    "page": page,
                    "filter_type": "",
                    "search_type": "speaker",
                    "sort_type": "",
                    "view_all": "1"
                }
                page += 1
                try:
                    response = session.post(url, data=data, headers=self.headers)
                except Exception as e:
                    logger.error(e)
                    response = None
                # 请求失败,直接下一页
                if not response:
                    continue
                li = self.gain_speaker_list(response)
                speaker_url_list.extend(li)
                if not li:
                    break
            # self.save_relationship(speaker_url_list, id)




    def gain_speaker_list(self, response):
        selector = etree.HTML(response.content)
        speaker_url_list = selector.xpath('//div[@class="ellips-wrapper"]/a/h3/../@href')
        name_list = selector.xpath("//h3/text()")
        i = 0
        for url in speaker_url_list:
            print url
            print name_list[i]
            i += 1
        return speaker_url_list

s=Spider()
s.find_speaker()