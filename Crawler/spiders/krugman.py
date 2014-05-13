'''
Created on 25.04.2014

@author: nils witt
'''

import datetime
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from Crawler import toolbox
from Crawler.items import BlogItem
from Crawler.toolbox import safepop


class MySpider(CrawlSpider):
    name = 'krugman.blogs.nytimes.com'
    start_urls = ['http://krugman.blogs.nytimes.com/']

    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//h3[@class="entry-title"]', )), callback='parse_item'),
    )

    def parse_item(self, response):
        sel = Selector(response)
        item = BlogItem()
        links = []
        item['blog_name'] = "The Conscience of a Liberal"
        item['url'] = response.url
        item['releasedate'] = safepop(sel.xpath("/html/body/div/main/div[2]/div/div/div/article/header/div[2]/time/@datetime").extract(), 0)
        item['crawldate'] = datetime.datetime.now().isoformat()
        item['author'] = "Paul Krugman"
        item['headline'] = safepop(sel.xpath("/html/body/div/main/div[2]/div/div/div/article/header/h1/text()").extract(), 0)
        item['body'] = safepop(toolbox.mergeListElements(sel.xpath('//p[@class="story-body-text"]/text() | //p[@class="story-body-text"]/a/text()').extract()), 0)
        for i in sel.xpath("//p[@class='story-body-text']/a/attribute::href").extract():
            links.append(i)
        item['links'] = links
        log.msg("parsed %s successfully" % response.url, level=log.INFO)
        return item
