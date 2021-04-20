import scrapy
from scrapy_selenium import SeleniumRequest

class DGisSpider(scrapy.Spider):
    name = 'dgis'
    allowed_domains = ['2gis.ru']
    start_urls = ['https://2gis.ru/']

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        self.logger.info(response.request.meta['driver'].title)
