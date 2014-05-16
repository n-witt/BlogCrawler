'''
Created on 06.05.2014

@author: user
'''
import datetime
import json
from scrapy import log
from scrapy.selector import Selector
from scrapy.spider import Spider
import urllib2

from Crawler.items import BlogItem
from Crawler.toolbox import safepop, mergeListElements


class MySpider(Spider):
    name = 'nytimes.com/upshot/json'
    start_urls = []
    
    '''
    the constructor grabs pages of the content delivery interface and
    extracts the contained url which are pointing to the actual blog-entries.
    currently it grabs all available entries (~160 on 2014-05-15), there is
    no upper barrier. it raises an exception (KeyError) if the response
    won't correspond the expectations.   
    '''
    
    def __init__(self, *args, **kwargs):
        log.start(loglevel='WARNING', logstdout=False)       
        try:
            response = self.fetch_json_doc(1)
            hits = response['response']['meta']['hits']
            offset = response['response']['meta']['offset']
            i = 2
            while hits > offset:
                for n in response['response']['docs']:
                    self.start_urls.append(n['web_url'])
                    log.msg(n['web_url'], level=log.DEBUG)
                response = self.fetch_json_doc(i)
                hits = response['response']['meta']['hits']
                offset = response['response']['meta']['offset']
                i += 1                
        except KeyError:
            log.msg("Error reading init-Page for spider " + self.name + ".\n\
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
        log.msg("parsed %s successfully" % response.url, level=log.INFO) 
        return item
        
    '''
    the main purpose of this method is to ban the ugly url out of the important
    elements of the source code. it expects you to pass an int-parameter (otherwise 
    it will throw an AssertionError) which refers to a page. it returns the response
    to in a json-style format (a python dict with nested elements). 
    '''
    def fetch_json_doc(self, page):
        assert type(page) == int
        response = urllib2.urlopen("http://query.nytimes.com/svc/add/v1/sitesearch.json?\
fq=section_name%3A%28%22The+Upshot%22%29+AND+document_type%3A%28%22article%22%29&page="+ str(page) + "\
&end_date=" + str(datetime.datetime.today().date()))
        return json.loads(response.read())