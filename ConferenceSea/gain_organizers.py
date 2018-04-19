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
        self.mysql_cli = pymysql.connect(host="localhost", port=3306, database="conference", user="root", password="mysql")
        self.cursor = self.mysql_cli.cursor()

    def run(self):
        if self.thread_name:
            print self.thread_name + "开始采集数据"
        self.start_spider()
        if self.thread_name:
            print self.thread_name + "结束采集"

    def start_spider(self):
        response = self.get_first_page()
        if not response:
            return
        # 获取第一页中的组织链接
        url_list = self.parse_data(response)
        for url in url_list:
            # 遍历,拿到每一个机构的url
            response = self.get_detail(url)
            if not response:
                continue
            data = self.parse_detail(response, url)
            # 保存数据
            self.save_data(data)
        # 获取其他页链接
        while True:
            response = self.get_other_page()
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
                data = self.parse_detail(response, url)

                self.save_data(data)

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
                response = requests.post(page_url, post_data, headers=headers)
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
                response = None
                logger.error(self.thread_name + "读取页%d失败" %self.page)
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
            summary += s
        organizer.summary = summary
        organizer.url = url
        organizer.organizer_id = organizer_id
        organizer.address = address
        organizer.name = name
        # 返回对象
        return organizer

    def save_data(self, data):
        pass



    def __del__(self):
        self.mysql_cli.close()
        self.cursor.close()

