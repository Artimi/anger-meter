import scrapy
import re
from crawlers.items import Article, Comment
import datetime
number = re.compile(r'\d+')


class IdnesSpider(scrapy.Spider):
    name = 'idnes'
    start_urls = ['http://ekonomika.idnes.cz/vyroci-provozu-railjetu-u-ceskych-drah-d9h-/eko-doprava.aspx?c=A170310_203809_eko-doprava_suj']

    def parse(self, response):
        article = Article()
        article['title'] = response.xpath('//title/text()').extract()[0]
        article['url'] = response.url
        article['content'] = '\n'.join(response.xpath('//*[@id="art-text"]/div/p/text()').extract())
        article['datetime'] = response.xpath('//*[@id="space-a"]/div[1]/div[1]/span/span/@content').extract()[0]
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
        comment["content"] = sel.xpath(".//div[contains(@class, 'user-text')]/p/text()").extract_first().strip()
        score = sel.xpath(".//div[contains(@class, 'score')]/span/text()").extract()
        comment['score_plus'] = int(number.findall(score[0].strip())[0])
        comment['score_minus'] = int(number.findall(score[1].strip())[0])
        datetime_str = sel.xpath(".//div[contains(@class, 'date')]/text()").extract_first().strip()
        comment['datetime'] = datetime.datetime.strptime(datetime_str, '%d.%m.%Y %H:%M')
        comment['article_url'] = article_url
        return comment
