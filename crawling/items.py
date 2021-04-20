from scrapy_djangoitem import DjangoItem

from .models import Company


class CompanyItem(DjangoItem):
    django_model =  Company
