# coding=utf-8
import requests
import threading
from lxml import etree
from config import logger
import pymysql
import time
import random
import re
from Queue import Queue

class Speaker:
    url = ''
    name = ''
    position = ''
    interested = ''
    specialities = ''
    address = ''


class SpeakerSpider(threading.Thread):

    def __init__(self, page_queue, thread_name):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        # 代理
        self.proxies = {
            'http': 'http://122.114.214.159:16817',
            # 'https': 'http://chenzhiyou0320@163.com:lwslf70d@114.215.174.49:16818'
        }
        self.page_queue = page_queue
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Cache-Control": "no-cache",
            # "Connection": "keep-alive",
        }
        # 开始url
        self.start_url = "https://www.emedevents.com/Speakers/viewAllSpeakers?data[headerSearchForm][search_type]=speaker"
        # 开始页
        self.start_page = page_queue.get()
        print self.start_page
        self.page = self.start_page
        self.mysql_cli = pymysql.connect(host='localhost', port=3306, database='conference', user='root', password='mysql', charset='utf8')
        self.cursor = self.mysql_cli.cursor()

        # print self.url

    def run(self):
        print "开始采集"
        # self.url = 'https://www.emedevents.com/Speakers/viewAllSpeakers?data[headerSearchForm][search_type]=speaker&data[SearchSpeaker][speaker_name]=%s' % self.key_word
        # 开始爬取
        self.start_spider()
        print "结束采集"

    def start_spider(self):

        # 为了代码一致,所以都从第一页开始爬取
        # 获取第一页数据
        # first_page_data = self.get_first_list_page()
        # if first_page_data is None:
        #     return
        # print 'get_first_page'
        # url_list = self.parse_data(first_page_data)
        # if url_list is None:
        #     return
        # # print url_list
        # for url in url_list:
        #     # 查找人物信息
        #     speaker = self.get_speaker(url)
        #     # 写入数据库
        #     self.save(speaker)

        # 死循环获取其他页的信息，直到返回空列表
        while True:

            print 'get_other_page'
            other_page_data = self.get_other_list_page()
            print 'get_data'
            # 某一页请求失败的话，直接进行下一次循环
            if other_page_data is None:
                continue
            url_list = self.parse_data(other_page_data)

            print url_list
            logger.error(self.thread_name + "********" + str(self.page))
            print self.page
            # 针对三个线程,设定不同的跳出条件
            if self.start_page == 200:
                # 从第一页开始,到4000页结束
                # self.page = 4000
                if self.page >= 4000:
                    break
            elif self.start_page == 4200:
                # 从第4000页开始,到7000页结束
                if self.page >= 7000:
                    break
            else:
                # 从7000页开始
                # 不再有人物信息，跳出循环
                if not url_list:
                    break
            # 页码加1
            self.page += 1
            logger.error(self.page)
            for url in url_list:
                # 查找人物信息
                speaker = self.get_speaker(url)
                # 写入数据库
                if speaker:
                    self.save(speaker)
                time.sleep(1)


    def get_first_list_page(self):
        headers = self.headers
        headers["Referer"] = "https://www.emedevents.com/"
        # 获取列表页(第一页)
        times = 1
        while times < 4:
            # 一次请求失败的话,多次发起请求
            times += 1
            try:
                response = requests.get(self.start_url, headers=self.headers, timeout=30)
                # 请求成功, 跳出循环
                break
            except Exception as e:
                logger.error(e)
                response = None
        if not response:
            return None

        return response.content


    def get_other_list_page(self):
        # 获取其他页面的信息,第二页,第三页
        headers = self.headers
        headers["Referer"] = self.start_url
        cur_url = "https://www.emedevents.com/Speakers/viewAllSpeakers/search_speaker/%d" % self.page

        post_data = {
            "resultData": "",
            "page": self.page,
            "filter_type": "search_speaker",
            "speaker_name": "",
            "speaker_speciality": "",
            "speaker_location": "",
        }
        try:
            response = requests.post(cur_url, data=post_data, timeout = 30)
        except Exception as e:
            logger.error(e)
            return None
        return response.content


    def parse_data(self, data):
        # 获取每一个发言人的链接
        selector = etree.HTML(data)
        speaker_url_list = selector.xpath('//div[@align="center"]/div/div/a/@href')

        return speaker_url_list

    def get_speaker(self, speaker_url):

        headers = self.headers
        headers['Referer'] = self.start_url
        times = 1
        while times < 4:
            times += 1
            try:
                # proxies = {"http": "http://" + get_proxy()}
                # speaker_data = requests.get(url, headers=self.headers, proxies=proxies)
                speaker_data = requests.get(speaker_url, headers=headers)
                break
            except Exception as e:
                logger.error(e)
                logger.error('查找发言人信息失败')
                speaker_data = None

        # 一直没有数据的话,返回
        if not speaker_data:
            return None
        # 获取信息
        try:
        # 得到发言人页的信息
            speaker_data = etree.HTML(speaker_data.content)
            # 获取发言人姓名
            name = speaker_data.xpath('//h1/text()')[0]
            name = name.strip()
            # 职位信息
            position_area = speaker_data.xpath('//h1/../text()')[1].strip()
            # 有的没有职位信息
            # 或者只有地址,没有职位
            if not position_area:
                position = ''
                address = ''
            else:
                # 匹配竖线, 有的话为有职位,没有的话只有地址
                line = re.match(r'(.*?)\|(.*)', position_area)
                if line:
                    address = line.group(2)
                    position = line.group(1)
                else:
                    position = ''
                    address = position_area
            # 发言主题
            speaker_specialities = speaker_data.xpath('//h2[@id="moreSpecilty"]/following-sibling::div[1]/text()')[
                0].strip()
            # 兴趣主题
            speaker_interested = speaker_data.xpath('//h2[@id="moreTopics"]/following-sibling::div[1]/text()')[
                0].strip()
            # 如果作者没有填写相关信息,则设置为none
            if speaker_specialities == 'This section has yet to be updated by the speaker':
                speaker_specialities = ''
            if speaker_interested == 'This section has yet to be updated by the speaker':
                speaker_interested = ''
        except Exception as e:
            logger.error(e)
            logger.error("发言人信息读取失败")
            return None
        # 构建speaker对象,方便存储
        speaker = Speaker()
        speaker.name = name
        speaker.position = position
        speaker.url = speaker_url
        speaker.interested = speaker_interested
        speaker.specialities = speaker_specialities
        speaker.address = address
        # print speaker.url
        return speaker


    def save(self, speaker):
        # 将数据保存至mysql数据库
        try:
            sql = """insert into speakers(url, name, address, position, specialties, interested) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')""" % (speaker.url, speaker.name,
                                                                                   speaker.address, speaker.position, speaker.specialities, speaker.interested)
            self.cursor.execute(sql)
            # 提交
            self.mysql_cli.commit()
        except Exception as e:
            self.mysql_cli.rollback()
            # 错误的话回滚
            logger.error(e)
            logger.error('保存人物信息失败')
    def __del__(self):
        # 关闭数据库链接
        self.cursor.close()
        self.mysql_cli.close()

def main():
    # 队列放入数据
    page_queue = Queue()
    # file = open('./key/speaker_words')
    # 三个线程,分别从这三个页码开始爬取
    for i in [200, 4200, 7300]:
        page_queue.put(i)

    thread_list = []
    thread_name_list = ["thread_1", "thread_2", "thread_3"]

    # 三个线程运行
    for i in range(3):
        spider = SpeakerSpider(page_queue, thread_name_list[i])
        thread_list.append(spider)
        print spider

    # 设置为守护线程
    for thread in thread_list:
        # thread.setDaemon(True)
        thread.start()

    # 等待线程结束
    for thread in thread_list:
        thread.join()
    print '程序结束'


if __name__ == "__main__":
    main()


