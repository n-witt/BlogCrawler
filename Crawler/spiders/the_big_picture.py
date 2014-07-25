'''
Created on 03.06.2014
@author: nils witt
'''

from datetime import datetime
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from Crawler import toolbox
from Crawler.items import BlogItem
from Crawler.toolbox import safepop, mergeListElements
import dateutil.parser as dparser


class MySpider(CrawlSpider):
    name = 'ritholtz.com'
    start_urls = []
    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//div/h2/a')), callback='parse_item', follow=True),             
        Rule(SgmlLinkExtractor(restrict_xpaths=('//a[@class="next page-numbers"]')), follow=True),
    )

    def __init__(self, startDate, endDate, *args, **kwargs):
        try:
            startDate, endDate = toolbox.validate_date_range(startDate, endDate)
        except ValueError as e:
            raise ValueError(e.message)
        
        for i in range(0, (endDate.year-startDate.year) * 12 + (endDate.month-startDate.month) + 1):
            url = 'http://www.ritholtz.com/blog/' + toolbox.add_months(startDate, i).strftime('%Y/%m') + "/"
            self.start_urls.append(url)
        super(MySpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        self.log(response.url, level=log.DEBUG)
        sel = Selector(response)
        item = BlogItem()
        item['blog_name'] = "The BIG Picture"
        item['url'] = response.url
        item['releasedate'] = dparser.parse(sel.xpath('//p[@class="byline"]/text()').extract()[-1], fuzzy=True)
        item['crawldate'] = datetime.now().isoformat()
        item['author'] = safepop(sel.xpath('//span[@class="author"]/text()').extract(), 0)
        item['headline'] = safepop(sel.xpath('//div[@class="headline"]/h2/a/text()').extract(), 0)
        item['body'] = safepop(mergeListElements(sel.xpath('//a[@rel="category tag"]/parent::*/preceding-sibling::*/descendant-or-self::*/text()').extract()), 0)
        item['links'] = sel.xpath('//a[@rel="category tag"]/parent::*/preceding-sibling::*/descendant-or-self::*/@href').extract()
        item['references'] = ""
        item['comments'] = sel.xpath('//div[@class="comment-meta commentmetadata"]/following-sibling::p/text()').extract() 
        item['tags'] = sel.xpath('//a[@rel="category tag"]/text()').extract()
        item["teaser"] = ""
        self.log("parsed %s successfully" % response.url, level=log.INFO)
        
        return item