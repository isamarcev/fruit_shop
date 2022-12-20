from django.contrib import admin

from fruitshop.models import Product, PersonalAccount, Transaction, Declaration


# Register your models here.
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(PersonalAccount)
admin.site.register(Declaration)
