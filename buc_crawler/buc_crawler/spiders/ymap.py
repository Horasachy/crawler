import time
import logging
from abc import ABC
from typing import List
from scrapy.loader import ItemLoader
from buc_crawler.xpaths import YandexMapPath
from scrapy_selenium import SeleniumRequest
from scrapy import Spider, Selector, Request
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy_splash import SplashRequest
from buc_crawler.items import CompanyItem
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)

xpath = YandexMapPath()


class YmapSpider(Spider, ABC):
    name = 'ymap'
    allowed_domains = ['yandex.ru']
    start_urls = ['https://yandex.ru/maps/']
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
                url=self.start_urls[0],
                callback=self.parse_category_links,
                wait_time=10,
                cb_kwargs={'city': city},
                wait_until=EC.presence_of_element_located((By.XPATH, xpath.search)),
                dont_filter=True
            )

    def parse_category_links(self, response, **kwargs):
        driver: WebDriver = response.request.meta['driver']
        city: str = kwargs.get("city")
        urls: List = []
        for category in self.category_list:
            search_field: Selector = driver.find_element_by_xpath(xpath.search)
            search_field.send_keys(f'{city} {category}')
            time.sleep(3)
            search_field.send_keys(Keys.ENTER)
            time.sleep(3)
            scroll_down_load_companies(driver)
            fill_and_prepare_urls_of_companies(driver, city, category, urls)
            search_clear(driver)

        for url in urls:
            yield SplashRequest(
                url=url['href'],
                callback=self.parse_company_detail_page,
                cb_kwargs={'city': url['city'], 'category': url['category']}
            )

    def parse_company_detail_page(self, response, **kwargs):
        loader = ItemLoader(item=CompanyItem(), response=response)
        loader.add_value('category', kwargs.get('category'))
        loader.add_value('city', kwargs.get('city'))
        loader.add_xpath('name', xpath.company_name)
        loader.add_xpath('site', xpath.company_site)
        loader.add_xpath('email', xpath.company_email)
        loader.add_xpath('social', xpath.company_social)
        loader.add_xpath('phones', xpath.company_phones)
        company_url = f'{response.request.url}prices'

        yield Request(
            url=company_url,
            callback=self.parse_company_products,
            cb_kwargs={'loader': loader}
        )

    def parse_company_products(self, response, **kwargs):
        loader: ItemLoader = kwargs.get('loader')
        loader.add_xpath('products', xpath.company_products)
        yield loader.load_item()


def scroll_down_load_companies(driver: WebDriver) -> None:
    while True:
        companies: List[Selector] = driver.find_elements_by_xpath(xpath.company_element)
        scroll_to: Selector = companies[-1]
        end_el: List[Selector] = driver.find_elements_by_xpath(xpath.end_scroll)
        if not end_el and len(companies) < 20:
            driver.execute_script("arguments[0].scrollIntoView();", scroll_to)
            time.sleep(1)
        else:
            driver.execute_script("arguments[0].scrollIntoView();", scroll_to)
            time.sleep(1)
            break


def fill_and_prepare_urls_of_companies(driver: WebDriver, city: str, category: str, urls: List) -> None:
    urls_xpath: List[Selector] = driver.find_elements_by_xpath(xpath.link_company)
    time.sleep(1)
    for url in urls_xpath:
        logger.info(f"City:{city} Category:{category}")
        urls.append({'href': url.get_attribute("href"), 'city': city, 'category': category})


def search_clear(driver: WebDriver) -> None:
    try:
        search_clear: Selector = driver.find_element_by_xpath(xpath.search_clear)
        search_clear.click()
        time.sleep(3)
    except NoSuchElementException:
        pass

