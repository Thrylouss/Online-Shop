# Generated by Django 4.2.19 on 2025-02-17 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OnlineShopApp', '0009_product_subcategory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
    ]
