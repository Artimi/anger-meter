# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import boto3

import crawlers.items


class DBPipeline(object):

    def open_spider(self, spider):
        self._dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
        self._articles = self._dynamodb.Table('articles')
        self._comments = self._dynamodb.Table('comments')

    def process_item(self, item, spider):
        if isinstance(item, crawlers.items.Article):
            self._articles.put_item(Item=dict(item))
        elif isinstance(item, crawlers.items.Comment):
            self._comments.put_item(Item=dict(item))

        return item
