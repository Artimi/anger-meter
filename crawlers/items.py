# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Article(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    datetime = scrapy.Field()


class Comment(scrapy.Item):
    author = scrapy.Field()
    content = scrapy.Field()
    score_plus = scrapy.Field()
    score_minus = scrapy.Field()
    datetime = scrapy.Field()
