# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QqtestItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Feed(scrapy.Item):
    id = scrapy.Field() # 表示该条说说的id
    content = scrapy.Field() # 该条说说的内容
    createTime = scrapy.Field() # 该说说创建时间
    comments_list = scrapy.Field() # 该条说说的评论集合