import django_filters
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    # Поиск по частичному совпадению имени (без учета регистра)
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    # Фильтрация по диапазону цен
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    # Фильтр по категории (по ID)
    subcategory = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), field_name='subcategory')

    class Meta:
        model = Product
        fields = ['name', 'subcategory', 'status', 'min_price', 'max_price']
