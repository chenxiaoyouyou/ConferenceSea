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
    """从块代理首页获取代理并从中加入列表"""
    # 快代理
    pro_list = []
    url = 'https://www.kuaidaili.com/free/'
    content = requests.get(url)
    selector = etree.HTML(content.text)
    ip = selector.xpath('//tr/td[1]/text()')
    port = selector.xpath('//tr/td[2]/text()')
    for i in range(len(ip)):
        pro_list.append(ip[i] + ':' + port[i])
    # time.sleep(300)
    # 随机返回一个可用的ip和端口
    return random.choice(pro_list)