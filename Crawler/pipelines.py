from scrapy import log
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient


class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

'''
Created on 05.05.2014

@author: nils witt
@summary: this class makes sure that the collected scrapy items
          become persisted into an elasticsearch-db. 
'''

class StoreInElasticsearch(object):
    
    es = Elasticsearch()
    ic = IndicesClient(es)
    index = 'foo'
    doc_type = 'bar'
    
    def process_item(self, item, spider):
        
        #create a convenient index, if not already exists
        if not self.ic.exists_type(index=self.index, doc_type=self.doc_type):
            self.create_index(self.es)
        
        blog_entry = {
               "blog_name": item['blog_name'],
               "url": item['url'],
               "releasedate": item['releasedate'],
               "crawldate": item['crawldate'],
               "author": item['author'],
               "headline": item['headline'],
               "body": item['body'],
               "links": item['links'],
               "references" : item['references'],
               "comments" : item['comments'],
               "tags" : item['tags'],
               "teaser" : item['teaser']
               }
        count_url_query = {"query": {
                        "term": {
                           "url": item['url']
                        }
                      }
                    }
        
        #checks, if a document (identified by its url) is already stored
        hits = self.es.count(index=self.index, doc_type=self.doc_type, body=count_url_query)
        if hits['count'] == 0:
            #insert into index
            self.es.index(index=self.index, doc_type=self.doc_type, body=blog_entry)
            log.msg("%s inserted into elasticsearch" % item['url'], level=log.INFO)
        return item
    
    def create_index(self, es):
        mapping = {
           "mappings" : {
              "bar" : {
                 "properties" : {
                    "author" : {
                       "type" : "string"
                    },
                    "body" : {
                       "type" : "string"
                    },
                    "crawldate" : {
                       "type" : "date",
                       "format" : "dateOptionalTime"
                    },
                    "headline" : {
                       "type" : "string"
                    },
                    "links" : {
                       "type" : "string"
                    },
                    "name" : {
                       "type" : "string"
                    },
                    "releasedate" : {
                       "type" : "date",
                       "format" : "dateOptionalTime"
                    },
                    "url" : {
                       "index" : "not_analyzed",
                       "type" : "string"
                    }
                  }
                }
              }
            }
        self.ic.create(self.index, mapping)
