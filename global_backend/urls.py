from django.urls import path, include
from .views import MyTokenObtainPairView
from product import views as product_views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
# from core import views as core_views
from core.api.create_user import post_create_user


urlpatterns = [
    path('core/create/', post_create_user),
    path('api/', include('core.urls') ),
    # path('api/', include(router.urls)),
    path('api/', include('product.urls') ),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]