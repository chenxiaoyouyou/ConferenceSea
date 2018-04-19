# coding=utf-8
import redis
import requests
from lxml import etree
import pymysql
import threading
from config import logger
import re
from User_Agent import User_Agent
import random

class Meeting:
    # 保留organizer 和 organizer_id两个字段,一个方便链表查询,一个方便直接读取,且可能读取不到组织信息
    title = ""
    url = ""
    start_date = ""
    end_date = ""
    area = ""
    specialties = ""
    organizer_id = 0
    organizer_url = ""
    organizer = ""


class GainDetailInfoThread(threading.Thread):
    """
    获取每个会议的详细信息
    """
    def __init__(self, thread_name=None):
        threading.Thread.__init__(self)
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept - Encoding': 'gzip',
                        'Cache-Control': 'no-cache',
                        'User-Agent': random.choice(User_Agent),
                        'Connection': 'keep-alive',
                        }
        # 创建一个redis链接
        self.redis_cli = redis.StrictRedis(host='localhost', port=6379, db=7)
        # 创建一个mysql链接
        self.mysql_cli = pymysql.connect(host='192.168.204.140', port=3306, database='conference', user='root', password='mysql', charset='utf8')
        self.cursor = self.mysql_cli.cursor()
        self.thread_name = thread_name


    def run(self):
        print self.thread_name + '开始爬取'
        self.gain_info()
        print '结束爬取'

    def gain_info(self):
        """
        获取信息
        :return:
        """
        # 无限循环从redis中获取数据
        # i = 1
        # while True:
        #     print i
        #     i += 1
        #
        #     try:
        #
        #         # url = self.redis_cli.spop('2017_urls')
        #     except Exception as e:
        #         logger.error(e)
        #         logger.error('从redis中取数据出错')
        #     if not url:
        #         break
            # 多次尝试打开一个网页,打开就直接跳出,打开失败尝试再次打开
        url = "https://www.emedevents.com/c/medical-conferences-2018/principles-of-medical-education-maximizing-your-teaching-skills-3"
        # 实验刚开始
        i = 1
        while True:
            i += 1
            if i > 2:
                break

            times = 4
            html_selector = None
            while times > 0:
                times -= 1
                try:
                    """
                    proxies = { "http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080", }
                    requests.get("http://example.org", proxies=proxies)
                    """

                    content = requests.get(url, headers=self.headers)
                    # 获取数据
                    html_selector = etree.HTML(content.text)
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error('打开网页失败')
            if len(content.text) == 0:
                return

            # 存在网页数据, 从中取出需要的数据
            # 链接地址
            current_url = url
            # 会议标题
            title = html_selector.xpath('//h1/text()')[0]
            # 获取会议的开始日期和结束日期
            date_str = html_selector.xpath('//div[@class="date"]/text()')[0]
            # 获取日期字符串
            date_str = date_str.replace(',', ' ').replace('|', ' ').replace('\t', '').strip()
            date_str = re.match(r'([^ ]+) ([\d]{1,2}) - ([a-zA-Z]{3})?.*?([\d]{1,2}).*?([\d]{4})', date_str)
            month1 = date_str.group(1)
            start_day = date_str.group(2)
            month2 = date_str.group(3)
            end_day = date_str.group(4)
            year = date_str.group(5)
            # 月份字典,用于将英文月份转化为数字字符串
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
            if not month2:
                start_date = year + '-' + Month.get(month1) + '-' + start_day
                end_date = year + '-' + Month.get(month1) + '-' + end_day
            else:
                start_date = year + '-' + Month.get(month1) + '-' + start_day
                end_date = year + '-' + Month.get(month2) + '-' + end_day

            print start_date
            print end_date
            # 获取会议举行的地区,(列表)
            area = html_selector.xpath('//div[@class="date"]/a/text()')
            # 地区
            area = area[0] + ',' + area[1]
            print area
            # 组织机构
            organizer = html_selector.xpath('//div[@class="speakers marT10"]/span/a/text()')[0]
            organizer_url = html_selector.xpath('//div[@class="speakers marT10"]/span/a/@href')[0]
            print organizer_url
            # 学科, 可能有多个学科
            specialties_list = html_selector.xpath('//div[@class="speakers"]/span/a/text()')
            specialities = ''
            # 可采用模糊查询得到结果
            for spe in specialties_list:
                specialities += (spe + ',')
            # 最终学科字符串
            specialities = specialities.strip(',')
            print specialities
            # 获取发言人信息
            # speakers_list = html_selector.xpath('//h5/a/text()')
            meeting = Meeting()
            meeting.url = current_url
            meeting.title = title
            meeting.start_date = start_date
            meeting.end_date = end_date
            meeting.area = area
            meeting.specialties = specialities
            meeting.organizer = organizer
            # 根据组织单位的url查找该组织在表中的id
            meeting.organizer_url = organizer_url
            # 保存会议信息,返回会议在会议表中id
            meeting_id = self.save_meeting(meeting)
            # 没有查询到id的话,直接结束
            if not meeting_id:
                return
            # 查找发言人信息
            print meeting_id
            # 查找viewall, 有的话直接发起viewall链接,没有的话查询本页发言人,没有的话直接
            viewall = html_selector.xpath('//a[@data-type="speaker"]')
            print viewall
            # 有viewall的话,直接访问viewall
            if viewall:
                print "viewall"
                orgSpeakersData = re.findall(r"""conf_speak_data = "(.*?)";""", content.text)[0]
                conftypeid = html_selector.xpath('//input[@name="conftypeid"]/@value')[0]
                conftype = "Speaking at " + title
                speakers_url_list = self.gain_viewall(orgSpeakersData, conftype, conftypeid)
            else:
                # 没有viewall, 直接查询人物信息
                speakers_url_list = html_selector.xpath('//div[@id="speaker_confView"]/div/div/div/a/@href')
            if not speakers_url_list:
                return
            for speaker_url in speakers_url_list:
                self.save_relationship(speaker_url, meeting_id)


    def gain_viewall(self, orgSpeakersData, conftype, conftypeid):
        "请求发言人信息的viewall"
        url = "https://www.emedevents.com/view-all"
        # post请求数据
        post_data = {
            "orgSpeakersData": orgSpeakersData,
            "conftype": conftype,
            "conftypeid": conftypeid,
            "spr_type": "detail_sat"
        }
        i = 1
        while i <=4:
            i += 1
            try:
                response = requests.post(url, data=post_data, headers=self.headers)
                selector = etree.HTML(response.text)
                break
            except Exception as e:
                logger.error(e)
                logger.error("查询viewall失败")
                selector = None
        # 请求失败的话,直接返回
        if selector is not None:
            return
        speakers_url_list = selector.xpath('//h3/../@href')
        print speakers_url_list
        return speakers_url_list

    def save_meeting(self, meeting):
        """
        保存会议信息, 接受会议对象为参数
        :param meeting:
        :return: 该会议在数据库中的id
        """
        try:
            sql = """select id from organizers where url = '%s'""" % meeting.organizer_url
            self.cursor.execute(sql)
            organizer_id = self.cursor.fetchone()
            if not organizer_id:
                organizer_id = 'null'
                insert_sql = """insert into conferences(title, url, start_date, end_date, area, specialties, organizer, organizer_id) VALUES
                                          ("%s", "%s", "%s", "%s", "%s", "%s", "%s", %s)""" % (
                    meeting.title, meeting.url, meeting.start_date, meeting.end_date, meeting.area, meeting.specialties,meeting.organizer,
                    organizer_id)
            else:
                organizer_id = organizer_id[0]
                insert_sql = """insert into conferences(title, url, start_date, end_date, area, specialties, organizer, organizer_id) VALUES
                          ("%s", "%s", "%s", "%s", "%s", "%s", %d)""" % (
                meeting.title, meeting.url, meeting.start_date, meeting.end_date, meeting.area, meeting.specialties, meeting.organizer,
                organizer_id)
            self.cursor.execute(insert_sql)

            self.mysql_cli.commit()
        except Exception as e:
            self.mysql_cli.rollback()
            logger.error(e)
            logger.error("保存会议失败")
        try:
            sql = """select id from conferences where url = '%s'""" % meeting.url
            self.cursor.execute(sql)
            conference_table_id = self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(e)
            logger.error("查询会议失败")
            return

        return conference_table_id


    def save_relationship(self, speaker_url, meetingid):
        """保存人物和会议的多对多关系"""
        # 查询人物的id
        sql = """select id from speakers where url = '%s'""" % speaker_url
        try:
            self.cursor.execute(sql)
            speaker_table_id = self.cursor.fetchone()
            if not speaker_table_id:
                return
            speaker_table_id = speaker_table_id[0]
            # 插入关系字段
            sql1 = """insert into conferences_speakers (conference_id, speakers_id) VALUES (%d, %d)""" %(meetingid, speaker_table_id)
            self.cursor.execute(sql1)
            self.mysql_cli.commit()
        except Exception as e:
            self.mysql_cli.rollback()
            print "查询人物, 写入人-会关系失败"
            logger.error(e)
            logger.error("查询人物, 写入人-会关系失败")


    def __del__(self):
        self.cursor.close()
        self.mysql_cli.close()



def main():
    name_list = ["thread_1", "thread_2", "thread_3"]
    thread_list = []
    for i in range(3):
        meetingspider = GainDetailInfoThread(name_list[i])
        thread_list.append(meetingspider)

    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()

    for thread in thread_list:
        thread.join()



if __name__ == '__main__':
    main()