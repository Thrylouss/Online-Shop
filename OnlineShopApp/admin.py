from django.contrib import admin
from .models import *
from django import forms
from django.db.models import Q

admin.site.register([Category, SubCategory, Product, News, BasketItem, CustomUser, Order, OrderItem, PhoneVerificationCode])


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['default_language', 'updated_at']