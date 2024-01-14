from django.contrib import admin
from .models import Product
# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name','link')
    list_display_links = ('id','name')
    search_fields = ('name',)


admin.site.register(Product, ProductAdmin)