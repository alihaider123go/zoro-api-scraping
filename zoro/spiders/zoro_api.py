import csv
from datetime import datetime
from scrapy import Spider, Request
import os
import random


class zoroSpider(Spider):
    name = "zoro_api"
    url = "https://api.prod.zoro.com/scm/v1/inventory/availability/{}?quantity={}"
    records = []
    user_agents_list = [
        'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    ]

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'apikey': '924526ffbdad25e5923b',
        'user-agent': random.choice(user_agents_list),
    }

    custom_settings = {
        'FEED_URI': 'zoro.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'HTTPERROR_ALLOW_ALL': True,
        'CONCURRENT_REQUESTS': 5,
        'DOWNLOAD_DELAY': 2,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408,403],
        # 'HTTPPROXY_ENABLED':True,
        # 'DOWNLOADER_MIDDLEWARES':{
        #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,
        #     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        # },
        # 'PROXY':'http://groups-BUYPROXIES94952,country-US:apify_proxy_hl2i3w4cMqwuzGyAhYqGiWqVlyItbI05TVGC@proxy.apify.com:8000'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_ids = []

        # inputs.csv is input file contains all model number
        with open('inputs.csv', mode='r', newline='', encoding='utf-8') as input_file:
            reader = csv.reader(input_file)
            for row in reader:
                self.input_ids.append(row[0])

    def start_requests(self):
        for id_ in self.input_ids[:]:
            if id_:
                url = "https://api.prod.zoro.com/catalog/v1/catalog/product?zoroNos={}&shallow=true".format(id_)
                yield Request(url, callback=self.parse, headers=self.headers, meta={'proxy': 'http://groups-BUYPROXIES94952,country-US:apify_proxy_hl2i3w4cMqwuzGyAhYqGiWqVlyItbI05TVGC@proxy.apify.com:8000','id': id_}, dont_filter=True)

    def parse(self, response, **kwargs):
        item_num = response.meta['id']
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        data = response.json()
        product = data.get('products', [{}])[0]
        item = {
            "itemNumber": item_num,
            "price": product.get('price', ''),
            "freightCost/surcharge": '0.0' if not product.get('freightCost', '') else product.get('freightCost', ''),
            "eligibility(Promotion Restriction)": 'YES',
            "category": ' / '.join(itm['name'] for itm in product.get('primaryCategoryPaths', [])),
            "brand": product.get('brand', ''),
            "image": product.get('media', [{}])[0].get('name', ''),
            "minRetailQty": product.get('minRetailQty', ''),
            "Instock Qty": '0',
            "Shipping_date": product.get('leadTime', ''),
            "date": formatted_datetime
        }
        for attr in product.get('attributes', []):
            if 'promotion' in attr.get('name', '').lower():
                if 'not' in attr.get('value', '').lower():
                    item['eligibility(Promotion Restriction)'] = 'NO'
                    break
        yield item
        yield Request(self.url.format(item_num, 100), callback=self.quantity, headers=self.headers,
                      meta={'id': item_num, 'item': item, 'stock': 100}, dont_filter=True)

    def quantity(self, response):
        data = response.json()
        item_num = response.meta['id']
        stock = response.meta['stock']
        item = response.meta['item']
        if int(stock) >= 300:
            item['Instock Qty'] = 300
            self.records.append(item)
            yield item
        elif int(stock) == 0:
            self.records.append(item)
            yield item
        elif 'instock' in data.get('payload', {}).get('availabilityType', '').lower():
            yield Request(self.url.format(item_num, stock + 100), callback=self.quantity, headers=self.headers,
                          meta={'id': item_num, 'item': item, 'stock': stock + 100}, dont_filter=True)
        elif 'limitedstock' in data.get('payload', {}).get('availabilityType',
                                                           '').lower() and 'order exceeds' not in data.get('payload',
                                                                                                           {}).get(
            'availabilityToolTip', '').lower():
            yield Request(self.url.format(item_num, stock + 1), callback=self.limited, headers=self.headers,
                          meta={'id': item_num, 'item': item, 'stock': stock + 1}, dont_filter=True)
        elif 'order exceeds' in data.get('payload', {}).get('availabilityToolTip',
                                                            '').lower() or 'backorder' in data.get('payload', {}).get(
            'availabilityType', '').lower():
            pre_stock = stock - 100
            stock_range = int((stock + pre_stock) / 2)
            yield Request(self.url.format(item_num, stock_range), callback=self.exceed, headers=self.headers,
                          meta={'id': item_num, 'item': item, 'stock': stock_range, 'start_value': pre_stock,
                                'end_value': stock}, dont_filter=True)
        else:
            self.records.append(item)
            yield item

    def exceed(self, response):
        data = response.json()
        item_num = response.meta['id']
        stock = response.meta['stock']
        start = response.meta['start_value']
        end = response.meta['end_value']
        item = response.meta['item']
        if int(stock) >= 300:
            item['Instock Qty'] = 300
            self.records.append(item)
            yield item
        elif int(stock) == 0:
            self.records.append(item)
            yield item
        elif 'instock' in data.get('payload', {}).get('availabilityType', '').lower():
            stock = stock + 1
            stock_range = int((stock + end) / 2)
            yield Request(self.url.format(item_num, stock_range), callback=self.exceed, headers=self.headers,
                          meta={'id': item_num, 'item': item, 'stock': stock_range, 'start_value': stock,
                                'end_value': end})
        elif 'limitedstock' in data.get('payload', {}).get('availabilityType', '').lower() and not data.get('payload',
                                                                                                            {}).get(
            'availabilityToolTip', '').lower().strip():
            yield Request(self.url.format(item_num, stock + 1), callback=self.limited, headers=self.headers,
                          meta={'id': item_num, 'item': item, 'stock': stock + 1})
        elif 'order exceeds' in data.get('payload', {}).get('availabilityToolTip',
                                                            '').lower() or 'backorder' in data.get('payload', {}).get(
            'availabilityType', '').lower():
            stock = stock - 1
            stock_range = int((start + stock) / 2)
            yield Request(self.url.format(item_num, stock_range), callback=self.exceed, headers=self.headers,
                          meta={'id': item_num, 'item': item, 'stock': stock_range, 'start_value': start,
                                'end_value': stock})
        else:
            self.records.append(item)
            yield item

    def limited(self, response):
        data = response.json()
        item_num = response.meta['id']
        stock = response.meta['stock']
        item = response.meta['item']
        if int(stock) >= 300:
            item['Instock Qty'] = 300
            self.records.append(item)
            yield item
        elif int(stock) == 0:
            self.records.append(item)
            yield item
        elif 'limitedstock' in data.get('payload', {}).get('availabilityType', '').lower() and not data.get('payload',
                                                                                                            {}).get(
                'availabilityToolTip', '').lower().strip():
            yield Request(self.url.format(item_num, stock + 1), callback=self.limited, headers=self.headers,
                          meta={'id': item_num, 'item': item, 'stock': stock + 1}, dont_filter=True)
        elif 'order exceeds' in data.get('payload', {}).get('availabilityToolTip',
                                                            '').lower() or 'backorder' in data.get('payload', {}).get(
                'availabilityType', '').lower():
            qty = stock - 1
            if int(qty) > 300:
                qty = 300
            item['Instock Qty'] = qty
            self.records.append(item)
            yield item

        else:
            self.records.append(item)
            yield item

    def close(self, reason):
        pass
        # scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # # add credential json file's path at the place of cred.json
        # file_path = os.path.join(os.path.dirname(__file__), 'cred.json')
        # creds = ServiceAccountCredentials.from_json_keyfile_name(file_path, scopes)
        # client = gspread.authorize(creds)
        # # gsheet share link
        # # add you sheet link here
        # sheet_url = ''
        # sheet = client.open_by_url(sheet_url)
        # worksheet = sheet.worksheet('output')

        # headers = self.records[0].keys()
        # header_row = worksheet.row_values(1)
        # if not header_row:
        #     worksheet.append_row(list(headers))

        # output_records = []
        # for rec in self.records:
        #     output_records.append(list(rec.values()))

        # worksheet.append_rows(output_records)

