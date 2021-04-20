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
