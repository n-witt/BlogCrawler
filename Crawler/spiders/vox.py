'''
Created on 19.05.2014
@author: nils witt
'''

from datetime import datetime
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from Crawler import toolbox
from Crawler.items import BlogItem
from Crawler.toolbox import safepop, mergeListElements, init_logger
import dateutil.parser as dparser


class MySpider(CrawlSpider):
    name = 'voxeu.org'
    start_urls = []
    start = datetime.now()
    end = datetime.now()
    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="vox-article autoclear"]/h2'))\
             , callback='parse_item'),
    )

    def __init__(self, startDate, endDate, *args, **kwargs):
        init_logger()
        
        try:
            toolbox.validate_date_range(startDate, endDate)
        except ValueError as e:
            raise ValueError(e.message)
        
        for i in range(0, (self.end.year-self.start.year) * 12 + (self.end.month-self.start.month) + 1):
            foo = 'http://www.voxeu.org/columns/archive/' + toolbox.add_months(self.start, i).strftime('%Y-%m')
            self.start_urls.append(foo)
        super(MySpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        sel = Selector(response)
        item = BlogItem()
        item['blog_name'] = "Vox"
        item['url'] = response.url
        item['releasedate'] = dparser.parse(mergeListElements(sel.xpath('/html/body/div[2]/div/div[2]/p/text()').extract())[0], fuzzy=True)
        item['crawldate'] = datetime.now().isoformat()
        item['author'] = self.extract_authors(safepop(sel.xpath('/html/body/div[2]/div/div[2]/p/strong/text()').extract(), 0))
        item['headline'] = safepop(sel.xpath('/html/body/div[2]/div/div[2]/h1/text()').extract(), 0).strip()
        item['body'] = safepop(mergeListElements(sel.xpath('//div[@class="article-content"]/h1[contains(., "Reference")]/preceding-sibling::*/text()').extract()), 0)
        item['links'] = sel.xpath('//div[@class="article-content"]/h1[contains(., "Reference")]/following-sibling::*/a/@href').extract()
        item['references'] = self.extract_references(sel.xpath('//div[@class="article-content"]/h1[contains(., "Reference")]/following-sibling::*'))
        item['comments'] = ""
        item['tags'] = ""
        item["teaser"] = safepop(mergeListElements(sel.xpath('//div[contains(@class, "teaser")]/descendant-or-self::*/text()').extract()), 0).strip()
        log.msg("parsed %s successfully" % response.url, level=log.INFO)
        
        return item
    
    def extract_references(self, selector):
        references = []
        for n in selector:
            references.append(mergeListElements(n.xpath(".//text()").extract()))
        return references

    def extract_authors(self, s):
        authors = []
        for n in s.split(","):
            author = n.strip()
            if author != u'':
                authors.append(author)
        return authors