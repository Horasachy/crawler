class YandexMapPath(object):
    def __init__(self):
        self.search = '//input[@type="search"]'
        self.search_clear = '//div[contains(@class, "small-search-form-view__icon") and contains(@class, "_type_close")]'
        self.company_element = '//div[@data-chunk="search-snippet"]'
        self.end_scroll = '//div[@class="search-list-view__add-business"]'
        self.link_company = '//a[@class="search-snippet-view__link-overlay"]'

        self.company_name = '//h1[contains(@class, "orgpage-header-view__header")]/text()'
        self.company_email = None
        self.company_site = '//span[contains(@class, "business-urls-view__text")]/text()'
        self.company_social = '//div[contains(@class,"business-contacts-view__social-button")]//a/@href'
        self.company_phones = '//div[contains(@class, "orgpage-phones-view__phone-number")]//text()'
        self.company_products = '//div[contains(@class, "related-item-list-view__title")]//text()'