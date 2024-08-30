import scrapy
from bs4 import BeautifulSoup

class ZoroSpiderSpider(scrapy.Spider):
    name = "zoro_spider"
    start_urls = [
        "https://www.zoro.com/buyers-products-b27082az-14-inch-clevis-with-pin-and-cotter-pin-kit-zinc-plated-b27082azkt/i/G812385835/"
        ]
    def parse(self, response):
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        item_number = soup.find('span', {'data-za': 'PDPZoroNo'}).text
        
        yield {'item_number':item_number}
