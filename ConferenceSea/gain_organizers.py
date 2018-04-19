# coding=utf-8
from User_Agent import User_Agent
import requests
from lxml import etree
import threading
from config import logger
import random
import pymysql
import re

class Organizer:
    name = ''
    url = ''
    summary = ''
    organizer_id = ''
    address = ''



class OrganizerSpider:

    def __init__(self, start_page=1, thread_name=None):
        # 起始的url,可以爬取到所有的组织机构信息
        self.start_url = "https://www.emedevents.com/view-all?data[headerSearchForm][search_type]=organizer"
        # 第一次请求用这个user-agent,之后的请求随机选择代理
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Cache-Control": "no-cache",
        }
        self.start_page = start_page
        self.page = self.start_page
        self.thread_name = thread_name
        # # 第一次解析页面的时候查找result,之后就不在找,以此为标记
        # 固定不变的,不用获取了
        # self.flag = True
        self.mysql_cli = pymysql.connect(host="localhost", port=3306, database="conference", user="root", password="mysql", charset="utf8")
        self.cursor = self.mysql_cli.cursor()

    def run(self):
        if self.thread_name:
            print self.thread_name + "开始采集数据"
        print "开始"
        self.start_spider()
        if self.thread_name:
            print self.thread_name + "结束采集"


    def start_spider(self):
        # 第一页
        response = self.get_first_page()
        print "第一页"
        if not response:
            return
        # 获取第一页中的组织链接
        url_list = self.parse_data(response)
        print "拿到首页数据"
        for url in url_list:
            # 遍历,拿到每一个机构的url, 没拿到的话,直接抓取下一个
            response = self.get_detail(url)
            print "拿到组织信息"
            if not response:
                continue
            self.parse_detail(response, url)

        # 获取其他页链接
        while True:
            print "组织第%d页" % self.page
            response = self.get_other_page()
            print "拿到第%d页" % self.page
            self.page += 1
            if not response:
                # 当前页加载失败的话,直接进行下一页的加载
                continue
            url_list = self.parse_data(response)
            if not url_list:
                break
            for url in url_list:
                response = self.get_detail(url)
                if not response:
                    continue
                # 拿到每个会议组织者
                self.parse_detail(response, url)
                # 保存组织者信息
                # self.save_data(data)
                # 改为在解析函数内部执行


    def get_first_page(self):
        times = 1
        while times < 4:
            times += 1
            try:
                response = requests.get(self.start_url)
                # 请求成功,跳出循环
                break
            except Exception as e:
                logger.error(e)
                logger.error(self.thread_name + "打开第一页失败")
                response = None
        return response

    def get_other_page(self):
        # 获取其他页的信息
        times = 1
        print self.page
        page_url = "https://www.emedevents.com/conferences/searchViewMore"
        post_data = {
            "resultData": "YToyOntzOjQ6ImRhdGEiO2E6MTp7czoxNjoiaGVhZGVyU2VhcmNoRm9ybSI7YToxOntzOjExOiJzZWFyY2hfdHlwZSI7czo5OiJvcmdhbml6ZXIiO319czoxNjoiaGVhZGVyU2VhcmNoRm9ybSI7YToxOntzOjExOiJzZWFyY2hfdHlwZSI7czo5OiJvcmdhbml6ZXIiO319",
            "page": self.page,
            "filter_type": "",
            "search_type": "organizer",
            "sort_type": "",
            "view_all": 0
        }

        while times <4:
            times += 1
            headers = self.headers
            headers['User-Agent'] = random.choice(User_Agent)
            try:
                response = requests.post(page_url, data=post_data, headers=headers)
                break
            except Exception as e:
                logger.error(e)
                response = None
                logger.error(self.thread_name + "读取页%d失败" %self.page)
        return response


    def parse_data(self, response):
        content = response.content
        selector = etree.HTML(content)
        url_list = selector.xpath('//div[@class="ellips-wrapper"]/a/@href')
        return url_list

    def get_detail(self, url):
        # 请求会议的详情页
        times = 1
        while times <4:
            times += 1
            headers = self.headers
            headers['User-Agent'] = random.choice(User_Agent)
            try:
                response = requests.get(url, headers=headers)
                break
            except Exception as e:
                logger.error(e)
                logger.error(self.thread_name + "读取页%d失败" %self.page)
                return
        return response


    def parse_detail(self, response, url):

        # 从详情页解析出每一条信息
        organizer = Organizer()
        selector = etree.HTML(response.content)
        name = selector.xpath('//title/text()')[0].strip()
        organizer_id = re.match(r'.*?-(\d+)$', url).group(1)
        address1 = selector.xpath('//div[@class="contact-address"]/div[1]/text()')[0].strip()
        address2 = selector.xpath("//h1/following-sibling::div[1]/text()")[0].strip()
        address = address1 + ' , ' + address2
        summary_list = selector.xpath('//div[@id="Summary"]/p/text()')
        summary = ""
        for s in summary_list:
            s=s.strip()
            summary += s + '\n'
        organizer.summary = summary
        organizer.url = url
        organizer.organizer_id = organizer_id
        organizer.address = address
        organizer.name = name
        # 保存组织者信息
        self.save_data(organizer)
        # 查找是否有发言人,
        self.find_speaker(organizer.organizer_id)

    def find_speaker(self, id):
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
        headers = self.headers
        headers['User-Agent'] = random.choice(User_Agent)
        session = requests.session()
        while times < 4:
            times += 1
            try:
                response = session.post(post_url, data=post_data, headers=headers, timeout=10)
                break
            except Exception as e:
                logger.error(e)
                response = None
                logger.error(self.thread_name + "读取页%d失败" % self.page)
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
            self.save_relationship(speaker_url_list, id)



    def gain_speaker_list(self, response):
        selector = etree.HTML(response.content)
        speaker_url_list = selector.xpath('//div[@class="ellips-wrapper"]/a/h3/../@href')
        # name_list = selector.xpath()
        # for url in speaker_url_list:
        #     print url
        return speaker_url_list


    def save_relationship(self, url_list, or_id):
        """保存组织机构和发言人的关系表
            url_list为发言人的url表
            or_id为数据库中组织机构的id
        """
        try:
            organizer_sql = """select id from organizers where organizer_id = %s""" % or_id
            self.cursor.execute(organizer_sql)
            or_table_id = self.cursor.fetchone()[0]
            print "找到组织"
        except Exception as e:
            logger.error(e)
            logger.error("查询组织失败")
            return
        if not or_table_id:
            return
        for url in url_list:
            print url
            try:
                speaker_sql = """select id from speakers WHERE url = '%s'""" % url
                self.cursor.execute(speaker_sql)
                speaker_table_id = self.cursor.fetchone()[0]
                print speaker_table_id
                print "找到发言人"
            except Exception as e:
                logger.error(e)
                print "查询发言人出错"
                continue
            if not speaker_table_id:
                continue
            # 保存关系
            sql = "insert into organizers_speakers (organizers_id, speakers_id) VALUES (%d, %d)" %(or_table_id, speaker_table_id)
            print sql
            try:
                self.cursor.execute(sql)
                self.mysql_cli.commit()
                print "保存关系"
            except Exception as e:
                self.mysql_cli.rollback()
                logger.error(e)
                logger.error("保存关系失败")
                print "保存关系失败"

    def save_data(self, organizer):
        sql = """insert into organizers (url, name, organizer_id, address, summary) VALUES ('%s', '%s', %s, '%s', '%s')""" %(
            organizer.url, organizer.name, organizer.organizer_id, organizer.address, organizer.summary
        )
        try:
            self.cursor.execute(sql)
            self.mysql_cli.commit()
            print "保存组织成功"
        except Exception as e:
            self.mysql_cli.rollback()
            logger.error(e)
            logger.error("保存组织失败")


    def __del__(self):
        self.cursor.close()
        self.mysql_cli.close()


if __name__ == "__main__":
    orgaspider = OrganizerSpider()
    orgaspider.run()