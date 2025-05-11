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

    @action(detail=False, methods=['get'], url_path='subcategory/(?P<category_id>[^/.]+)')
    def get_subcategories(self, request, category_id=None):
        category = Category.objects.get(pk=category_id)
        subcategories = category.category_set.all()
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)


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
    queryset = BasketItem.objects.all()
    serializer_class = BasketItemSerializer
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи

    def create(self, request, *args, **kwargs):
        print("Authenticated user:", request.user)  # Debugging
        print("Request data:", request.data)

        if request.user.is_anonymous:
            return Response({"error": "Пользователь не аутентифицирован"}, status=status.HTTP_401_UNAUTHORIZED)

        # Получаем `product_id`
        product_id = request.data.get('product_id')
        amount = int(request.data.get('amount', 1))

        if not product_id:
            return Response({"error": "Не указан ID товара"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, существует ли продукт
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, есть ли уже товар в корзине
        basket_item, created = BasketItem.objects.get_or_create(
            user=request.user, product=product
        )

        if not created:
            basket_item.amount += amount
            basket_item.save()

        serializer = self.get_serializer(basket_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-basket')
    def get_basket_items(self, request):
        basket_items = BasketItem.objects.filter(user=request.user)
        serializer = self.get_serializer(basket_items, many=True)
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