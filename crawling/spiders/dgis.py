import scrapy

import time

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.firefox.webelement import FirefoxWebElement

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class DGisSpider(scrapy.Spider):
    name = 'dgis'
    allowed_domains = ['2gis.ru']
    start_urls = ['https://2gis.ru/']
    category_urls = []

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=10,
                wait_until=EC.element_to_be_clickable((By.XPATH, '//input[@type="text"]'))
            )

    def parse(self, response, **kwargs):
        webdriver: WebDriver = response.request.meta['driver']

        self.set_parse_city(webdriver=webdriver, city='Москва')
        self.set_parse_rubric(webdriver=webdriver, target_rubric='Пром. товары', target_sub_rubric='Металлы')

        categories = webdriver.find_elements_by_xpath('//div[contains(@class, "_13w22bi")]/a')
        for category in categories:
            self.category_urls.append(category.get_attribute('href'))

        for url in self.category_urls:
            return SeleniumRequest(url=url, callback=self.parse_category, wait_time=10)


    def parse_category(self, response, **kwargs):
        webdriver: WebDriver = response.request.meta['driver']
        companies =  webdriver.find_elements_by_xpath('//div[contains(@class, "awwm2v")]/div')
        for company in companies:
            self.parse_company(webdriver=webdriver, company=company)
            time.sleep(3)

    def parse_company(self, webdriver: WebDriver, company: FirefoxWebElement):
        company.click()
        company_card = webdriver.find_element_by_xpath('//div[contains(@class, "_18lzknl")]')
        company_name = company_card.find_element_by_xpath('//h1').text
        self.logger.info(company_name)

    def set_parse_city(self, webdriver: WebDriver, city: str):
        search_field = webdriver.find_element_by_xpath('//input[@type="text"]')
        time.sleep(3)
        search_field.send_keys(city)
        search_field.send_keys(Keys.ENTER)
        time.sleep(3)
        search_result_btn = webdriver.find_element_by_xpath(f'//div[contains(@class, "_y3rccd")]//span[contains(text(), "{city}")][1]')
        search_result_btn.click()
        time.sleep(3)

    def set_parse_rubric(self, webdriver: WebDriver, target_rubric: str, target_sub_rubric: str):
        all_rubrics_btn = webdriver.find_element_by_xpath('//div/a/span[contains(text(), "Рубрики")]')
        all_rubrics_btn.click()
        time.sleep(3)
        target_rubric_btn = webdriver.find_element_by_xpath(f'//div/a/span[contains(text(), "{target_rubric}")]')
        target_rubric_btn.click()
        time.sleep(3)
        sub_target_btn = webdriver.find_element_by_xpath(f'//div/a/span[contains(text(), "{target_sub_rubric}")]')
        sub_target_btn.click()
        time.sleep(3)