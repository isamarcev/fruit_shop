# Generated by Django 4.1.4 on 2022-12-20 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fruitshop', '0005_alter_transaction_sum'),
    ]

    operations = [
        migrations.AddField(
            model_name='declaration',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
