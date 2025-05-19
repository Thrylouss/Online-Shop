from django.urls import path, re_path
from django.urls import include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from . import views
from .views import SendCodeView, VerifyCodeView

schema_view = get_schema_view(
    openapi.Info(
        title="Project API",
        default_version="v1",
        description="Example API",
    ),
    public=True,
    permission_classes=([permissions.AllowAny,]),
)


router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'news', views.NewsViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'basket', views.BasketItemViewSet)
router.register(r'orders_item', views.OrderItemViewSet)
router.register(r'subcategories', views.SubCategoryViewSet)
router.register(r'site_settings', views.SiteSettingsView)
# router.register(r'product_images', views.ProductImageViewSet)


urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),

    path('', include(router.urls)),

    path('auth/', include('djoser.urls')),  # Базовые маршруты для работы с пользователями
    path('auth/', include('djoser.urls.authtoken')),  # Подключаем маршруты для токенов

    path('auth/send-code/', SendCodeView.as_view(), name='send-code'),
    path('auth/verify-code/', VerifyCodeView.as_view(), name='verify-code'),

]
