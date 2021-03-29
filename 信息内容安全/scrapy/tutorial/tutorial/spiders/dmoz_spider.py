import scrapy
import json
import random
import time
import os
import pprint
import copy
from tutorial.items import TutorialItem


class DmozSpider(scrapy.Spider):
    name = "dmoz"
    start_urls = []
    allowed_domains = ["douban.com", "book.douban.com"]

    start_urls = [
        "https://m.douban.com/rexxar/api/v2/subject_collection/ECKM5FBEI/items?start=0&count=50&items_only=1&for_mobile=1"  # 获得书本详情页api
    ]

    def parse(self, response):
        item = TutorialItem()
        item['book_info'] = {}
        data = json.loads(response.body)['subject_collection_items']
        for i in data:
            item['book_info'] = {'book_name': i['title'], 'review': ''}
            time.sleep(random.randint(3, 6))
            yield scrapy.Request(url=i['url'], callback=self.parse1, meta={'item': copy.deepcopy(item)})    #对书本详情页发起请求

    def parse1(self, response):
        item = response.meta['item']
        url_id = response.xpath('//div/@data-cid').extract()[0:2]
        time.sleep(random.randint(3, 6))
        tample = 'https://book.douban.com/j/review/{}/full'
        for i in url_id:
            time.sleep(random.randint(3, 6))
            yield scrapy.Request(url=tample.format(i), callback=self.parse2, meta={'item': copy.deepcopy(item)})    #对书评发起请求

    def parse2(self, response):
        item = response.meta['item']
        item['book_info']['review'] = (json.loads(response.body)['html'])
        time.sleep(random.randint(3, 6))
        yield copy.deepcopy(item)           #将item给予pipeline进行处理
