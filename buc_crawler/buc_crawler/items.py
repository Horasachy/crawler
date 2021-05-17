from scrapy import Item,Field


class CompanyItem(Item):
    category = Field()
    city = Field()
    name = Field()
    email = Field()
    site = Field()
    phones = Field()
    social = Field()

class CityItem(Item):
    name = Field()


class RubricItem(Item):
    name = Field()
    url = Field()


