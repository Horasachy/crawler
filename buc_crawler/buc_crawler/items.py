from scrapy import Item,Field


class CompanyItem(Item):
    category = Field()
    city = Field()
    name = Field()
    email = Field()
    site = Field()
    social = Field()
    phones = Field()
    products = Field()

class CityItem(Item):
    name = Field()


class RubricItem(Item):
    name = Field()
    url = Field()


class CompanyItem(Item):
    city = Field()
    rubric = Field()
    sub_rubric = Field()
    category = Field()
    url = Field()
    name = Field()
    kind = Field()
    tel = Field()
    email = Field()
    website = Field()
    networks = Field()
