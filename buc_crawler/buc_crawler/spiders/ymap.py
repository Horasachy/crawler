import time
from abc import ABC
import scrapy
from scrapy.loader import ItemLoader
from buc_crawler.xpaths import YandexMapPath
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from buc_crawler.items import CompanyItem
from selenium.webdriver.support.wait import WebDriverWait


class YmapSpider(scrapy.Spider, ABC):
    name = 'ymap'
    allowed_domains = ['yandex.ru']
    start_urls = ['https://yandex.ru/maps/']
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

    def __init__(self, *args, **kwargs):
        super(YmapSpider, self).__init__(*args, **kwargs)
        self.path = YandexMapPath()

    def start_requests(self):
        # for city in self.cities:
        yield SeleniumRequest(
            url=self.start_urls[0],
            callback=self.parse_links,
            wait_time=10,
            wait_until=EC.presence_of_element_located((By.XPATH, self.path.search)),
            cb_kwargs={'city': self.cities[0]},
        )

    def parse_links(self, response, **kwargs):
        driver: WebDriver = response.request.meta['driver']
        search_field = driver.find_element_by_xpath(self.path.search)
        category = self.category_list[0]
        search_field.send_keys(f'{kwargs.get("city")} {category}')
        time.sleep(3)
        search_field.send_keys(Keys.ENTER)
        time.sleep(3)
        self.scroll_down_load_companies(driver)
        time.sleep(3)
        self.get_companies_links(driver, category)
        for link in self.links:
            yield SeleniumRequest(
                url=link['url'],
                callback=self.parse_company_info,
                cb_kwargs={'city': self.cities[0], 'category': category},
            )

    def parse_company_info(self, response, **kwargs):
        loader = ItemLoader(item=CompanyItem(), response=response)
        loader.add_value('category', kwargs.get('category'))
        loader.add_value('city', kwargs.get('city'))
        loader.add_xpath('name', self.path.company_name)
        loader.add_xpath('site', self.path.company_site)
        loader.add_xpath('email', self.path.company_email)
        loader.add_xpath('social', self.path.company_social)
        loader.add_xpath('phones', self.path.company_phones)

        company_url = f'{response.request.url}prices'
        yield scrapy.Request(
            url=company_url,
            callback=self.parse_company_products,
            cb_kwargs={'loader': loader}
        )

    def parse_company_products(self, response, **kwargs):
        loader = kwargs.get('loader')
        loader.add_xpath('products', self.path.company_products)
        return loader.load_item()

    def scroll_down_load_companies(self, driver):
        while True:
            scroll_to = driver.find_elements_by_xpath(self.path.company_element)[-1]
            end_el = driver.find_elements_by_xpath(self.path.end_scroll)
            if not end_el:
                driver.execute_script("arguments[0].scrollIntoView();", scroll_to)
                time.sleep(1)
            else:
                driver.execute_script("arguments[0].scrollIntoView();", scroll_to)
                time.sleep(1)
                break

    def get_companies_links(self, driver, category) -> None:
        time.sleep(1)
        links = driver.find_elements_by_xpath(self.path.link_company)
        for elem in links:
            self.links.append({'category': category, 'url': elem.get_attribute("href")})
            print(self.links)
        driver.find_element_by_xpath(self.path.search_clear).click()
        time.sleep(1)
