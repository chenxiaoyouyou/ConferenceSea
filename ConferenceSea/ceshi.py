import requests
proxies = {
    'http':'http://115.28.146.28:16816'
}

resoponse = requests.get('http://www.baidu.com', proxies= proxies)
print resoponse.request
