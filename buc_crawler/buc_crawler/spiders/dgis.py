from os import path
from typing import List
import time
from scrapy import Spider, Selector, Request
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from scrapy_splash import SplashRequest

from buc_crawler.items import CompanyItem
from buc_crawler.tools import is_not_firm


class DGisSpider(Spider):
    name = '2gis'

    allowed_domains = [
        '2gis.ru',
    ]
    start_url = [
        'https://2gis.ru/ufa/firm/2393065583034549',
    ]
    cities = [
        'Уфа', 'Салават'
        # 'Москва', 'Московская область', 'Белгородская область',
        # 'Брянская область', 'Владимирская область', 'Воронежская область',
        # 'Ивановская область', ' Калужская область', 'Костромская область',
        # 'Курская область', 'Липецкая область', 'Орловская область',
        # 'Рязанская область', 'Смоленская область', 'Тамбовская область',
        # 'Тульская область', 'Ярославская область'
    ]
    category_list = [
        'Металлопрокат', 'Строительная компания', 'Торгово-производственная компания',
        'Строительные материалы', 'Чёрный металлопрокат', 'Цветной металл'
    ]
    links = []
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
            'scrapy_selenium.SeleniumMiddleware': 800,
        },
        'ITEM_PIPELINES': {}
    }

    def start_requests(self):
        for url in self.start_url:
            yield SeleniumRequest(
                url=url,
                callback=self.parse_category_links,
                cb_kwargs={'city': 'Уфа'}
            )

    def parse_category_links(self, response, **kwargs):
        driver: WebDriver = response.request.meta['driver']
        search_field = driver.find_element_by_xpath('//input[contains(@class, "_xykhig")]')
        search_field.send_keys(f'{kwargs.get("city")} {self.category_list[0]}')
        time.sleep(3)
        search_field.send_keys(Keys.ENTER)
        time.sleep(3)
        # self.scroll_down_load_companies(driver)
        time.sleep(3)
        self.get_companies_links(driver)
        for link in self.links:
            yield SeleniumRequest(
                url=link,
                callback=self.parse_company_detail_page,
                cb_kwargs={'city':kwargs.get('city'), 'category':self.category_list[0]}
            )


    def get_companies_links(self, driver):
        while(True):
            urls = driver.find_elements_by_xpath('//div[@class="_1h3cgic"]//a')
            time.sleep(1)
            try:
                next_page = driver.find_element_by_xpath('//div[@class="_n5hmn94"][2]/*[name()="svg"]')
                time.sleep(1)
            except NoSuchElementException:
                next_page = driver.find_element_by_xpath('//div[@class="_n5hmn94"]/*[name()="svg"]')
                time.sleep(1)
            time.sleep(1)
            driver.execute_script("arguments[0].scrollIntoView();", urls[-1])
            time.sleep(2)

            if len(urls) == 12:
                for url in urls:
                    self.links.append(url.get_attribute("href"))
                time.sleep(2)
                next_page.click()
                time.sleep(1)
            else:
                break;


    def parse_company_detail_page(self, response, **kwargs):
        time.sleep(2)
        loader = ItemLoader(item=CompanyItem(), response=response)
        loader.add_xpath('name', '//span[@class="_oqoid"]/text()')
        loader.add_value('category', kwargs.get('category'))
        loader.add_value('city', kwargs.get('city'))
        loader.add_xpath('site', '//div[@class="_49kxlr"]//a[contains(@class, "_pbcct4") and contains(@target, "_blank")]')
        loader.add_xpath('email', '//div[@class="_49kxlr"]//div//a[contains(@target,"_blank") and contains(@class, "_1nped2zk")]/text()')
        loader.add_xpath('phones', '//div[@class="_b0ke8"]//a[@class="_1nped2zk"]/@href')
        loader.add_xpath('social', '//div[@class="_oisoenu"]//a/@href')

        return loader.load_item()

    def parse_company_products(self, response, **kwargs):
        pass


    # def parse_rubric(self, response, **kwargs):
    #     sub_rubrics_container_selector: Selector = response.xpath('(//div[@class="_1667t0u"])[2]')
    #     sub_rubric_selectors = sub_rubrics_container_selector.css('div._mq2eit')
    #
    #     for selector in sub_rubric_selectors:
    #         name = selector.css('a *::text').get()
    #         url = selector.css('a *::attr(href)').get()
    #         yield Request(
    #             url=response.urljoin(url),
    #             callback=self.parse_yet_rubric,
    #             cb_kwargs={
    #                 'city': kwargs.get('city'),
    #                 'rubric': kwargs.get('rubric'),
    #                 'sub_rubric': name
    #             }
    #         )
    #
    # def parse_yet_rubric(self, response, **kwargs):
    #     sub_rubric_selectors = response.xpath('(//div[@class="_13w22bi"])')
    #     for selector in sub_rubric_selectors:
    #         name = selector.css('a *::text').get()
    #         url = selector.css('a *::attr(href)').get()
    #         yield Request(
    #             url=response.urljoin(url),
    #             callback=self.parse_company_list_page,
    #             cb_kwargs={
    #                 'city': kwargs.get('city'),
    #                 'rubric': kwargs.get('rubric'),
    #                 'sub_rubric': kwargs.get('sub_rubric'),
    #                 'category': name
    #             }
    #         )
    #
    # def parse_company_list_page(self, response, **kwargs):
    #     next_page = response.xpath('//div[@class="_12wz8vf"]//div[@class="_1swfts6i"]/following::a[1]/@href').get()
    #
    #     company_selectors = response.xpath('//div[@class= "_y3rccd"]')
    #     for selector in company_selectors:
    #         name = selector.css('a *::text').get()
    #         url = selector.css('a *::attr(href)').get()
    #         yield Request(
    #             url=response.urljoin(url),
    #             callback=self.parse_company_detail_page,
    #             cb_kwargs={
    #                 'city': kwargs.get('city'),
    #                 'rubric': kwargs.get('rubric'),
    #                 'sub_rubric': kwargs.get('sub_rubric'),
    #                 'category': kwargs.get('category'),
    #                 'name': name
    #             }
    #         )
    #
    #     yield Request(
    #         url=response.urljoin(next_page),
    #         callback=self.parse_company_list_page,
    #         cb_kwargs={
    #             'city': kwargs.get('city'),
    #             'rubric': kwargs.get('rubric'),
    #             'sub_rubric': kwargs.get('sub_rubric'),
    #             'category': kwargs.get('category'),
    #         }
    #     )