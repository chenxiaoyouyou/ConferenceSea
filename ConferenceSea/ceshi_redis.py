#coding=utf-8
# import pymysql
# mysql_cli = pymysql.connect(host='localhost', port=3306, database='conference', user='root', password='mysql',
#                                  charset='utf8')
#
# paras = ['title', 'current_url', '1990-03-20', '1990-03-20', 'area', 'organizer', 'specialities']
# cursor = mysql_cli.cursor()
# # a = cursor.execute('insert into conference (title, url, start_date, end_date, area, organized, specialties) VALUES (%s, %s, %s, %s, %s, %s, %s)', paras)
# mysql_cli.commit()
# paras2 = ['current_url',]
# cursor.execute('select id from conference where url = %s', paras2)
# print cursor.fetchall()
#
# # print a

import requests
from lxml import etree
import random

a = []


# 获取代理
def get_proxy():
    """从块代理首页获取代理并从中加入列表"""
    while True:
        # 快代理
        url = 'https://www.kuaidaili.com/free/'
        content = requests.get(url)
        selector = etree.HTML(content.text)
        ip = selector.xpath('//tr/td[1]/text()')
        port = selector.xpath('//tr/td[2]/text()')
        for i in range(len(ip)):
            a.append(ip[i] + ':' + port[i])
        print a
        break
get_proxy()
print random.choice(a)