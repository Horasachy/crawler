from django.contrib import admin

from .models import Company, City


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass
