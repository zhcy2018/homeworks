# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import time
import random
import redis
class TutorialPipeline:
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
    r = redis.Redis(connection_pool=pool)
    def process_item(self, item, spider):
        self.r.lpush('book_review1',json.dumps(item['book_info']))
        return item
