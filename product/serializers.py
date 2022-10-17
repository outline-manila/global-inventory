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
        fields = ('id', 'job_role', 'description', 'is_active','updated_at', 'created_at', 'end_date')

class PartNoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PartNo
        fields = ('id', 'part_no', 'description', 'is_active','updated_at', 'created_at', 'end_date')

class UnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'unit', 'description', 'is_active','updated_at', 'created_at', 'end_date')

class SupplierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'supplier', 'description', 'is_active','updated_at', 'created_at', 'end_date')
    
class BrandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'brand', 'description', 'is_active','updated_at', 'created_at', 'end_date')



class WarehouseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('id', 'warehouse_no', 'description', 'is_active','updated_at', 'created_at', 'end_date')
        

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

