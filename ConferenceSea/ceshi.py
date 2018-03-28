import requests
proxies = {
    'http':'http://115.193.97.23:9000'
}

resoponse = requests.get('http://www.baidu.com', proxies= proxies)
print resoponse.text
