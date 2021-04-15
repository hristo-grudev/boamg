import scrapy

from scrapy.loader import ItemLoader

from ..items import BoamgItem
from itemloaders.processors import TakeFirst


class BoamgSpider(scrapy.Spider):
	name = 'boamg'
	start_urls = ['https://www.boa.mg/actualites/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="services-text"]')
		for post in post_links:
			url = post.xpath('.//a[@class="link-services"]/@href').get()
			date = post.xpath('.//time/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//a[@class="next page-link"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="entry-content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BoamgItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
