# coding=utf-8
import requests
from lxml import etree

file = open('./tes.html')
selector = etree.HTML(file.read())
title = selector.xpath('//h1/text()')[0]
                # 获取会议的开始日期和结束日期
date_str = selector.xpath('//div[@class="date"]/text()')[0]
print title
print date_str
organizer = selector.xpath('//div[@class="speakers marT10"]/span/a/text()')[0]
organizer_url = selector.xpath('//div[@class="speakers marT10"]/span/a/@href')[0]
print organizer
print organizer_url

file1 = open('./organizer.html')
selector1 = etree.HTML(file1.read())
location = selector1.xpath('//div[@class="location"]/text()')
print location[0].strip() + location[1].strip()
view_all = selector1.xpath('//div[@class="people-info marT10"]/a')
print view_all
# 不在获取view-all, 直接查找
