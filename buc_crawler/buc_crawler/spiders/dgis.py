from os import path
from typing import List

from scrapy import Spider, Selector, Request
from scrapy.loader import ItemLoader


from scrapy_splash import SplashRequest

from buc_crawler.items import CompanyItem
from buc_crawler.tools import is_not_firm


class DGisSpider(Spider):
    name = '2gis'

    allowed_domains = [
        '2gis.ru',
    ]
    start_url = [
        'https://2gis.ru/moscow/',
    ]
    custom_settings = {
        'BOT_NAME': 'Thank you so much!',
        'ROBOTSTXT_OBEY': False,
        'URLLENGTH_LIMIT': 4166,
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru',
        },
        'DOWNLOADER_MIDDLEWARES': {
            'buc_crawler.middlewares.CrawlingDownloaderMiddleware': 543,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        'ITEM_PIPELINES': {}
    }

    def start_requests(self):
        for url in self.start_url:
            yield SplashRequest(
                url=path.join(url, 'rubrics'),
                callback=self.parse_city,
                cb_kwargs={'city': 'Москва'}
            )

    def parse_city(self, response, **kwargs):
        rubric_selectors: List[Selector] = response.xpath('//div[contains(@class, "_mq2eit")]')
        for selector in rubric_selectors:
            name = selector.css('a *::text').get()
            url = selector.css('a::attr(href)').get()
            if is_not_firm(url):
                yield Request(
                    url=response.urljoin(url),
                    callback=self.parse_rubric,
                    cb_kwargs={
                        'city': kwargs.get('city'),
                        'rubric': name
                    }
                )

    def parse_rubric(self, response, **kwargs):
        sub_rubrics_container_selector: Selector = response.xpath('(//div[@class="_1667t0u"])[2]')
        sub_rubric_selectors = sub_rubrics_container_selector.css('div._mq2eit')

        for selector in sub_rubric_selectors:
            name = selector.css('a *::text').get()
            url = selector.css('a *::attr(href)').get()
            yield Request(
                url=response.urljoin(url),
                callback=self.parse_yet_rubric,
                cb_kwargs={
                    'city': kwargs.get('city'),
                    'rubric': kwargs.get('rubric'),
                    'sub_rubric': name
                }
            )

    def parse_yet_rubric(self, response, **kwargs):
        sub_rubric_selectors = response.xpath('(//div[@class="_13w22bi"])')
        for selector in sub_rubric_selectors:
            name = selector.css('a *::text').get()
            url = selector.css('a *::attr(href)').get()
            yield Request(
                url=response.urljoin(url),
                callback=self.parse_company_list_page,
                cb_kwargs={
                    'city': kwargs.get('city'),
                    'rubric': kwargs.get('rubric'),
                    'sub_rubric': kwargs.get('sub_rubric'),
                    'category': name
                }
            )

    def parse_company_list_page(self, response, **kwargs):
        next_page = response.xpath('//div[@class="_12wz8vf"]//div[@class="_1swfts6i"]/following::a[1]/@href').get()

        company_selectors = response.xpath('//div[@class= "_y3rccd"]')
        for selector in company_selectors:
            name = selector.css('a *::text').get()
            url = selector.css('a *::attr(href)').get()
            yield Request(
                url=response.urljoin(url),
                callback=self.parse_company_detail_page,
                cb_kwargs={
                    'city': kwargs.get('city'),
                    'rubric': kwargs.get('rubric'),
                    'sub_rubric': kwargs.get('sub_rubric'),
                    'category': kwargs.get('category'),
                    'name': name
                }
            )

        yield Request(
            url=response.urljoin(next_page),
            callback=self.parse_company_list_page,
            cb_kwargs={
                'city': kwargs.get('city'),
                'rubric': kwargs.get('rubric'),
                'sub_rubric': kwargs.get('sub_rubric'),
                'category': kwargs.get('category'),
            }
        )

    def parse_company_detail_page(self, response, **kwargs):
        loader = ItemLoader(item=CompanyItem(), response=response)
        loader.add_value('city', kwargs.get('city'))
        loader.add_value('rubric', kwargs.get('rubric'))
        loader.add_value('sub_rubric', kwargs.get('sub_rubric'))
        loader.add_value('category', kwargs.get('category'))
        loader.add_value('url', response.url)
        loader.add_xpath('name', '(//span[@class="_oqoid"])[1]/text()')
        loader.add_xpath('kind', '(//span[@class="_oqoid"])[2]/text()')
        loader.add_xpath('tel', '//div[contains(@class, "_b0ke8")]//a/@href')
        loader.add_xpath('email', '//a[contains(@href, "mailto")]/@href')
        loader.add_xpath('website', '//div[@class="_49kxlr"]//a[@class="_pbcct4"]/@text')
        loader.add_xpath('networks', '//div[@class="_14uxmys"]//a/@href')
        return loader.load_item()
