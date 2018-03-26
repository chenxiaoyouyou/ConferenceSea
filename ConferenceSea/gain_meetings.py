# coding=utf-8
import redis
import requests
from lxml import etree
import pymysql
import threading
from config import logger
import re

class GainDetailInfoThread(threading.Thread):
    """
    获取每个会议的详细信息
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.headers = {'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Cache-Control': 'max-age=0',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                        'Connection': 'keep-alive',
                        }
    def run(self):
        print '开始爬取'
        self.gain_info()
        print '结束爬取'

    def gain_info(self):
        """
        获取信息
        :return:
        """
        # 无限循环从redis中获取数据
        while True:
            redis_cli = redis.StrictRedis(host='localhost', port=6379, db=7)
            url = redis_cli.spop('2017_urls')
            if not url:
                break
            # 多次尝试打开一个网页,打开就直接跳出,打开失败尝试再次打开
            times = 4
            html_selector = None
            while times > 0:
                times -= 1
                try:
                    # 请求url
                    content = requests.get(url, headers=self.headers)
                    # 获取数据
                    html_selector = etree.HTML(content.text)
                    break
                except Exception as e:
                    logger.error(e)

            if html_selector:
                # 存在网页数据, 从中取出需要的数据
                # 链接地址
                current_url = url
                # 会议标题
                title = html_selector.xpath('//h1/text()')[0]
                # 获取会议的开始日期和结束日期
                date_str = html_selector.xpath('//div[@class="date"]/text()')[0]
                # 获取日期字符串
                date_str = date_str.replace(',', ' ').replace('|', ' ').replace('\t', '').strip()
                date_str = re.match(r'([^ ]+).*?([\d]{1,2}).*?([\d]{1,2}).*?([\d]{4})', date_str)
                month = date_str.group(1)
                start_day = date_str.group(2)
                end_day = date_str.group(3)
                year = date_str.group(4)
                # 月份字典,用于将英文月份转化为数字
                Month = {
                    'Jan': '01',
                    'Feb': '02',
                    'Mar': '03',
                    'Apr': '04',
                    'May': '05',
                    'Jun': '06',
                    'Jul': '07',
                    'Aug': '08',
                    'Sep': '09',
                    'Oct': '10',
                    'Nov': '11',
                    'Dec': '12'
                }
                # 开始日期和结束日期,格式为'1990-03-20'
                start_date = year + '-' + Month.get(month) + '-' + start_day
                end_date = year + '-' + Month.get(month) + '-' + end_day
                # 获取会议举行的地区,(列表)
                area = html_selector.xpath('//div[@class="date"]/a/text()')
                # 地区
                area = area[0] + ',' + area[1]
                # 组织机构
                organizer = html_selector.xpath('//div[@class="speakers marT10"]/span/a/text()')[0]
                # 学科, 可能有多个学科
                specialties_list = html_selector.xpath('//div[@class="speakers"]/span/a/text()')
                specialities = ''
                for spe in specialties_list:
                    specialities += (spe + ',')
                # 最终学科字符串
                specialities = specialities.strip(',')
                # 获取发言人信息
                speakers_list = html_selector.xpath('//h5/a/text()')
                speakers_url_list = html_selector.xpath('//div[@id="speaker_confView"]/div/div/div/a/@href')
                for url in speakers_url_list:
                    # 依次打开发言人url, 并从中获取信息
                    try:
                        speaker_data = requests.get(url, headers=self.headers)
                        # 得到作者页的信息
                        speaker_data = etree.HTML(speaker_data)
                        name = speaker_data.xpath()






