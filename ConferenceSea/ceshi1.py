# coding=utf-8
import requests
hear={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"Accept-Encoding": "gzip, deflate, br",
"X-Requested-With": "XMLHttpRequest"
}
data = {
"month": "All",
"sterm": "",
"cme_from": 0,
"cme_to": 500,
"country": "All",
"city": "All",
"ctype": "All",
"specialty": "All",
"page": 100,
"year": "2018",
"custom_date_flag": "",
"custom_date_from":"04%2F01%2F2010" ,
"custom_date_to": "04%2F01%2F2018",
"org_confs": "",
"search_organizer":"",
"org_conference_type":"",
"org_sort_conferences": ""
}


hear['Referer'] = "https://www.emedevents.com/Conferences/searchConference?headerSearchType=conference"
url1 = "https://www.emedevents.com/conferences/searchFilter"
response = requests.post(url1, data=data, headers=hear)
print response.status_code
print response.content
from lxml import etree
se = etree.HTML(response.content)
a = se.xpath('//div[@class="conf_summery"]/div[@class="c_name"]/a/@href')
print a
print len(a)







