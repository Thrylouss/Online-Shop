# Generated by Django 4.2.19 on 2025-02-17 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OnlineShopApp', '0007_product_subcategory_alter_product_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='subcategory',
        ),
    ]
