from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import ProductFilter
from .models import *
from .serializers import *  # исправленный импорт
from rest_framework.authtoken.models import Token


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    # Подключаем фильтрацию
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Указываем класс фильтра
    filterset_class = ProductFilter

    # Поля для поиска (поиск по name и description)
    search_fields = ['name', 'description']

    # Поля для сортировки (например, по цене и дате создания)
    ordering_fields = ['price', 'created_at']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def get_subcategories(self, request, pk=None):
        subcategories = SubCategory.objects.filter(category_id=pk)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data)


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [AllowAny]


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]


# class ProductImageViewSet(viewsets.ModelViewSet):
#     queryset = ProductImage.objects.all()
#     serializer_class = ProductImageSerializer
#     permission_classes = [AllowAny]

#     @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[^/.]+)')
#     def get_product_images(self, request, product_id=None):
#         product_images = ProductImage.objects.filter(product_id=product_id)
#         serializer = self.get_serializer(product_images, many=True)
#         return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)  # Показываем только заказы текущего пользователя

    @action(detail=False, methods=['post'], url_path='create')
    def create_order(self, request):
        user = request.user
        basket_items = BasketItem.objects.filter(user=user)
        if not basket_items.exists():
            return Response({"error": "Ваша корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        for item in basket_items:
            price = float(item.product.price)
            discount = float(item.product.discount)
            final_price = price * (1 - discount / 100) if discount != 0 else price
            total_price += final_price * item.amount

        try:
            with transaction.atomic():
                order = Order.objects.create(user=user, total_price=int(total_price))
                for item in basket_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        amount=item.amount
                    )
                basket_items.delete()
            return Response({"message": "Заказ успешно создан", "order_id": order.id},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class BasketItemViewSet(viewsets.ModelViewSet):
    queryset = BasketItem.objects.select_related('product').all()
    serializer_class = BasketItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BasketItem.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-basket')
    def get_basket_items(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SendCodeView(APIView):
    """
    Эндпоинт для генерации кода верификации.
    Вызывается при вводе (или передаче) номера телефона (username).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")  # Это ваш телефон
        if not username:
            return Response({"error": "Поле 'username' (номер телефона) обязательно"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Ищем или создаём запись для этого номера телефона
        verification, created = PhoneVerificationCode.objects.get_or_create(username=username)

        # Генерируем новый код
        verification.generate_code()

        # Здесь можно вызвать логику отправки кода (SMS, Telegram, email — не важно).
        # Для теста просто вернём его в ответе.
        return Response(
            {
                "message": f"Код для {username} успешно сгенерирован.",
                "code": verification.code  # Для отладки
            },
            status=status.HTTP_200_OK
        )


class VerifyCodeView(APIView):
    """
    Эндпоинт для проверки кода и автоматического входа (логина) с JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        code = request.data.get("code")
        full_name = request.data.get("full_name")

        if not username or not code:
            return Response({"error": "Поле 'username' и 'code' обязательны"},
                            status=status.HTTP_400_BAD_REQUEST)


        # Получаем запись, или 404
        verification = get_object_or_404(PhoneVerificationCode, username=username)

        if not verification.is_valid():
            return Response({"error": "Код истёк или уже использован"},
                            status=status.HTTP_400_BAD_REQUEST)

        if verification.verify_code(code):
            # Создаём пользователя, если его нет
            user, created = CustomUser.objects.get_or_create(username=username)

            if full_name and user.full_name != full_name:
                user.full_name = full_name
                user.save(update_fields=['full_name'])

            # Генерируем JWT токены
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "message": "Телефон успешно подтверждён!",
                "user_created": created,
                "username": username,
                "access_token": access_token,  # Основной токен
                "refresh_token": str(refresh)  # Токен для обновления
            }, status=status.HTTP_200_OK)

        return Response({"error": "Неверный код или он уже использован!"},
                        status=status.HTTP_400_BAD_REQUEST)


class SiteSettingsView(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [AllowAny]
