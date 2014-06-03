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
    name = 'zerohedge.com'
    start_urls = []
    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//li[@class="print_html"]')), callback='parse_item', follow=True),             
        Rule(SgmlLinkExtractor(restrict_xpaths=('//h2[@class="title"]/a')), follow=True),
        Rule(SgmlLinkExtractor(restrict_xpaths=('//li[@class="pager-next"]/a')), follow=True),
    )

    def __init__(self, startDate, endDate, *args, **kwargs):
        try:
            startDate, endDate = toolbox.validate_date_range(startDate, endDate)
        except ValueError as e:
            raise ValueError(e.message)
        
        for i in range(0, (endDate.year-startDate.year) * 12 + (endDate.month-startDate.month) + 1):
            url = 'http://www.zerohedge.com/archive/all/' + toolbox.add_months(startDate, i).strftime('%Y/%m')
            self.start_urls.append(url)
        super(MySpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        self.log(response.url, level=log.INFO)
        sel = Selector(response)
        item = BlogItem()
        item['blog_name'] = "Zero Hedge"
        item['url'] = response.url
        item['releasedate'] = dparser.parse(sel.xpath('//span[@class="submitted"]/text()').extract()[-1], fuzzy=True)
        item['crawldate'] = datetime.now().isoformat()
        item['author'] = safepop(sel.xpath('//span[@class="submitted"]/a/text()').extract(), 0)
        item['headline'] = safepop(sel.xpath('//h1[@class="print-title"]/text()').extract(), 0)
        item['body'] = safepop(mergeListElements(sel.xpath('//div[@class="content"]/descendant-or-self::text()').extract()), 0)
        item['links'] = self.extract_links(sel.xpath('//div[@class="print-links"]/p/text()').extract())
        item['references'] = ""
        item['comments'] = ""
        #the last two elements are always "permalink" an and "comment", hence they can be discarded
        item['tags'] = sel.xpath('//ul[@class="links"]/li/a/text()').extract()
        item["teaser"] = ""
        self.log("parsed %s successfully" % response.url, level=log.DEBUG)
        return item

    def extract_links(self, urls):
        new_urls = []
        assert type(urls) == list
        for url in urls:
            if len(url) >= 2: 
                new_urls.append(url.split(" ")[1])            
        return new_urls
        