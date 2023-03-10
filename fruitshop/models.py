from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class PersonalAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="account")
    balance = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Банковский счет"


class Declaration(models.Model):
    account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE)
    file = models.FileField(upload_to="declaration/")
    date = models.DateTimeField(auto_now=True)


class Product(models.Model):
    name = models.CharField(max_length=30)
    balance = models.PositiveIntegerField(default=0)
    last_operation = models.ForeignKey('Transaction', on_delete=models.SET_NULL,
                                       blank=True,
                                       null=True,
                                       related_name='last_operation')


class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    sum = models.PositiveIntegerField()
    success = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE)
    auto_task = models.BooleanField(default=False)
    TYPE = (
        ("Покупка", "Покупка"),
        ("Продажа", "Продажа")
    )
    type = models.CharField(choices=TYPE, max_length=10)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.sum = self.count * self.price
        return super(Transaction, self).save()
