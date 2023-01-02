from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import (
    Supplier,
    JobRole,
    PartNo,
    Product,
    Warehouse,
    Brand, 
    Unit,
    InboundHistory,
    OutboundHistory
    )
from core.models import User
from .serializers import (
    SupplierSerializer,
    UserSerializer, 
    JobRoleSerializer,
    PartNoSerializer,
    ProductSerializer,
    WarehouseSerializer,
    BrandSerializer,
    UnitSerializer,
    SupplierSerializer,
    InboundHistorySerializer,
    OutboundHistorySerializer
)

# @permission_classes([IsAuthenticated])
class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# @permission_classes([IsAuthenticated])
class SupplierView(viewsets.ModelViewSet):
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer

# @permission_classes([IsAuthenticated])
class JobRoleView(viewsets.ModelViewSet):
    queryset = JobRole.objects.filter(is_active=True)
    serializer_class = JobRoleSerializer

# @permission_classes([IsAuthenticated])
class PartNoView(viewsets.ModelViewSet):
    queryset = PartNo.objects.filter(is_active=True)
    serializer_class = PartNoSerializer

# @permission_classes([IsAuthenticated])
class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# @permission_classes([IsAuthenticated])
class OutboundHistoryView(viewsets.ModelViewSet):
    queryset = InboundHistory.objects.all()
    serializer_class = InboundHistorySerializer

class TraInboundHistoryView(viewsets.ModelViewSet):
    queryset = OutboundHistory.objects.all()
    serializer_class = OutboundHistorySerializer

# @permission_classes([IsAuthenticated])
class WarehouseView(viewsets.ModelViewSet):
    queryset = Warehouse.objects.filter(is_active=True)
    serializer_class = WarehouseSerializer

# @permission_classes([IsAuthenticated])
class BrandView(viewsets.ModelViewSet):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer

# @permission_classes([IsAuthenticated])
class UnitView(viewsets.ModelViewSet):
    queryset = Unit.objects.filter(is_active=True)
    serializer_class = UnitSerializer

