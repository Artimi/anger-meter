import re
import datetime
import hashlib

import dateutil.parser
import scrapy
import pytz

from crawlers.items import Article, Comment

number = re.compile(r'\d+')


def str_to_timestamp(str, default_tz=pytz.timezone('Europe/Prague')):
    dt = dateutil.parser.parse(str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=default_tz)
    return int(dt.timestamp())


class IdnesSpider(scrapy.Spider):
    name = 'idnes'
    start_urls = ['http://zpravy.idnes.cz/archiv.aspx?strana=1']

    def parse(self, response):
        for article_url in response.css('a.art-link::attr(href)').extract():
            yield scrapy.Request(article_url, callback=self.parse_article)

    def parse_article(self, response):
        article = Article()
        article['title'] = response.xpath('//title/text()').extract()[0]
        article['url'] = response.url
        article['content'] = '\n'.join(response.xpath('//*[@id="art-text"]/div/p/text()').extract())
        datetime_str = response.xpath('//*[@id="space-a"]/div[1]/div[1]/span/span/@content').extract()[0]
        article['timestamp'] = str_to_timestamp(datetime_str)
        yield article

        comment_url_extracted = response.xpath('//*[@id="moot-linkin"]/@href').extract_first()
        comment_url = response.urljoin(comment_url_extracted)
        comment_url += '&razeni=time'
        yield scrapy.Request(comment_url, callback=self.parse_comments, meta={'article_url': article['url']})

    def parse_comments(self, response):
        article_url = response.meta['article_url']
        for sel in response.xpath("//*[contains(@class, 'contribution')]"):
            yield self._extract_comment(sel, article_url)

        next_page = response.xpath("//a[contains(@title, 'další')]/@href").extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_comments, meta={'article_url': article_url})

    def _extract_comment(self, sel, article_url):
        comment = Comment()
        comment['author'] = "".join(sel.xpath(".//h4[contains(@class, 'name')]/a/text()").extract())
        comment['author_id'] = "".join(sel.xpath(".//h4[contains(@class, 'name')]/sup/text()").extract())
        comment["content"] = sel.xpath(".//div[contains(@class, 'user-text')]/p/text()").extract_first().strip()
        score = sel.xpath(".//div[contains(@class, 'score')]/span/text()").extract()
        comment['score_plus'] = int(number.findall(score[0].strip())[0])
        comment['score_minus'] = int(number.findall(score[1].strip())[0])
        datetime_str = sel.xpath(".//div[contains(@class, 'date')]/text()").extract_first().strip()
        comment['timestamp'] = str_to_timestamp(datetime_str)
        comment['article_url'] = article_url
        comment['comment_id'] = hashlib.md5('{}_{}_{}'.format(
            comment['author_id'], comment['timestamp'], comment['article_url']
        ).encode()).hexdigest()
        return comment
