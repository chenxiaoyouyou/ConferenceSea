# coding=utf-8
# import lxml
import re
from lxml import etree
f = open('./organizer.html')
content = f.read()
# result = re.findall(r'javascript', content)
# print result
res = etree.HTML(content)
a = res.xpath("//title/text()")[0].strip()
print a


url= "https://www.emedevents.com/organizer-profile/international-society-for-diseases-of-the-esophagus-isde-6053"
organizer_id = re.match(r'.*?-(\d+)$', url)
print organizer_id.group(1)
a = res.xpath("//h1/following-sibling::div[1]/text()")[0].strip()
print a
b = res.xpath('//div[@class="contact-address"]/div[1]/text()')[0].strip()
print b
p = res.xpath('//div[@id="Summary"]/p/text()')
a = ''
for pa in p:
    a += pa

print a