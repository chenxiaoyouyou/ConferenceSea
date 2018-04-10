#coding=utf-8
# import re
# a = """Mar 01 - dec 07, 2018&nbsp;&nbsp; | &nbsp;&nbsp;
# """
# date_str = re.match(r'([^ ]+) ([\d]{1,2}) - ([a-zA-Z]{3})?.*?([\d]{1,2}).*?([\d]{4})', a)
# print date_str.group(1)
# print date_str.group(2)
# print date_str.group(3)
# print date_str.group(4)
# print date_str.group(5)
# begin_date = '01/05/2016'
# year = begin_date[-4:]
# print year.

from lxml import etree
import re

file = open('./speaker.html')
speaker_data = etree.HTML(file.read())

name = speaker_data.xpath('//h1/text()')[0]
name = name.strip()
print name
# 职位信息
position = speaker_data.xpath('//h1/../text()')[1].strip()
print position
a = re.match(r"(.*)\|(.*)", position)

print a.group(1).strip()
print a.group(2).strip()


# 发言主题
speaker_specialities = speaker_data.xpath('//h2[@id="moreSpecilty"]/following-sibling::div[1]/text()')[
    0].strip()
print speaker_specialities
# 兴趣主题
speaker_interested = speaker_data.xpath('//h2[@id="moreTopics"]/following-sibling::div[1]/text()')[
    0].strip()
print speaker_interested
# 如果作者没有填写相关信息,则设置为none
if speaker_specialities == 'This section has yet to be updated by the speaker':
    speaker_specialities = None
if speaker_interested == 'This section has yet to be updated by the speaker':
    speaker_interested = None

line = re.match(r'(.*?)\|(.*)', 'dsfad|saf')
print line.group(1)
print line.group(2)