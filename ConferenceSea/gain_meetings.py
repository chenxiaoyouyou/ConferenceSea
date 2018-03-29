# coding=utf-8
import redis
import requests
from lxml import etree
import pymysql
import threading
from config import logger, get_proxy
import re

class GainDetailInfoThread(threading.Thread):
    """
    获取每个会议的详细信息
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept - Encoding': 'gzip',
                        'Cache-Control': 'no-cache',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                        'Connection': 'keep-alive',
                        }
        # 创建一个redis链接
        self.redis_cli = redis.StrictRedis(host='localhost', port=6379, db=7)
        # 创建一个mysql链接
        self.mysql_cli = pymysql.connect(host='localhost', port=3306, database='conference', user='root', password='mysql', charset='utf8')

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
        i = 1
        while True:
            print i
            i += 1

            try:

                url = self.redis_cli.spop('2017_urls')
            except Exception as e:
                logger.error(e)
                logger.error('从redis中取数据出错')
            if not url:
                break
            # 多次尝试打开一个网页,打开就直接跳出,打开失败尝试再次打开
            times = 4
            html_selector = None
            while times > 0:
                times -= 1
                try:
                    """
                    proxies = { "http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080", }
                    requests.get("http://example.org", proxies=proxies)
                    """

                    # proxies = {"http":"http://" + get_proxy()}
                    # 请求url
                    # content = requests.get(url, headers=self.headers, proxies=proxies)
                    content = requests.get(url, headers=self.headers)
                    # 获取数据
                    html_selector = etree.HTML(content.text)
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error('打开网页失败')

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
                # 获取会议举行的地区,(列表)
                area = html_selector.xpath('//div[@class="date"]/a/text()')
                # 地区
                area = area[0] + ',' + area[1]
                # 组织机构
                organizer = html_selector.xpath('//div[@class="speakers marT10"]/span/a/text()')[0]
                organizer_url = html_selector.xpath('//div[@class="speakers marT10"]/span/a/@href')[0]
                # 学科, 可能有多个学科
                specialties_list = html_selector.xpath('//div[@class="speakers"]/span/a/text()')
                specialities = ''
                # 可采用模糊查询得到结果
                for spe in specialties_list:
                    specialities += (spe + ',')
                # 最终学科字符串
                specialities = specialities.strip(',')
                # 获取发言人信息
                # speakers_list = html_selector.xpath('//h5/a/text()')
                speakers_url_list = html_selector.xpath('//div[@id="speaker_confView"]/div/div/div/a/@href')

                # 打开组织单位链接
                try:
                    self.headers['referer']=current_url
                    organizer_info = requests.get(organizer_url, hearder=self.headers)
                    organizer_info = etree.HTML(organizer_info.text)
                    address = organizer_info.xpath('//div[@class="location"]/text()')
                    address = address[0].strip() + address[1].strip()
                except Exception as e:
                    logger.error(e)
                    print e



                # 将会议的信息加入mysql数据库
                try:
                    meeting_info = [title, current_url, start_date, end_date, area, organizer, specialities]
                    # 游标
                    cursor = self.mysql_cli.cursor()
                    # 准备加一个锁
                    cursor.execute('insert into conferences(title, url, start_date, end_date, area, organized, specialties) VALUES (%s, %s, %s, %s, %s, %s, %s)', meeting_info)
                    self.mysql_cli.commit()
                    paras2 = [current_url,]
                    cursor.execute('select id from conferences where url = %s', paras2)
                    # 获取该条数据在数据库中的id, fetchone结果为元祖
                    conference_id = cursor.fetchone()[0]

                except Exception as e:
                    # 发生错误,数据库回滚
                    self.mysql_cli.rollback()
                    logger.error(e)
                    logger.error('插入数据错误')
                    # 会议信息加入数据库失败的话,就不在查找发言人信息,直接进行下一次循环
                    continue
                finally:
                    cursor.close()


                for url in speakers_url_list:
                    # 依次打开发言人url, 并从中获取信息


                    # 将会议信息和发言人信息加入关系表
                    if all([conference_id, speaker_id]):
                        try:
                            cursor = self.mysql_cli.cursor()
                            # 将二者关系插入关系表
                            cursor.execute('insert into conferences_speakers(conference_id, speakers_id) VALUES (%s, %s)', [conference_id, speaker_id])
                            cursor.commit()
                        except Exception as e:
                            self.mysql_cli.rollback()
                            logger.error(e)
                            logger.error('关系插入失败')
                        finally:
                            # 关闭游标
                            cursor.close()
        # 无线循环跳出以后,没有后续任务后,关闭mysql数据库链接
        self.mysql_cli.close()

    def gain_speaker_info(self, url, referer):
        """
        根据url获取发言人的信息
        :param url: 发言人自己的链接
        referer: 当前链接,作为请求头的referer
        :return: 返回该条信息在数据库中的id
        """
        try:
            # proxies = {"http": "http://" + get_proxy()}
            # speaker_data = requests.get(url, headers=self.headers, proxies=proxies)
            self.headers['referer'] = referer
            speaker_data = requests.get(url, headers=self.headers)
            # 得到发言人页的信息
            speaker_data = etree.HTML(speaker_data)
            # 获取发言人姓名
            name = speaker_data.xpath('//h1/text()')[0]
            name = name.strip()
            # 职位信息
            position = speaker_data.xpath('//h1/../text()')[1].strip()
            # 发言主题
            speaker_specialities = speaker_data.xpath('//h2[@id="moreSpecilty"]/following-sibling::div[1]/text()')[
                0].strip()
            # 兴趣主题
            speaker_interested = speaker_data.xpath('//h2[@id="moreTopics"]/following-sibling::div[1]/text()')[
                0].strip()
            # 如果作者没有填写相关信息,则设置为none
            if speaker_specialities == 'This section has yet to be updated by the speaker':
                speaker_specialities = None
            if speaker_interested == 'This section has yet to be updated by the speaker':
                speaker_interested = None
        except Exception as e:
            logger.error(e)
            logger.error('查找发言人信息失败')
            position = None
            name = None
            speaker_specialities = None
            speaker_interested = None

        # 将查询到的发言人信息写进数据库(url和名字是必须信息,如果没有的话,不写入数据库)
        if all([url, name]):
            cursor = self.mysql_cli.cursor()
            try:
                speaker_info = [url, name, position, speaker_specialities, speaker_interested]
                cursor.execute(
                    'insert into speakers(url, name, position, specialties, interested) VALUES (%s, %s, %s, %s, %s)',
                    speaker_info)
                # 提交插入信息
                self.mysql_cli.commit()
            except Exception as e:
                self.mysql_cli.rollback()
                logger.error(e)
                logger.error('发言人信息插入失败')
                # 如果该条信息已经存在的话也会插入失败
                # 失败的话可以直接进行下一次循环
            #　尝试查询该ｕｒｌ所指示的任务信息
            try:
                url = [url, ]
                speaker_id = cursor.execute('select id from speakers where url = %s', url)
            except Exception as e:
                logger.error(e)
                logger.error('查询数据库出错')
                speaker_id = None
        else:
            speaker_id = None

        return speaker_id