#coding=utf-8
import re
a = """Mar 01 - dec 07, 2018&nbsp;&nbsp; | &nbsp;&nbsp;
"""
date_str = re.match(r'([^ ]+) ([\d]{1,2}) - ([a-zA-Z]{3})?.*?([\d]{1,2}).*?([\d]{4})', a)
print date_str.group(1)
print date_str.group(2)
print date_str.group(3)
print date_str.group(4)
print date_str.group(5)
begin_date = '01/05/2016'
year = begin_date[-4:]
print year
