from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth.password_validation import validate_password
from .models import *
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError


class CustomUserSerializer(UserCreateSerializer):
    # Делаем поле password необязательным
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ("id", "username", "full_name", "email", "town", "district", "password")

    def validate(self, attrs):
        password = attrs.get("password")
        if not password:
            # Если пароль не указан или пустой, убираем его из данных и пропускаем валидацию пароля
            attrs.pop("password", None)
            return attrs
        # Если пароль присутствует, выполняем стандартную валидацию
        user = CustomUser(**attrs)
        try:
            validate_password(password, user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        # Переопределяем метод обновления, чтобы не пытаться валидировать отсутствующий пароль
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance



# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImage
#         fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    # images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user_phone = serializers.ReadOnlyField(source='user.username')
    items = OrderItemSerializer(source='order_items', many=True, read_only=True)  # Используем related_name

    class Meta:
        model = Order
        fields = '__all__'


class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True  # Позволяет отправлять product_id, но не отображать в ответе
    )

    class Meta:
        model = BasketItem
        fields = ['id', 'user', 'product', 'product_id', 'amount', 'created_at', 'updated_at']
        read_only_fields = ['user', 'product', 'created_at', 'updated_at']