'''
Created on 25.04.2014

@author: nils witt
'''

import datetime
import json
from scrapy import log
from scrapy.selector import Selector
from scrapy.spider import Spider

from Crawler import toolbox
from Crawler.items import BlogItem
from Crawler.toolbox import safepop


class MySpider(Spider):
    name = 'json.krugman.blogs.nytimes.com'
    start_urls = ['http://krugman.blogs.nytimes.com/more_posts_json/?homepage=1&apagenum=1']

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        for i in json_response["posts"]:
            links = []
            sel = Selector(text=i['html'])
            item = BlogItem()
            item['blog_name'] = "The Conscience of a Liberal"
            item['url'] = sel.xpath('//div[@data-url]/attribute::data-url').extract()
            item['releasedate'] = sel.xpath('//time/@datetime').extract()
            item['crawldate'] = datetime.datetime.now().isoformat()
            item['author'] = "Paul Krugman"
            item['headline'] = sel.xpath('//h3[@class="entry-title"]/a/text()').extract()
            item['body'] = safepop(toolbox.mergeListElements(sel.xpath('//p[@class="story-body-text"]/text() | //p[@class="story-body-text"]/a/text()').extract()), 0)
            for i in sel.xpath("//p[@class='story-body-text']/a/attribute::href").extract():
                links.append(i)
            item['links'] = links
            log.msg("parsed %s successfully" % response.url, level=log.INFO)
            yield item
