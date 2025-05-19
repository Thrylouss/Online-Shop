from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth.password_validation import validate_password
from .models import *
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError


class LangAwareSerializer(serializers.ModelSerializer):
    def get_lang(self):
        request = self.context.get('request')
        return request.query_params.get('lang') if request else None

    def is_ru(self):
        return self.get_lang() == 'ru'


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


class ProductSerializer(LangAwareSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    characteristics = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'characteristics',
            'price', 'discount', 'quantity', 'product_code',
            'status', 'image1', 'image2', 'image3', 'image4', 'image5',
            'mobile_image1', 'mobile_image2', 'mobile_image3', 'mobile_image4', 'mobile_image5',
            'slug', 'created_at', 'updated_at', 'subcategory'
        ]

    def get_name(self, obj):
        return obj.name_ru if self.is_ru() and obj.name_ru else obj.name

    def get_description(self, obj):
        return obj.description_ru if self.is_ru() and obj.description_ru else obj.description

    def get_characteristics(self, obj):
        return obj.characteristics_ru if self.is_ru() and obj.characteristics_ru else obj.characteristics

    def get_status(self, obj):
        return obj.status_ru if self.is_ru() and obj.status_ru else obj.status


class CategorySerializer(LangAwareSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    mobile_image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'mobile_image',
            'created_at', 'updated_at'
        ]

    def get_name(self, obj):
        print("Language:", self.get_lang())
        return obj.name_ru if self.is_ru() and obj.name_ru else obj.name

    def get_description(self, obj):
        description = obj.description_ru if self.is_ru() and obj.description_ru else obj.description
        return description

    def get_image(self, obj):
        image = obj.image_ru if self.is_ru() and obj.image_ru else obj.image
        return image.url if image else None

    def get_mobile_image(self, obj):
        image = obj.mobile_image_ru if self.is_ru() and obj.mobile_image_ru else obj.mobile_image
        return image.url if image else None


class SubCategorySerializer(LangAwareSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description', 'category', 'created_at', 'updated_at']

    def get_name(self, obj):
        return obj.name_ru if self.is_ru() and obj.name_ru else obj.name

    def get_description(self, obj):
        return obj.description_ru if self.is_ru() and obj.description_ru else obj.description


class NewsSerializer(LangAwareSerializer):
    image = serializers.SerializerMethodField()
    mobile_image = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = ['id', 'image', 'mobile_image', 'new_type', 'created_at', 'updated_at']

    def get_image(self, obj):
        image = obj.image_ru if self.is_ru() and obj.image_ru else obj.image
        return image.url if image else None

    def get_mobile_image(self, obj):
        image = obj.mobile_image_ru if self.is_ru() and obj.mobile_image_ru else obj.mobile_image
        return image.url if image else None



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
        write_only=True
    )

    class Meta:
        model = BasketItem
        fields = ['id', 'product', 'product_id', 'amount', 'created_at', 'updated_at']
        read_only_fields = ['product', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user

        product = validated_data['product']
        amount = validated_data.get('amount', 1)

        instance, created = BasketItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'amount': amount}
        )
        if not created:
            instance.amount += amount
            instance.save()

        return instance


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = '__all__'