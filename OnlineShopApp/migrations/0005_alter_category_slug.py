# Generated by Django 4.2.19 on 2025-02-15 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OnlineShopApp', '0004_rename_quantity_basketitem_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
