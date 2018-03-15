# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy import Item


class QqtestPipeline(object):
    def open_spider(self, spider):
        self.db_client = MongoClient('mongodb://localhost:27017')
        self.db = self.db_client['qqzone']


    def process_item(self, item, spider):
        if isinstance(item,Item):
            item = dict(item)
        self.db.qqfeed.insert_one(item)

    def close_spider(self, spider):
        self.db_client.close()