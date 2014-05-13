'''
Created on 06.05.2014

@author: user
'''
import datetime
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from Crawler.items import BlogItem
from Crawler.toolbox import safepop, mergeListElements


class MySpider(CrawlSpider):
    name = 'nytimes.com/upshot'
    start_urls = ['http://www.nytimes.com/upshot']

    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//h2[@class="story-heading stream-item-headline"]', )), callback='parse_item'),
    )
    def parse_item(self, response):
        sel = Selector(response)
        item = BlogItem()
        links = []
        item['blog_name'] = "The Upshot"
        item['url'] = response.url
        item['releasedate'] = self.parse_date(safepop(sel.xpath("//article/header/div/div/p/time/@datetime | //article/header/div/div/div/p/time/@datetime").extract(), 0))
        item['crawldate'] = datetime.datetime.now().isoformat()
        item['author'] = sel.xpath("//article/div[3]/p/span/a/span/text() | //article/div[3]/p/span/span/text()").extract()                                                                               
        item['headline'] = safepop(sel.xpath("//article/header/div/h1/text()").extract(), 0)
        item['body'] = safepop(mergeListElements(sel.xpath('//p[@class="story-body-text story-content"]/text() | //p[@class="story-body-text story-content"]/a/text()').extract()), 0)
        for i in sel.xpath("//p[@class='story-body-text story-content']/a/attribute::href").extract():
            links.append(i)
        item['links'] = links
        log.msg("parsed %s successfully" % response.url, level=log.INFO) 
        return item

    def parse_date(self, d):
        if d is not None:
            year, month, day = d.split('-')
            return datetime.datetime(int(year), int(month), int(day), 0, 0).isoformat()
        else:
            return None