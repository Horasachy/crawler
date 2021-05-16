from os import path
from typing import List
import time
from scrapy import Spider, Selector, Request
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from scrapy_splash import SplashRequest
from urllib.parse import urljoin
from buc_crawler.items import CompanyItem
from buc_crawler.tools import is_not_firm
from selenium.webdriver.support import expected_conditions as EC

class DGisSpider(Spider):
    name = '2gis'

    allowed_domains = [
        '2gis.ru',
    ]
    start_url = [
        'https://2gis.ru',
    ]
    cities = [
        'Москва', 'Московская область', 'Белгородская область',
        'Брянская область', 'Владимирская область', 'Воронежская область',
        'Ивановская область', ' Калужская область', 'Костромская область',
        'Курская область', 'Липецкая область', 'Орловская область',
        'Рязанская область', 'Смоленская область', 'Тамбовская область',
        'Тульская область', 'Ярославская область'
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
                cb_kwargs={'city': 'Москва'}
            )

    def parse_category_links(self, response, **kwargs):
        driver: WebDriver = response.request.meta['driver']
        try:
            accept_cookie = driver.find_element_by_xpath('//div[@class="_trvdea"]//button[@class="_1wadwrc"]')
            accept_cookie.click()
            time.sleep(3)
        except NoSuchElementException:
            pass
        search_field = driver.find_element_by_xpath('//input[contains(@class, "_xykhig")]')
        search_field.send_keys(f'{kwargs.get("city")} {self.category_list[0]}')
        time.sleep(3)
        search_field.send_keys(Keys.ENTER)
        time.sleep(3)
        self.get_companies_links(driver)
        time.sleep(3)
        for link in self.links:
            yield SplashRequest(
                url=link,
                callback=self.parse_company_detail_page,
                cb_kwargs={'city':kwargs.get('city'), 'category':self.category_list[0], 'link':link}
            )


    def parse_company_detail_page(self, response, **kwargs):
        link: str = kwargs.get('link')
        loader = ItemLoader(item=CompanyItem(), response=response)
        loader.add_xpath('name', '//span//span[@class="_oqoid"]/text()')
        loader.add_value('category', kwargs.get('category'))
        loader.add_value('city', kwargs.get('city'))
        loader.add_xpath('site', '//div[@class="_49kxlr"]//a[contains(@class, "_pbcct4") and contains(@target, "_blank")]/text()')
        loader.add_xpath('email', '//div[@class="_49kxlr"]//div//a[contains(@target,"_blank") and contains(@class, "_1nped2zk")]/text()')
        loader.add_xpath('phones', '//div[@class="_b0ke8"]//a[@class="_1nped2zk"]/@href')
        loader.add_xpath('social', '//div[@class="_oisoenu"]//a/@href')
        yield SeleniumRequest(
            url=link,
            callback=self.parse_company_products,
            cb_kwargs={'loader': loader}
        )

    def parse_company_products(self, response, **kwargs):
        driver: WebDriver = response.request.meta['driver']
        loader: ItemLoader = kwargs.get('loader')
        try:
            price = driver.find_element_by_xpath('//a[contains(@class, "_1nped2zk") and contains(text(), "Цены")]')
        except NoSuchElementException:
            price = None
        if price:
            price.click()
            time.sleep(3)
            i = 0
            while (i < 25):
                products = driver.find_elements_by_xpath('//div[@class="_8mqv20"]//div[1]') or driver.find_elements_by_xpath('//article[@class="_gc1bca"]//div[@class="_o2i0na"]')
                if len(products) > 1:
                    driver.execute_script("arguments[0].scrollIntoView();", products[-1])
                time.sleep(1)
                i += 1
            for product in products:
                loader.add_value('products', product.text)

        return loader.load_item()

    def get_companies_links(self, driver):
        while(True):
            urls = driver.find_elements_by_xpath('//div[@class="_1h3cgic"]//a')
            try:
                next_page = driver.find_element_by_xpath('//div[@class="_n5hmn94"][2]/*[name()="svg"]')
            except NoSuchElementException:
                next_page = driver.find_element_by_xpath('//div[@class="_n5hmn94"]/*[name()="svg"]')
            driver.execute_script("arguments[0].scrollIntoView();", urls[-1])
            time.sleep(1)
            if len(urls) == 12:
                for url in urls:
                    self.links.append(url.get_attribute("href"))
                time.sleep(1)
                next_page.click()
                time.sleep(1)
            else:
                for url in urls:
                    self.links.append(url.get_attribute("href"))
                    time.sleep(1)
                break