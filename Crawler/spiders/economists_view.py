'''
Created on 02.06.2014
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
    name = 'economistsview.typepad.com'
    start_urls = []
    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//h3[@class="entry-header"]/a')), callback='parse_item', follow=True),
        Rule(SgmlLinkExtractor(restrict_xpaths=('//span[@class="pager-right"]')), follow=True),
    )

    def __init__(self, startDate, endDate, *args, **kwargs):
        try:
            startDate, endDate = toolbox.validate_date_range(startDate, endDate)
        except ValueError as e:
            raise ValueError(e.message)
        
        for i in range(0, (endDate.year-startDate.year) * 12 + (endDate.month-startDate.month) + 1):
            url = 'http://economistsview.typepad.com/' + toolbox.add_months(startDate, i).strftime('%Y/%m') + '/'
            self.start_urls.append(url)
        super(MySpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        self.log(response.url, level=log.DEBUG)
        sel = Selector(response)
        item = BlogItem()

        item['blog_name'] = "Economist's View"
        item['url'] = response.url
        item['releasedate'] = dparser.parse(mergeListElements(sel.xpath('//h2[@class="date-header"]/text()').extract())[0], fuzzy=True)
        item['crawldate'] = datetime.now().isoformat()
        item['author'] = safepop(sel.xpath('//a[@rel="author"]/text()').extract(), 0)
        item['headline'] = safepop(sel.xpath('//h3[@class="entry-header"]/a/text()').extract(), 0)
        item['body'] = safepop(mergeListElements(sel.xpath('//div[@class="entry-body"]/descendant-or-self::text()').extract()), 0)
        item['links'] = sel.xpath('//div[@class="entry-body"]/descendant-or-self::a/@href').extract()
        item['references'] = ""
        item['comments'] = ""
        #the last two elements are always "permalink" an and "comment", hence they can be discarded
        item['tags'] = sel.xpath('//p[@class="posted"]/a[@rel="author"]/following-sibling::*/text()').extract()[0:-2]
        item["teaser"] = ""
        self.log("parsed %s successfully" % response.url, level=log.INFO)
        return item
