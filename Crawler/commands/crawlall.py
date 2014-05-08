'''
Created on 06.05.2014
@author: user
@summary: this class provides the 'scrapy crawlall'-command. it takes
          zero params and starts all spiders within the scrapy project
@warning: the run-method contains weird code borrowed from the 'scrapy crawl'
          command (and some other sources). i tried to understand it, but
          failed. i hope this code will never throw any errors.
          hope dies last.
@requires: this command requires a running elasticsearch-instance at
           localhost:9200
@
'''
from scrapy import signals
from twisted.internet import reactor
from scrapy.command import ScrapyCommand
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings

class Command(ScrapyCommand):

    requires_project = True
    closedSpiders = 0
    numberOfSpiders = 0

    def __init__(self):
        settings = get_project_settings()
        self.numberOfSpiders = len(Crawler(settings).spiders.list())
        
    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        settings = get_project_settings()
        crawler_process = self.crawler_process
        
        for spider_name in crawler_process.create_crawler().spiders.list():
            crawler = Crawler(settings)
            crawler.signals.connect(self.quitReactor, signal=signals.spider_closed)
            crawler.configure()
            spider = crawler.spiders.create(spider_name)
            crawler.crawl(spider)
            crawler.start()
        crawler_process.start()
        
    def quitReactor(self, spider):
        self.closedSpiders += 1
        if self.closedSpiders >= self.numberOfSpiders:
            reactor.stop()  #@UndefinedVariable