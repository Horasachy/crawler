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


class DGisMapPath(object):
    def __init__(self):
        self.search = '//input[contains(@class, "_xykhig")]'
        self.search_clear = '//button[@class="_1mit2xq"]'
        self.companies_urls = '//div[@class="_1h3cgic"]//a'
        self.accept_cookie = '//div[@class="_trvdea"]//button[@class="_1wadwrc"]'
        self.next_page_one = '//div[@class="_n5hmn94"][2]/*[name()="svg"]'
        self.next_page_two = '//div[@class="_n5hmn94"]/*[name()="svg"]'

        self.company_price = '//a[contains(@class, "_1nped2zk") and contains(text(), "Цены")]'
        self.company_name = '//span//span[@class="_oqoid"]/text()'
        self.company_email = '//div[@class="_49kxlr"]//div//a[contains(@target,"_blank") and contains(@class, "_1nped2zk")]/text()'
        self.company_site = '//div[@class="_49kxlr"]//a[contains(@class, "_pbcct4") and contains(@target, "_blank")]/text()'
        self.company_social = '//div[@class="_oisoenu"]//a/@href'
        self.company_phones = '//div[@class="_b0ke8"]//a[@class="_1nped2zk"]/@href'
        self.company_product_selector_one = '//div[@class="_8mqv20"]//div[1]'
        self.company_product_selector_two = '//article[@class="_gc1bca"]//div[@class="_o2i0na"]'
