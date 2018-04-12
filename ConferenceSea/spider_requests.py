# coding=utf-8
import requests
from lxml import etree
import threading
import urllib
import redis
from config import logger
import time
import random
import Queue
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class UrlSpider(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        # 获取队列
        self.q = q
        # 代理
        # proxies = {
        #     'http': 'http://username:password@117.201.23.54:9000'
        # }
        self.proxies = {
            'http': 'http://114.215.174.49:16818',
            # 'https': 'http://chenzhiyou0320@163.com:lwslf70d@114.215.174.49:16818'
        }

        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept - Encoding': 'gzip',
                        'Cache-Control': 'no-cache',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                        'Connection': 'keep-alive',
                        'Referer':'https://www.emedevents.com/'
                        }
        # redis链接
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=7)
        # 添加请求头
        # 为每个线程创建redis链接, 多个线程操作一个redis链接会发生错误
        self.redis_cli = redis_cli


    def run(self):
        print '开始爬'
        self.start_spider()
        print '结束啦'


    def start_spider(self):
        """查询第一页中的信息"""
        while True:
            # 每次请求之间的时间间隔
            time.sleep(random.randint(3, 5))
            line = self.q.get()
            if not line:
                break
            # 得到检索的关键信息
            keywords, begin_date, end_date = line.split()
            print keywords + begin_date + end_date
            # 拼接请求的url
            url_start = """https://www.emedevents.com/Conferences/searchConference?headerSearchType=conference&keywordSearch="""
            # USA&custom_startdate=01%2F01%2F2018
            # &custom_enddate=01%2F31%2F2018
            # &search-time=customdate
            url_end = """&pageId=1&browser_name_and_version=&pageId=1&browser_name_and_version="""
            begin = {'custom_startdate': begin_date}
            self.keywords = keywords
            self.begin_date = begin_date
            self.end_date = end_date
            end = {'custom_enddate': end_date}
            begin = urllib.urlencode(begin)
            end = urllib.urlencode(end)
            # 拼接会议列表页的url字符串
            self.url = '%s%s&%s&%s&search-time=customdate%s' % (url_start, keywords, begin, end, url_end)
            # 记录一下爬取进度
            print self.url
            logger.error(self.url)
            self.gain_first_page()


    def gain_first_page(self):
        # 发起请求
        i = 1
        while 1<4:
            i += 1
            try:
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                response = requests.get(self.url, headers=self.headers, proxies=self.proxies,verify=False)
                break
            except Exception as e:
                logger.error(e)
                logger.error('请求失败')
                response = None

        if not response:
            return

        selector = etree.HTML(response.text)
        # 选择除url_list(会议的url)
        url_list = selector.xpath('//div[@class="conf_summery"]/div[@class="c_name"]/a/@href')
        org_start_date = selector.xpath('//input[@id="org_start_date"]/@value')[0]
        # print org_start_date
        org_end_date = selector.xpath('//input[@id="org_end_date"]/@value')[0]
        # print org_end_date

        # 将url写进数据库
        if url_list:
            try:
                # 加载完成时把第一页的写入
                for url in url_list:
                    self.redis_cli.sadd('2017_urls', url)
                    print url
            except Exception as e:
                logger.error(e)
                logger.error('redis错误')

            # 查找有没有view_more
            view_more = selector.xpath('//a[@id="view_more"]')
            if view_more:
                self.gain_others(org_start_date, org_end_date)
                print 'gain_others'

    def gain_others(self, org_start_date,org_end_date):

        """获得点击view_more之后的信息"""
        url1 = 'https://www.emedevents.com/conferences/searchFilter'
        i = 1
        while True:
            time.sleep(random.randint(3,4))
            year = self.begin_date[-4:]
            print year
            form_data = {
                'month': 'All',
                'sterm': self.keywords,
                'cme_from': 0,
                'cme_to': 500,
                'country': 'All',
                'city': 'All',
                'ctype': 'All',
                'specialty': 'All',
                'page': i,
                'year': str(year),
                'custom_date_flag': 1,
                'custom_date_from': self.begin_date,
                'custom_date_to': self.end_date,
                'org_confs': '',
                'search_organizer': '',
                'org_conference_type': '',
                'org_start_date': org_start_date,
                'org_end_date': org_end_date,
                'org_sort_conferences': ''
            }
            self.headers['Referer'] = self.url
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
                    response = requests.post(url1, headers=self.headers, data=form_data, proxies = self.proxies, verify=False)
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error('点击view_more失败')
                    response = None
            if not response:
                return
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
            i += 1
            # 当页数过大,不再有数据,跳出循环
            if not url_list:
                break


def main():
    page_queue = Queue.Queue()
    file = open('./key/meeting_words')
    while True:
        line = file.readline()
        if not line:
            break
        # 将关键字信息加入队列
        page_queue.put(line)
    # 三个线程
    for i in range(4):
        spider = UrlSpider(page_queue)
        spider.start()


if __name__ == '__main__':
    main()
