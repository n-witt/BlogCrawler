#BlogCrawler

This prototype is a focus web crawler that allows the visiting pre-defined websites, extract their contents and save them into an [elasticsearch](https://www.elastic.co/products/elasticsearch) datastore. The blog crawler is based on [scrapy](http://scrapy.org), a python framework to facilitate the development of webscraping applications.
##Requirements
  * Linux or Mac OS X
  * Python 2.7 or newer
  * Scrapy 0.22 or newer
  * lxml 
  * pyOpenSSL
  * Elasticsearch 1.2.1 or newer
  * Java Runtime Environment 7 or newer

##Installation
The easiest way to install the required software is to use the packet manager of the OS. 
The commands below are tested with Ubuntu 14.04, but they should work on all the distributions that use the `apt-get` packet manager. For `yum`-based systems like Fedora and SuSE some modifications might be required.

The following commands will make sure that all requirements are met:
```
sudo apt-get install -y build-essential git python-pip python python-dev libxml2-dev libxslt-dev lib32z1-dev openjdk-7-jdk
sudo pip install pyopenssl lxml scrapy elasticsearch dateutils Twisted service_identity
```

Elasticsearch can not be installed via `apt-ge`. Hence, this has to be done manually. First we download the latest Elasticsearch version:
```
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-x.y.z.deb
```
where x.y.z. is the current version number and thus needs to be replaced. Then the installation process can be trigged via:
```
sudo dpkg -i elasticsearch-x.y.z.deb
```
Again, x.y.z refers to the latest's version number and has to be replaced. The installation is complete and elasticsearch can be started using the following command:
```
sudo service elasticsearch start
```
It is to note, that the service will not start automatically when the computer boots up. If this is required, the following command has to be used:
```
sudo update-rc.d elasticsearch defaults 95 10
```
The blog crawler can be cloned from Github:
```
git clone purl.org/eexcess/components/research/blogcrawler}}
```
The crawler can be invoked by changing into the just cloned repository-directory and starting the script `crawlall.sh`. That the process can take several hours. To interrupt the process <ctrl+z> must be pressed.
