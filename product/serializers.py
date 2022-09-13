from rest_framework import serializers
from .models import JobRole, PartNo, Unit, Supplier, Brand, Warehouse, Product, TransactionHistory
from core.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'uuid', 
            'email', 
            'employee_id', 
            'first_name', 
            'last_name', 
            'job_role', 
            'joined_on'
        )

class JobRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobRole
        fields = ('id', 'job_role', 'is_active','updated_at', 'created_at')

class PartNoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PartNo
        fields = ('id', 'part_no', 'is_active','updated_at', 'created_at')

class UnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'unit', 'is_active','updated_at', 'created_at')

class SupplierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'supplier', 'is_active','updated_at', 'created_at')
    
class BrandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'brand', 'is_active','updated_at', 'created_at')

class WarehouseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('id', 'warehouse_no', 'is_active','updated_at', 'created_at')
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'uuid',
            'warehouse_no',
            'part_no',
            'other_part_no',
            'brand',
            'remaining_stock',
            'unit',
            'supplier',
            'updated_at',
            'created_at'
        )

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = (
            'id',
            'uuid',
            'date',
            'invoice_no',
            'action',
            'description',
            'user_id',
            'warehouse_no',
            'product_id'
        )

