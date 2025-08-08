from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'login', LoginViewSet, basename='login')

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .apis.transaction import TransactionViewSet

urlpatterns = [
    # JWT endpoints
    path('auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('predict/', TransactionViewSet.as_view({'post': 'create', 'get': 'list'}), name='predict'),
    path('predict/file/', TransactionViewSet.as_view({'post': 'upload_file'}), name='predict-file'),
    path('predict/<int:pk>/', TransactionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='predict-detail'),

    path('frauds/', TransactionViewSet.as_view({'get': 'frauds'}), name='fraud'),
]