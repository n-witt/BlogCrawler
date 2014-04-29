'''
Created on 25.04.2014

@author: nils witt
'''

from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.spider import Spider
from Crawler.items import CrawlerItem


#from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
class blogCrawler(Spider):
    name='blogCrawler'
    start_urls = ['http://krugman.blogs.nytimes.com/']
    #rules = (Rule(SgmlLinkExtractor(restrict_xpaths="/html/body/div/main/div[2]/div/div/div/section/div/article"), callback='parse_item'),)

    def mergeDictElements(self, item):
        newItem = ""
        for i in item:
            newItem += i
        return [newItem]
    
    def parse(self, response):
        sel = Selector(response)
        items = []
        for article in sel.xpath("//article"):
            #print article.extract()
            linkExtractor = SgmlLinkExtractor()
            item = CrawlerItem()
            item['headline'] = article.xpath('header/h3/a/text()').extract()
            item['text'] = article.xpath('div/p[@class="story-body-text"]/text()').extract()
            item['text'] = self.mergeDictElements(item['text'])
            item['links'] = linkExtractor.extract_links(article)
            items.append(item)
        return items