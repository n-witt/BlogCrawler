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
    name = 'econbrowser.com'
    start_urls = []
    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//h1[@class="entry-title"]')), callback='parse_item', follow=True),             
        Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="nav-previous"]')), follow=True),
    )

    def __init__(self, startDate, endDate, *args, **kwargs):
        try:
            startDate, endDate = toolbox.validate_date_range(startDate, endDate)
        except ValueError as e:
            raise ValueError(e.message)
        
        for i in range(0, (endDate.year-startDate.year) * 12 + (endDate.month-startDate.month) + 1):
            url = 'http://econbrowser.com/archives/' + toolbox.add_months(startDate, i).strftime('%Y/%m')
            self.start_urls.append(url)
        super(MySpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        self.log(response.url, level=log.INFO)
        sel = Selector(response)
        item = BlogItem()
        item['blog_name'] = "econbrowser"
        item['url'] = response.url
        item['releasedate'] = dparser.parse(safepop(sel.xpath('//time[@class="entry-date"]/@datetime').extract(), 0), fuzzy=True)
        item['crawldate'] = datetime.now().isoformat()
        item['author'] = safepop(sel.xpath('//a[@rel="author"]/text()').extract(), 0)
        item['headline'] = safepop(sel.xpath('//h1[@class="entry-title"]/descendant-or-self::text()').extract(), 0)
        item['body'] = safepop(mergeListElements(sel.xpath('//div[@class="entry-content"]/div[@class="addtoany_share_save_container addtoany_content_bottom"]/preceding-sibling::*/descendant-or-self::text()').extract()), 0)
        item['links'] = sel.xpath('//div[@class="entry-content"]/div[@class="addtoany_share_save_container addtoany_content_bottom"]/preceding-sibling::*/descendant-or-self::a/@href').extract()
        item['references'] = ""
        item['comments'] = self.extract_comments(sel) 
        item['tags'] = ""
        item["teaser"] = ""
        self.log("parsed %s successfully" % response.url, level=log.DEBUG)
        
        return item
    
    def extract_comments(self, sel):
        assert type(sel) == Selector
        raw_comments = sel.xpath('//section[@class="comment-content comment"]')
        comments= []
        for comment in raw_comments:
            comments.append(mergeListElements(comment.xpath('./p/text()').extract()))
        return comments
            