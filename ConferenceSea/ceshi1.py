#coding=utf-8
from selenium import webdriver
import time
import urllib
from lxml import etree
from config import logger
import redis
from multiprocessing import Pool
from Queue import Queue
from selenium.webdriver import ActionChains
import selenium


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

        # 设置不加载图片
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option('prefs', prefs)
        # 构建浏览器对象
        self.driver = webdriver.Chrome(chrome_options=chrome_opt)
        # redis链接
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=7)
        # 为每个线程创建redis链接, 多个线程操作一个redis链接会发生错误
        self.redis_cli = redis_cli
        logger.error(self.url)

    def start_spider(self):
        # 访问开始url
        self.driver.get(self.url)
        # 寻找目标标签
        try:
            # 确认列表页是否有内容
            print '查找列表'
            url_list = self.driver.find_element_by_xpath("//div[@class='conf_summery']/div[@class='c_name']/a/@href")
            # 如果找到该div的话,寻找有没有view_more
            self.url_list = url_list
            print '查找view_more'
            self.view_mo()
            print '获取url'
            # 获取网页内容
            # html = self.driver.page_source
            print '获取html'
            print self.driver.page_source
            # selector = etree.HTML(html)
            # print '获取选择器'
            url_list = self.driver.find_elements_by_xpath("//div[@class='filter_search']/div[2]/div[@class='sec_conf_main']/div[2]/div[1]/a/@href")
            print len(url_list)
            try:
                for url in url_list:
                    # 放入redis集合中
                    # self.redis_cli.sadd('2017_urls', url)
                    print url
            except Exception as e:
                logger.error(e)

        except:
            logger.error('没有找到信息')
        finally:
            self.end()


    def view_mo(self):
        # 持续点击view_more直到没有更多记录
        try:
            print '寻找view_more'
            view_more = self.driver.find_element_by_id('view_more')
            print 'zhaodao view more'
            ActionChains(driver=self.driver).move_to_element(view_more).click(view_more).perform()
            view_more.click()

            print '点击 view_more'
            # 暂停3秒
            # time.sleep(3)
            self.view_mo()
        except:
            print '没有更多的view_more'
            return

    def end(self):
        self.driver.quit()
        print '结束运行'



def view_mo(driver):
    # 持续点击view_more直到没有更多记录
    try:
        print '寻找view_more'
        view_more = driver.find_element_by_id('view_more')
        print 'zhaodao view more'
        ActionChains(driver=driver).move_to_element(view_more).click(view_more).perform()
        # view_more.click()
        print '点击 view_more'
        url_list = driver.find_elements_by_xpath('//div[@class="conf_summery"]/div[@class="c_name"]/a')
        for url in url_list:
            print url.get_attribute('href')
        # 暂停3秒
        # time.sleep(3)
        view_mo(driver)
    except:
        print '没有更多的view_more'
        return



def create_pro(line):
    site, start_time, end_time = line.split()
    url_start = """https://www.emedevents.com/Conferences/searchConference?headerSearchType=conference&keywordSearch="""
    url_end = """&pageId=1&browser_name_and_version=&pageId=1&browser_name_and_version="""
    begin = {'custom_startdate': start_time}
    end = {'custom_enddate': end_time}
    begin = urllib.urlencode(begin)
    end = urllib.urlencode(end)
    # 拼接会议列表页的url字符串
    url = '%s%s&%s&%s&search-time=customdate%s' % (url_start, site, begin, end, url_end)
    print url

    chrome_opt = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_opt.add_experimental_option('prefs', prefs)
    # 构建浏览器对象
    driver = webdriver.Chrome(chrome_options=chrome_opt)
    driver.get(url)
    # redis链接
    # 进行4次链接,均链超时的话放弃
    # times = 4
    # while times > 0:
    #     try:
    #         driver.get(url)
    #         times -= 1
    #         break
    #     except selenium.common.exceptions.TimeoutException:
    #         print '请求超时'
    #         driver.quit()
    try:
        # 确认列表页是否有内容
        print '查找列表'
        url_list = driver.find_elements_by_xpath('//div[@class="conf_summery"]/div[@class="c_name"]/a')
        for url in url_list:
            print url.get_attribute('href')
        # 如果找到该div的话,寻找有没有view_more
        print '查找view_more'
        view_mo(driver)
        # print '获取url'
        # 获取网页内容
        # html = self.driver.page_source
        # print '获取html'
        # try:
        #     # print driver.page_source
        # # selector = etree.HTML(html)
        # # print '获取选择器'
        #     url_list = driver.find_elements_by_xpath(
        #     "//div[@class='sec_conf_main']/div[2]/div[1]/a/@href")
        # except Exception as e:
        #     url_list = None
        #     print e
        # print len(url_list)
        # try:
        #     for url in url_list:
        #         # 放入redis集合中
        #         # self.redis_cli.sadd('2017_urls', url)
        #         print url
        # except Exception as e:
        #     logger.error(e)

    except Exception as e:
        # logger.error('没有找到信息')
        print e
    finally:
        driver.quit()


create_pro('china 01/01/2018 05/01/2018')

