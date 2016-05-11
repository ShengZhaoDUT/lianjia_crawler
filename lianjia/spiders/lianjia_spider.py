#-*- coding: UTF-8 -*-
import scrapy
import sys
from scrapy.contrib.spiders import Rule  
from scrapy.contrib.linkextractors import LinkExtractor
from pymongo import MongoClient
import time
import re

reload(sys)
sys.setdefaultencoding( "utf-8" )

class LianjiaSpider(scrapy.spiders.Spider):

	name = "lianjia"
	allow_domains = ["lianjia.com"]
	start_urls = []

	def __init__(self):
		for i in range(1, 101):
			self.start_urls.append("http://bj.lianjia.com/xiaoqu/pg"+str(i))
		self.client = MongoClient('localhost', 27017)
		self.xiaoquCollection = self.client['lianjia']['xiaoqu']

	def parse(self, response):
		print response.url
		root = response.xpath('//div[@class="list-wrap"]/ul/li/div[@class="info-panel"]')
		title = root.xpath('h2/a/text()').extract()
		price = root.xpath('div[@class="col-3"]/div/span/text()').extract()
		dealInfo = root.xpath('div[@class="col-1"]/div[@class="where"]/a/text()').extract()
		num = root.xpath('div[@class="col-2"]/div/div/a/span/text()').extract()
		roomInfo = root.xpath('div[@class="col-1"]/div[@class="other"]/div/text()').extract()
		district = root.xpath('div[@class="col-1"]/div[@class="other"]/div/a/text()').extract()
		ts = time.strftime('%Y-%m-%d',time.localtime(time.time()))
		print ts
		records = []
		for i in range (0, len(title)):
			# 静安里 30天成交3套   11套正在出租 47947 25 塔楼/板楼/塔板结合 1961年建造 朝阳 国展
			
			deal = 0
			rent = 0
			buildYear = 0
			dealList = self.getNum(dealInfo[i * 2])
			rentList = self.getNum(dealInfo[i * 2 + 1])
			buildYearList = self.getNum(roomInfo[i * 2 + 1])
			if (len(dealList) == 2):
				deal = int(dealList[1])
			if (len(rentList) == 1):
				rent = int(rentList[0])
			if (len(buildYearList) == 1):
				buildYear = int(buildYearList[0])
			record = {'date': ts, 'name': title[i], 'deal': deal, 'rent': rent, 'price': int(price[i]), 'num_sell': int(num[i]), 'architecture': roomInfo[i * 2], 'year': buildYear, 'district': district[i * 2], 'sub_district': district[i * 2 + 1]}
			records.append(record)
			print title[i], deal, rent, int(price[i]), int(num[i]), roomInfo[i * 2], buildYear, district[i * 2], district[i * 2 + 1]
		self.xiaoquCollection.insert_many(records)

	def getNum(self, src):
		return re.findall( r'\d+', src)
