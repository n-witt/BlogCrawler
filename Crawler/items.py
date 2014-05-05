# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class BlogItem(Item):
    blog_name = Field()
    url = Field()
    releasedate = Field()
    crawldate = Field()
    author = Field()
    headline = Field()
    body = Field()
    links = Field()