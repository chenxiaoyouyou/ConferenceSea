# coding=utf-8
from selenium.webdriver import ActionChains
from selenium import webdriver
import time
import urllib
from config import logger, get_proxy
import redis
from multiprocessing import Pool
from Queue import Queue
import random


class Spider1:
    """
    爬虫类
    """
    def __init__(self, keywords, begin_data, enddata):

        url_start ="""https://www.emedevents.com/Conferences/searchConference?headerSearchType=conference&keywordSearch="""

        # USA&custom_startdate=01%2F01%2F2018
        # &custom_enddate=01%2F31%2F2018
        # &search-time=customdate
        url_end = """&pageId=1&browser_name_and_version=&pageId=1&browser_name_and_version="""
        begin = {'custom_startdate': begin_data}
        end = {'custom_enddate': enddata}
        begin = urllib.urlencode(begin)
        end = urllib.urlencode(end)
        # 拼接会议列表页的url字符串
        self.url = '%s%s&%s&%s&search-time=customdate%s' % (url_start, keywords, begin, end, url_end)
        # logger.
        print self.url
        # 设置不加载图片
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option('prefs', prefs)
        # 设置请求referer为该网站的首页
        # chrome_opt.add_argument('Referer=https://www.emedevents.com/')
        proxy = '--proxy-server=http://%s' % get_proxy()
        print proxy
        # 设置代理
        # chrome_opt.add_argument(proxy)
        # 构建浏览器对象
        self.driver = webdriver.Chrome(chrome_options=chrome_opt)
        # redis链接
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=7)
        # 添加请求头
        # 为每个线程创建redis链接, 多个线程操作一个redis链接会发生错误
        self.redis_cli = redis_cli
        logger.info(self.url)

    def start_spider(self):
        # 访问开始url
        # 三次尝试访问
        timeout = 3
        while timeout>0:
            try:
                timeout -= 1
                self.driver.get(self.url)
                # print self.driver.
                break
            except Exception as e:
                logger.error(e)
                logger.error('载入超时')

        # 寻找目标标签
        try:
            # 如果找到该div的话,寻找有没有view_more
            print '查找view_more'
            self.view_mo()
            print '查找列表'
            url_list = self.driver.find_elements_by_xpath('//div[@class="conf_summery"]/div[@class="c_name"]/a')
            try:
                # 将每个a标签的href写进redis
                for url in url_list:
                    self.redis_cli.sadd('2017_urls', url.get_attribute('href'))
            except Exception as e:
                logger.error(e)
                logger.error('redis错误')
        except Exception as e:
            logger.error(e)
            logger.error('没有找到信息')
        finally:
            self.end()


    def view_mo(self):
        # 持续点击view_more直到没有更多记录
        try:
            view_more = self.driver.find_element_by_id('view_more')
            print '找到view_more'
            # ActionChains(driver=self.driver).move_to_element(view_more).click().perform()
            # 暂停1-3秒
            view_more.click()
            time.sleep(random.randint(1,3))
            self.view_mo()
        except:
            print '没有更多的view_more'
            return

    def end(self):
        logger.info('Done'+ self.url)
        self.driver.quit()
        print '结束运行'


def create_pro(line):
    site, start_time, end_time = line.split()
    spider = Spider1(site, start_time, end_time)
    spider.start_spider()


def main():
    """
    将文件中的关键字读入队列
    :return:
    """
    page_queue = Queue()
    file = open('./key/123.txt')
    while True:
        line = file.readline()
        if not line:
            break
        # 将关键字信息加入队列
        page_queue.put(line)

    po = Pool(2)
    try:
        for i in range(2):
            # 从队列中取出一个
            line = page_queue.get()
            # 创建子进程
            po.apply_async(create_pro, (line,))
            logger.info('进程 %s' % i)
    except Exception as e:
        logger.error(e)
    # 关闭进程池
    po.close()
    # 等待结束
    po.join()
    print '结束'


if __name__ == '__main__':
    main()

