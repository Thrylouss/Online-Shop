# Generated by Django 4.2.19 on 2025-02-15 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OnlineShopApp', '0005_alter_category_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='description',
        ),
        migrations.RemoveField(
            model_name='news',
            name='title',
        ),
    ]
