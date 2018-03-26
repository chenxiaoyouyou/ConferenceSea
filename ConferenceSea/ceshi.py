# coding=utf-8
from selenium import webdriver
import urllib
from lxml import etree

# driver = webdriver.PhantomJS()
# driver.get('./tes.html')
# datas = driver.find_elements_by_xpath('//a')
# print type(datas)
# for data in datas:
#     print data
#



# end = {'custom_enddate': '01/02/2017'}
# end = urllib.urlencode(end)
# print end
html = """
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>

    <p>hello</p>
    <p>world</p>
    <a href="www.dfds">a1</a>
    <a href="dfada">a2</a>
    <div>div1</div>


</body>
</html>
"""
html = etree.HTML(html)
a = html.xpath('//a[1]/text()')
b = html.xpath('//div')
print a
print b
c = """
                                        JW Marriott Phoenix Desert Ridge Resort & Spa
5350 E Marriott Dr
Phoenix, Arizona, United States Of America

"""
c = c.strip()
print c
