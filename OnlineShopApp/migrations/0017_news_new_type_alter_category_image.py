# Generated by Django 4.2.19 on 2025-04-24 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OnlineShopApp', '0016_category_mobile_image_productimage_mobile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='new_type',
            field=models.CharField(choices=[('first', 'first'), ('second', 'second')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='category_images/'),
        ),
    ]
