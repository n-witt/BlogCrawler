'''
Created on 25.04.2014

@author: nils witt
'''

import calendar
import datetime
import json
from scrapy import log
from scrapy.selector import Selector
from scrapy.spider import Spider
import urllib2

from Crawler import toolbox
from Crawler.items import BlogItem
from Crawler.toolbox import safepop, init_logger
import dateutil.parser as dparser


class MySpider(Spider):
    name = 'krugman.blogs.nytimes.com'
    start_urls = []
    
    def __init__(self, startDate, endDate, *args, **kwargs):
        init_logger()
        #validating, parsing and converting the date/time-stuff
        try:
            toolbox.validate_date_range(startDate, endDate)
        except ValueError as e:
            raise ValueError(e.message)
        startDate = dparser.parse(startDate).replace(day=1).replace(tzinfo=None)
        endDate = dparser.parse(endDate).replace(tzinfo=None)
        endDate = endDate.replace(day=calendar.monthrange(int(endDate.strftime('%Y')), int(endDate.strftime('%m')))[1])
        endDate = endDate + datetime.timedelta(hours=23, minutes=59, seconds=59)
        
        try:
            json_page = self.fetch_json_doc(0)
        except urllib2.HTTPError:
            raise urllib2.HTTPError('The init-Page could not be fetched. Aborting.')
        i = 0
        while json_page['more_posts_next_page'] == True:
            pubDate = datetime.datetime.now() #for initializing-reasons
            for n in json_page['posts']:
                sel = Selector(text=n['html'])
                pubDate = dparser.parse(safepop(sel.xpath('//time/@datetime').extract(), 0)).replace(tzinfo=None)
                if pubDate >= startDate and pubDate <= endDate:
                    url = safepop(sel.xpath('//div[@data-url]/attribute::data-url').extract(), 0)
                    self.start_urls.append(url)
                    log.msg(url, level=log.DEBUG)
            if pubDate < startDate:
                break
            i += 1
            json_page = self.fetch_json_doc(i)
        super(MySpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        sel = Selector(response)
        links = []
        item = BlogItem()
        item['blog_name'] = "The Conscience of a Liberal"
        item['url'] = safepop(sel.xpath('//div[@data-url]/attribute::data-url').extract(), 0)
        item['releasedate'] = dparser.parse(safepop(sel.xpath('//time/@datetime').extract(), 0)).replace(tzinfo=None)
        item['crawldate'] = datetime.datetime.now().isoformat()
        item['author'] = "Paul Krugman"
        item['headline'] = sel.xpath('//h1[@class="entry-title"]/text()').extract()
        item['body'] = safepop(toolbox.mergeListElements(sel.xpath('//p[@class="story-body-text"]/text() | //p[@class="story-body-text"]/a/text()').extract()), 0)
        for i in sel.xpath("//p[@class='story-body-text']/a/attribute::href").extract():
            links.append(i)
        item['links'] = links
        item['references'] = ""
        item['comments'] = ""
        item['tags'] = ""
        item['teaser'] = ""
        log.msg("parsed %s successfully" % response.url, level=log.DEBUG)
        return item
            
    def fetch_json_doc(self, page):
        assert type(page) == int
        response = urllib2.urlopen("http://krugman.blogs.nytimes.com/more_posts_json/?homepage=1&apagenum="+ str(page))
        return json.loads(response.read())