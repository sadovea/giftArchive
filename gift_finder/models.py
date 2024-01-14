from django.db import models


#A model that is needed to save links to a category of a certain product and pass this link to the parser
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Назва товару')
    link = models.URLField(verbose_name='Посилання на товар')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
