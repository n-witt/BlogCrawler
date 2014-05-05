'''
Created on 25.04.2014

@author: nils witt
'''

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from Crawler.items import BlogItem
import datetime
from scrapy import log


class MySpider(CrawlSpider):
    name = 'blogCrawler'
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
        item['releasedate'] = sel.xpath("/html/body/div/main/div[2]/div/div/div/article/header/div[2]/time/@datetime").extract().pop()
        item['crawldate'] = datetime.datetime.now().isoformat()
        item['author'] = "Paul Krugman"
        item['headline'] = sel.xpath("/html/body/div/main/div[2]/div/div/div/article/header/h1/text()").extract().pop(0)
        item['body'] = self.mergeListElements(sel.xpath('//p[@class="story-body-text"]/text() | //p[@class="story-body-text"]/a/text()').extract()).pop(0)
        for i in sel.xpath("//p[@class='story-body-text']/a/attribute::href").extract():
            links.append(i)
        item['links'] = links
        log.msg("parsed %s successfully" % response.url, level=log.INFO) 
        return item
    
    def substring(self, s, leftDelimiter, rightDelimiter):
        """extracts substrings in string that are enclosed by leftDelimiter an rightDelimiter.
        multiple appearances of the delimiters are handeled as well.
        example: "live long and prosper" with delimiter "l" and " " will result in ["ive", "ong"]
        all parameters must be strings
        """
        if isinstance(s, str) and isinstance(leftDelimiter, str) and isinstance(rightDelimiter, str):
            result = []
            leftBorder = 0
            rightBorder = 0
            while True:
                leftBorder = s.find(leftDelimiter, rightBorder)
                if leftBorder == -1:
                    break
                rightBorder = s.find(rightDelimiter, leftBorder+len(leftDelimiter))
                result.append(s[leftBorder+len(leftDelimiter):rightBorder])
                leftBorder = rightBorder + 1
            return result
        else:
            log.msg("invalid parametertype used", level=log.DEBUG)
            raise Exception("one or more parameter are not of type str")
    
    def mergeListElements(self, item):
        """merges n elements of item into one.
        e.g. ["f", "o", "o"] becomes ["foo"].
        item must be a list.
        """
        if isinstance(item, list):
            newItem = ""
            for i in item:
                newItem += i
            return [newItem]
        else:
            log.msg("item is not a list", level=log.DEBUG)
            raise Exception("item is not a list")
