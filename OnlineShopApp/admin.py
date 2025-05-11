from django.contrib import admin
from .models import *
from django import forms
from django.db.models import Q

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    # Перенаправляем выбор подкатегории
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # Если категория существует, фильтруем подкатегории
        if 'subcategory' in self.fields:
            category = self.instance.subcategory and self.instance.subcategory or None
            self.fields['subcategory'].queryset = Category.objects.filter(subcategory=category)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register([News, BasketItem, CustomUser, Order, OrderItem, PhoneVerificationCode])
