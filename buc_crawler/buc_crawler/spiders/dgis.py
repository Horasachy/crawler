import time
import logging
from typing import List

from selenium.webdriver.common.by import By

from buc_crawler.xpaths import DGisMapPath
from scrapy import Spider, Selector, Request
from selenium.webdriver.firefox.webdriver import WebDriver
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from scrapy_splash import SplashRequest
from buc_crawler.items import CompanyItem
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

xpath = DGisMapPath()


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
    custom_settings = {
        'BOT_NAME': 'Thank you so much!',
        'ROBOTSTXT_OBEY': False,
        'URLLENGTH_LIMIT': 4166,
        'CONCURRENT_REQUESTS': 200,
        'DOWNLOAD_DELAY': 0.50,
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru',
        },
        'SPIDER_MIDDLEWARES': {
            'buc_crawler.middlewares.CrawlingSpiderMiddleware': 543,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'buc_crawler.middlewares.CrawlingDownloaderMiddleware': 543,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
            'scrapy_selenium.SeleniumMiddleware': 800,
        },
        'ITEM_PIPELINES': {}
    }

    def start_requests(self):
        for city in self.cities:
            yield SeleniumRequest(
                    url=self.start_url[0],
                    callback=self.parse_category_links,
                    cb_kwargs={'city': city},
                    wait_time=10,
                    wait_until=EC.presence_of_element_located((By.XPATH, xpath.search)),
                    dont_filter=True
                )

    def parse_category_links(self, response, **kwargs):
        driver: WebDriver = response.request.meta['driver']
        city: str = kwargs.get("city")
        urls: List = []
        accept_cookie(driver)
        for category in self.category_list:
            search_field = driver.find_element_by_xpath(xpath.search)
            time.sleep(3)
            search_field.send_keys(f'{city} {category}')
            time.sleep(3)
            search_field.send_keys(Keys.ENTER)
            time.sleep(3)
            fill_and_prepare_urls_of_companies(driver, city, category, urls)
            time.sleep(3)
            search_clear(driver)

        for url in urls:
            yield SplashRequest(
                url=url['href'],
                callback=self.parse_company_detail_page,
                cb_kwargs={'city': url['city'], 'category': url['category']}
            )

    def parse_company_detail_page(self, response, **kwargs):
        loader: ItemLoader = ItemLoader(item=CompanyItem(), response=response)
        loader.add_value('category', kwargs.get('category'))
        loader.add_value('city', kwargs.get('city'))
        loader.add_xpath('site', xpath.company_site)
        loader.add_xpath('name', xpath.company_name)
        loader.add_xpath('email', xpath.company_email)
        loader.add_xpath('phones', xpath.company_phones)
        loader.add_xpath('social', xpath.company_social)
        return loader.load_item()


def fill_and_prepare_urls_of_companies(driver: WebDriver, city: str, category: str, urls: List) -> None:
    while True:
        logger.info(f"City:{city} Category:{category}")
        urls_xpath: List[Selector] = driver.find_elements_by_xpath(xpath.companies_urls)
        try:
            next_page: Selector = driver.find_element_by_xpath(xpath.next_page_one)
        except NoSuchElementException:
            next_page: Selector = driver.find_element_by_xpath(xpath.next_page_two)
        driver.execute_script("arguments[0].scrollIntoView();", urls_xpath[-1])
        time.sleep(1)
        if len(urls_xpath) == 12:
            for url in urls_xpath:
                urls.append({'href': url.get_attribute("href"), 'city': city, 'category': category})
            next_page.click()
            time.sleep(1)
        else:
            for url in urls_xpath:
                urls.append({'href': url.get_attribute("href"), 'city': city, 'category': category})
            time.sleep(1)
            break


def accept_cookie(driver: WebDriver) -> None:
    try:
        accept_cookie: Selector = driver.find_element_by_xpath(xpath.accept_cookie)
        accept_cookie.click()
        time.sleep(3)
    except NoSuchElementException:
        pass


def search_clear(driver: WebDriver) -> None:
    try:
        search_clear: Selector = driver.find_element_by_xpath(xpath.search_clear)
        search_clear.click()
        time.sleep(3)
    except NoSuchElementException:
        pass
