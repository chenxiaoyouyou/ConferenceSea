# coding=utf-8
import logging
from logging.handlers import RotatingFileHandler
import requests
from lxml import etree
import random
import datetime

# 配置日志功能
# 创建日志对象
logger = logging.getLogger()
# 设定等级
logger.setLevel(level=logging.ERROR)
# 添加handler
file_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=5)
# 设定日志格式
formater = logging.Formatter('%(levelname)s %(filename)s : %(lineno)d  %(message)s ')
file_handler.setFormatter(formater)
# 为logger对象添加格式
logger.addHandler(file_handler)


# 获取代理
def get_proxy():
    """从daxiang代理首页获取代理并从中加入列表"""
    # 快代理
    url = 'http://tvp.daxiangdaili.com/ip/?tid=556978916294208&num=50000&protocol=https'
    data = requests.get(url)
    # print data.content
    ip_list = data.content
    ip_list = ip_list.split()
    print ip_list
    a = []

        # proxies = "https://" + random.choice(ip_list)
    for proxies in  ip_list:
        url1=  'https://www.baidu.com'
        try:
            response = requests.get(url1, proxies=proxies)
            if response.status_code == 200:
                # break
                print proxies
                # a.append(proxies)
        except Exception as e:
            # print e
            pass

    # print a
    # return proxies

# get_proxy()