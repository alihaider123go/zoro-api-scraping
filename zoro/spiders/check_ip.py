import scrapy
from scrapy import Request
import random

class CheckIP(scrapy.Spider):
    name = "check_ip"
    user_agents_list = [
        'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    ]

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': random.choice(user_agents_list),
        'Cookie':'XSRF-TOKEN=eyJpdiI6InpPeSt1Wk9jQmVqelNWTEdjcTI5Y1E9PSIsInZhbHVlIjoibjJXSGRJMjV6UVlGSmhYWkVSMGRySDZcL3dRQ1YwZzlQazhpYWRoZWhqYnlBSk85SXY2OVhBWk5ZaThjTXpTd08iLCJtYWMiOiI3NGViZGY5MjJjMjU0MWUyZjg1NDk5YWNiNjNmNzY2ZTg4OTA4MzZlYzVmYzdiNWM1NzUzMDkzMzlkZDBmZDk1In0%3D;ip_geolocation_api_session=eyJpdiI6IkQydld3MWkzZEJJNTYyRnRWMjl0b3c9PSIsInZhbHVlIjoiOVBnMGh5U2pFSENrZXVVcWs5RXUzY0lIWGttMHJLSVdXOVVUVEliQkZ5d2UzclpjanpGQUt1ODVSeTBGSzM3UzVaTVBTbU03QTBYVnJpV2tjZzlPNWlrYSt1KzZOQ1lyTGtGeTBKQ0s1ZlcxdTBlNmFiaGZsVzhjckVucjNyeEYiLCJtYWMiOiIyYmRiNDBhNWJiNjE3NDI3NGRjMjhhNmU1MTMzOTNjM2FiNTY0MmVlYjg3MDhiOWY5ZTU5NDgyYzVkYTU5NDgyIn0%3D; _gid=GA1.2.1048097430.1724830064; _ga=GA1.1.1817898455.1724830064; _ga_DV8QRYTLH3=GS1.1.1724830063.1.0.1724830277.60.0.0; perf_dv6Tr4n=1'
    }

    # custom_settings = {
        # 'CONCURRENT_REQUESTS': 1,
    #     'HTTPPROXY_ENABLED':True,
    #     'HTTPPROXY_AUTH_ENCODING':'latin1',
    #     'APIFY_PROXY_URL':'http://groups-SHADER+BUYPROXIES94952,country-US:apify_proxy_hl2i3w4cMqwuzGyAhYqGiWqVlyItbI05TVGC@proxy.apify.com:8000',
    #     'HTTP_PROXY':'http://groups-SHADER+BUYPROXIES94952,country-US:apify_proxy_hl2i3w4cMqwuzGyAhYqGiWqVlyItbI05TVGC@proxy.apify.com:8000',
    #     'HTTPS_PROXY':'http://groups-SHADER+BUYPROXIES94952,country-US:apify_proxy_hl2i3w4cMqwuzGyAhYqGiWqVlyItbI05TVGC@proxy.apify.com:8000'
    # }


    def start_requests(self):
        for i in range(5):
            ip_check_url = 'https://api.ipify.org'
            yield Request(
                ip_check_url, 
                callback=self.check_ip,
                headers=self.headers,  
                meta={'iteration': i},
                dont_filter=True
            )
    
    def check_ip(self, response):
        ip_address = response.text
        yield {'ip_address': ip_address}
