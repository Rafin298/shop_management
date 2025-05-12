from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView  # <- import the APIView here
from .views import RegisterView, CategoryViewSet, ProductViewSet, OrderViewSet

router = DefaultRouter()
router.register('auth/register', RegisterView, basename='register')
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    # router-registered viewsets
    path('', include(router.urls)),

    # explicit JWT endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]