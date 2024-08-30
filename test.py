# import requests
# from bs4 import BeautifulSoup

# URL = "https://zoro.com"
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# }
# page = requests.get(URL, headers=headers)
# soup = BeautifulSoup(page.content, "html.parser")

# print(soup)



import requests
from requests.auth import HTTPProxyAuth

proxy = {
    "http": "http://proxy.apify.com:8000",
    "https": "http://proxy.apify.com:8000"
}

auth = HTTPProxyAuth('auto', 'apify_proxy_eIIXihl4akrdTwz1SmhFjWe5WYaeSX1iTurd')

try:
    print(proxy,auth)
    response = requests.get('https://api.prod.zoro.com/catalog/v1/catalog/product?zoroNos=G2802685&shallow=true', proxies=proxy, auth=auth)
    print(response.status_code)
except requests.exceptions.ProxyError as e:
    print(f"Proxy error: {e}")
