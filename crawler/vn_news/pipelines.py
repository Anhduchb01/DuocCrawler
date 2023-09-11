# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import logging


class VnNewsPipeline:
	def process_item(self, item, spider):
		return item
	

class MongoPipeline(object):
	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			mongo_uri=crawler.settings.get('MONGO_URI'),
			mongo_db=crawler.settings.get('MONGO_DB')
		)

	def open_spider(self, spider):
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]

	def process_item(self, item, spider):
		name = item.__class__.__name__
		title = dict(item).get('title')
		url = dict(item).get('url')
		print('title',title)
		check_exits = self.db.posts.find_one({'url': url})
		try:
			if len(title.split()) >= 3 :
				if not check_exits:
					print('Add new item to MongoDB',title)
					self.db.posts.insert_one(dict(item))	
			else :
				print('len of split title and connten < 3',title)
				print('URL',url)
		except:
			print('not have title and content')
		
		return item

	def close_spider(self, spider):
		print('Finished crawling! ',spider.name)
		print('self.mongo_uri',self.mongo_uri)
		print('self.mongo_db',self.mongo_db)
		print(self.db.crawlers.find_one({'addressPage': spider.name}))
		self.db.crawlers.update_one({'addressPage': spider.name}, {'$set': {'statusPageCrawl': 'success'}})
		print('Update status success for crawler ',spider.name)
		self.client.close()