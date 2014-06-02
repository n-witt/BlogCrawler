# Scrapy settings for Crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'Crawler'

SPIDER_MODULES = ['Crawler.spiders']
NEWSPIDER_MODULE = 'Crawler.spiders'
LOG_LEVEL = 'INFO'
REDIRECT_ENABLED = True

ITEM_PIPELINES = {
    'Crawler.pipelines.StoreInElasticsearch': 1,
}

COMMANDS_MODULE = 'Crawler.commands'
#USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0"
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Crawler (+http://www.yourdomain.com)'
