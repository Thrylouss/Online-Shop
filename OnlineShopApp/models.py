import random
from django.db.models import Max
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.utils.timezone import now
from datetime import timedelta


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, town=None, district=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, town=town, district=district, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Устанавливаем недоступный пароль

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password=password, **extra_fields)


class CustomUser(AbstractUser):
    town = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    objects = CustomUserManager()


class News(models.Model):
    image = models.ImageField(upload_to='news_images/')
    mobile_image = models.ImageField(upload_to='news_images/')

    image_ru = models.ImageField(upload_to='news_images/')
    mobile_image_ru = models.ImageField(upload_to='news_images/')

    NEWS_CATEGORY_CHOICES = [
        ("first", "first"),
        ("second", "second")
    ]
    new_type = models.CharField(max_length=255, choices=NEWS_CATEGORY_CHOICES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    description_ru = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    mobile_image = models.ImageField(upload_to='category_images/mobile/', null=True, blank=True)  # New mobile image field

    image_ru = models.ImageField(upload_to='category_images/')
    mobile_image_ru = models.ImageField(upload_to='category_images/')

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    name_ru = models.CharField(max_length=100)
    description_ru = models.CharField(max_length=100, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.JSONField()
    characteristics = models.JSONField()

    name_ru = models.CharField(max_length=100)
    description_ru = models.JSONField()
    characteristics_ru = models.JSONField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    product_code = models.PositiveIntegerField(unique=True, blank=True, null=True)
    status_type = [
        ('Mahsus taklif', 'mahsus_taklif'),
        ('Yangilik', 'yangilik'),
    ]
    status = models.CharField(max_length=20, choices=status_type, default='yangilik', blank=True, null=True)

    status_type_ru = [
        ('Специальное', 'special'),
        ('Новое', 'new'),
    ]
    status_ru = models.CharField(max_length=20, choices=status_type_ru, default='new', blank=True, null=True)

    image1 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image4 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image5 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    mobile_image1 = models.ImageField(upload_to='mobile_images/', null=True, blank=True)
    mobile_image2 = models.ImageField(upload_to='mobile_images/', null=True, blank=True)
    mobile_image3 = models.ImageField(upload_to='mobile_images/', null=True, blank=True)
    mobile_image4 = models.ImageField(upload_to='mobile_images/', null=True, blank=True)
    mobile_image5 = models.ImageField(upload_to='mobile_images/', null=True, blank=True)
    
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    # category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='subproducts')

    def save(self, *args, **kwargs):
        if not self.product_code:
            # Находим максимальное значение product_code среди существующих продуктов
            max_code = Product.objects.aggregate(Max('product_code'))['product_code__max']
            self.product_code = (max_code or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# class ProductImage(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
#     image = models.ImageField(upload_to='product_images/')
#     mobile_image = models.ImageField(upload_to='product_images/mobile/', null=True, blank=True)  # New mobile image field
    

#     def __str__(self):
#         return f"Image for {self.product.name}"


class BasketItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']  # Сортировать по дате создания по возрастанию

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.PositiveIntegerField(default=0)

    STATUS_CHOICES = (
        ('Bekor qilindi', 'Bekor qilindi'),
        ('Jarayonda', 'Jarayonda'),
        ('Yetkazib berildi', 'Yetkazib berildi'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Jarayonda', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    @property
    def items(self):
        """Возвращает все OrderItem, связанные с заказом"""
        return self.order_items.all()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')  # Добавили related_name
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.amount} x {self.product.name} in Order #{self.order.id}"


class PhoneVerificationCode(models.Model):
    username = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def generate_code(self):
        """Генерирует 6-значный код"""
        self.code = str(random.randint(100000, 999999))
        self.is_used = False
        self.created_at = now()  # Обновляем дату создания
        self.save()

    def verify_code(self, input_code):
        """Проверяет код и помечает его использованным"""
        if self.is_valid() and self.code == input_code:
            self.is_used = True
            self.save()
            return True
        return False

    def is_valid(self):
        """Код действителен 5 минут и не использован"""
        if self.is_used:
            return False  # Код уже использован

        time_diff = now() - self.created_at
        return time_diff.total_seconds() <= 300  # 300 секунд = 5 минут

