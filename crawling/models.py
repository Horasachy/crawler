from django.db import models


class Company(models.Model):
    name = models.CharField(
        max_length=300,
        verbose_name='Название компании'
    )
    kind = models.CharField(
        max_length=300,
        verbose_name='Вид деятельности'
    )

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


class City(models.Model):
    name = models.CharField(
        max_length=300,
        verbose_name='Название города'
    )
    slug = models.SlugField(
        max_length=300,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
