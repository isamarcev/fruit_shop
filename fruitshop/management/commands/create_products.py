from django.core.management import BaseCommand
from fruitshop import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('PRODUCT CREATING')
        if not models.Product.objects.all().exists():
            models.Product.objects.bulk_create([
                models.Product(name="Ананасы", balance=300),
                models.Product(name="Яблоки", balance=300),
                models.Product(name="Бананы", balance=300),
                models.Product(name="Апельсины", balance=300),
                models.Product(name="Абрикосы", balance=300),
                models.Product(name="Киви", balance=300),
            ])
        else:
            self.stdout.write("Products Already created")
