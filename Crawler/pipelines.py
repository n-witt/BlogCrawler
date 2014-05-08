from elasticsearch import Elasticsearch

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class StoreInElasticsearch(object):
    es = Elasticsearch()
    
    def process_item(self, item, spider):        
        doc = {
               "name": item['blog_name'],
               "url": item['url'],
               "releasedate": item['releasedate'],
               "crawldate": item['crawldate'],
               "author": item['author'],
               "headline": item['headline'],
               "body": item['body'],
               "links": item['links']
               }
        
        self.es.index(index='foo', doc_type='bar', body=doc)
        return item