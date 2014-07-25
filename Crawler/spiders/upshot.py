'''
Created on 06.05.2014

@author: user
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
from Crawler.toolbox import safepop, mergeListElements
import dateutil.parser as dparser


class MySpider(Spider):
    name = 'nytimes.com/upshot'
    start_urls = []
    
    '''
    the constructor fetches pages from the content delivery interface and
    extracts the contained url which are pointing to the actual blog-entries.
    currently it grabs all available entries (~160 on 2014-05-15), there is
    no upper barrier. it raises an exception (KeyError) if the response
    won't correspond the expectations.   
    '''
    
    def __init__(self, startDate, endDate, *args, **kwargs):
        try:
            toolbox.validate_date_range(startDate, endDate)
        except ValueError as e:
            raise ValueError(e.message)
        
        startDate = dparser.parse(startDate).replace(day=1).replace(tzinfo=None)
        endDate = dparser.parse(endDate).replace(day=1).replace(tzinfo=None)
        endDate = endDate.replace(day=calendar.monthrange(int(endDate.strftime('%Y')), int(endDate.strftime('%m')))[1])
        endDate = endDate + datetime.timedelta(hours=23, minutes=59, seconds=59)        
        
        try:
            response = self.fetch_json_doc(0)
            hits = response['response']['meta']['hits']
            offset = response['response']['meta']['offset']
            i = 1
            while hits > offset:
                for n in response['response']['docs']:
                    pubDate = dparser.parse(n['pub_date'], fuzzy=True).replace(tzinfo=None)
                    if pubDate >= startDate and pubDate <= endDate:
                        self.start_urls.append(n['web_url'])
                        log.msg(n['web_url'], level=log.DEBUG)
                response = self.fetch_json_doc(i)
                hits = response['response']['meta']['hits']
                offset = response['response']['meta']['offset']
                i += 1                
        except KeyError:
            self.msg("Error reading init-Page for spider " + self.name + ".\n\
#The required response.meta-element was not contained in the response.", level=log.ERROR)
            raise KeyError("Required Key in dict not found.")
        super(MySpider, self).__init__(*args, **kwargs)
        
    def parse(self, response):
        sel = Selector(response)
        item = BlogItem()
        links = []
        item['blog_name'] = "The Upshot"
        item['url'] = response.url
        item['releasedate'] = sel.xpath('//p[@class="byline-dateline"]/time[@class="dateline"]/attribute::datetime').extract()
        item['crawldate'] = datetime.datetime.now().isoformat()
        item['author'] = sel.xpath('//span[@class="byline-author"]/text()').extract()                                                                               
        item['headline'] = sel.xpath('//h1[@class="story-heading" and @itemprop="headline"]/text()').extract()
        item['body'] = safepop(mergeListElements(sel.xpath('//p[@class="story-body-text story-content"]/text() | //p[@class="story-body-text story-content"]/a/text()').extract()), 0)
        for i in sel.xpath("//p[@class='story-body-text story-content']/a/attribute::href").extract():
            links.append(i)
        item['links'] = links
        item['references'] = ""
        item['comments'] = ""
        item['tags'] = ""
        item['teaser'] = ""
        self.log("parsed %s successfully" % response.url, level=log.INFO) 
        return item
        
    '''
    the main purpose of this method is to ban the ugly url out of the important
    elements of the source code. it expects you to pass an int-parameter (otherwise 
    it will throw an AssertionError) which refers to a page. it returns the response
    in a json-style format (a python dict with nested elements). 
    '''
    def fetch_json_doc(self, page):
        assert type(page) == int
        response = urllib2.urlopen("http://query.nytimes.com/svc/add/v1/sitesearch.json?\
fq=section_name%3A(%22The+Upshot%22)+AND+document_type%3A(%22article%22)&page="+ str(page))
        return json.loads(response.read())
