# coding=utf-8
from selenium import webdriver
import urllib
import re
from lxml import etree
comtent = open('./tes.html')
Month = {
    'Jan': '01',
    'Feb' : '02',
    'Mar' : '03',
    'Apr' : '04',
    'May' : '05',
    'Jun' : '06',
    'Jul' : '07',
    'Aug' : '08',
    'Sep' : '09',
    'Oct' :'10',
    'Nov' : '11',
    'Dec' : '12'
}

html = comtent.read()
html = etree.HTML(html)
a = html.xpath('//div[@class="date"]/text()')[0]
# b = html.xpath('//div')
a = a.replace(',', ' ').replace('|', ' ').strip()
date_info = re.match(r'([^ ]+).*?([\d]{1,2}).*?([\d]{1,2}).*?([\d]{4})', a)
month =  date_info.group(1)
start_day =  date_info.group(2)
end_day =  date_info.group(3)
year =  date_info.group(4)

start_date = year + '-' + Month.get(month) + '-' + start_day
print start_date
area = html.xpath('//div[@class="date"]/a/text()')
print area[0]
print area[1]
area = area[0] + ',' + area[1]
print area

print '*'*30
organizer = html.xpath('//div[@class="speakers marT10"]/span/a/text()')
print organizer[0]
specialties_list = html.xpath('//div[@class="speakers"]/span/a/text()')
specialities = ''
for spe in specialties_list:
    specialities += (spe + ',')
print specialities.strip(',')
speakers =  html.xpath('//div[@id="speaker_confView"]/div/div/div/a/@href')
print speakers
speaker = html.xpath('//h5/a/text()')
print speaker

