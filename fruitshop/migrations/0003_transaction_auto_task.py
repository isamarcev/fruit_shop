# Generated by Django 4.1.4 on 2022-12-20 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fruitshop', '0002_alter_personalaccount_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='auto_task',
            field=models.BooleanField(default=False),
        ),
    ]
