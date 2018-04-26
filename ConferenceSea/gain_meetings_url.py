# coding=utf-8
import requests
from lxml import etree
import threading
import redis
from config import logger
import time
import random
import Queue
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from User_Agent import User_Agent

class UrlSpider(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        # 获取队列
        self.q = q
        # 代理
        self.proxies = {
            'http': 'http://114.215.174.49:16818',
            # 'https': 'http://chenzhiyou0320@163.com:lwslf70d@114.215.174.49:16818'
        }

        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept - Encoding': 'gzip',
                        'Cache-Control': 'no-cache',
                        'User-Agent': random.choice(User_Agent),
                        'Connection': 'keep-alive',
                        'Referer':'https://www.emedevents.com/'
                        }
        # redis链接
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=7)
        # 添加请求头
        # 为每个线程创建redis链接, 多个线程操作一个redis链接会发生错误
        self.redis_cli = redis_cli
        self.page = 1


    def run(self):
        print '开始爬'
        self.start_spider()
        print '结束啦'


    def start_spider(self):
        """查询第一页中的信息"""
        while True:
            # 每次请求之间的时间间隔
            time.sleep(random.randint(1, 2))
            year = str(self.q.get())
            self.year = year
            print self.year
            if not year:
                break
            # 得到检索的关键信息
            # 01 / 01 / 2016
            # 05 / 31 / 2016
            begin = "01/01/" + year
            end = "12/31/" + year
            self.begin = begin
            self.end = end
            # 拼接会议列表页的url字符串
            self.url = "https://www.emedevents.com/conferences/searchFilter"
            print self.begin
            self.gain_others()


    def gain_others(self):

        while True:
            time.sleep(random.randint(1,2))
            # print "sleep"
            self.data = {
                "month": "All",
                "sterm": "",
                "cme_from": 0,
                "cme_to": 500,
                "country": "All",
                "city": "All",
                "ctype": "All",
                "specialty": "All",
                "page": self.page,
                "year": self.year,
                "custom_date_flag": "",
                "custom_date_from": self.begin,
                "custom_date_to": self.end,
                "org_confs": "",
                "search_organizer": "",
                "org_conference_type": "",
                "org_sort_conferences": ""
            }
            print str(self.year) + "*****" +str(self.page)
            self.headers['Referer'] = "https://www.emedevents.com/Conferences/searchConference?headerSearchType=conference"
            self.headers['X-Requested-With'] = 'XMLHttpRequest'
            # Host:www.emedevents.com
            # Origin:https: // www.emedevents.com
            self.headers['HOST'] = 'www.emedevents.com'
            self.headers['Origin'] = 'https: // www.emedevents.com'
            # 发起post请求
            a = 1
            while a<3:
                a += 1
                try:
                    response = requests.post(self.url, headers=self.headers, data=self.data, verify=False)
                    "请求成功"
                    break
                except Exception as e:
                    logger.error(e)
                    response = None
            # 此次请求失败直接进行下一次
            if not response:
                continue
            selector = etree.HTML(response.text)
            url_list = selector.xpath('//div[@class="conf_summery"]/div[@class="c_name"]/a/@href')
            if url_list:
                try:
                    # 加载完成时把第一页的写入
                    for url in url_list:
                        if url.startswith('https://www.emedevents.com'):
                            print url
                            self.redis_cli.sadd('2017_urls', url)

                except Exception as e:
                    logger.error(e)
                    logger.error('redis错误')
            self.page += 1
            # 当页数过大,不再有数据,跳出循环
            if not url_list:
                er =  "break" + "********" + str(self.year)
                logger.error(er)
                break


def main():
    # 程序有点小问题,不能自动切换年份
    year_queue = Queue.Queue()
    for i in range(2017, 2021):
        print i
        year_queue.put(i)
    # 4个线程
    for i in range(4):
        spider = UrlSpider(year_queue)
        spider.start()


if __name__ == '__main__':
    main()
