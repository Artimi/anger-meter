# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import dataset
import crawlers.items
import sqlalchemy.exc


class DBPipeline(object):
    def open_spider(self, spider):
        self.db = dataset.connect('postgresql://postgres:postgres@localhost:5432/anger-meter')
        self.article = self.db['article']
        self.comment = self.db['comment']

    def process_item(self, item, spider):
        if isinstance(item, crawlers.items.Article):
            try:
                self.article.insert(item)
            except sqlalchemy.exc.IntegrityError:
                self.article.update(item, ['url'])
        elif isinstance(item, crawlers.items.Comment):
            try:
                self.comment.insert(item)
            except sqlalchemy.exc.IntegrityError:
                self.comment.update(item, ['article_url', 'author', 'datetime'])

        return item
