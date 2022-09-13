from django.urls import path, include
from .views import MyTokenObtainPairView
from product import views as product_views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
# from core import views as core_views
from core.api.create_user import post_create_user

router = routers.DefaultRouter()
router.register('users', product_views.UserView)
router.register('brand', product_views.BrandView)
router.register('supplier', product_views.SupplierView)
router.register('job_role', product_views.JobRoleView)
router.register('part_no', product_views.PartNoView)
router.register('transaction_history', product_views.TransactionHistoryView)
router.register('product', product_views.ProductView)
router.register('unit', product_views.UnitView)
router.register('warehouse', product_views.WarehouseView)

urlpatterns = [
    
    path('core/create/', post_create_user),
    path('api/', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]