# coding=utf-8
# https://www.emedevents.com/view-all
import requests
from lxml import etree
data = {
    "orgSpeakersData":"ok",
    "spr_type":"organizer_speaker",
    "organizer_id":5997,
    "conftype":"Speaking At Organizer's Conferences"
}
url = "https://www.emedevents.com/view-all"

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept - Encoding': 'gzip',
                        'Cache-Control': 'no-cache',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                        'Connection': 'keep-alive',
                        }
data = requests.post(url, data=data, headers= headers).content
se = etree.HTML(data)
li = se.xpath('//div[@class="ellips-wrapper"]/a/@href')
print li