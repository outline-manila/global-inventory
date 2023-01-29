from rest_framework import serializers
from .models import (
    InboundHistory,
    JobRole,
    PartNo,
    Unit,
    Supplier,
    Brand,
    Warehouse,
    Product,
    InboundHistory,
    Employee,
    OutboundHistory
)
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

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = (
            'id', 
            'uuid', 
            'email', 
            'employee_id', 
            'first_name', 
            'middle_name',
            'last_name', 
            'warehouse',
            'remarks',
            'start_date',
            'end_date',
            'job_role',
        )

class JobRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobRole
        fields = ('id', 'job_role', 'description', 'is_active','updated_at', 'created_at', 'start_date', 'end_date')

class PartNoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PartNo
        fields = ('id', 'part', 'brand', 'description', 'is_active','updated_at', 'created_at', 'start_date', 'end_date')

class UnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'unit', 'description', 'is_active','updated_at', 'created_at', 'start_date', 'end_date')

class SupplierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'supplier', 'description', 'is_active','updated_at', 'created_at', 'start_date', 'end_date')
    
class BrandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'brand', 'description', 'is_active','updated_at', 'created_at', 'start_date', 'end_date')



class WarehouseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('id', 'warehouse', 'description', 'is_active','updated_at', 'created_at', 'start_date', 'end_date')
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'uuid',
            'description',
            'warehouse',
            'part',
            'other_part',
            'brand',
            'remaining_stock',
            'unit',
            'supplier',
            'updated_at',
            'created_at'
        )

class UserSerializerTransaction(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 
            'last_name'
        )

class InboundHistorySerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.values('email'))
    user = UserSerializerTransaction()
    class Meta:
        model = InboundHistory
        fields = (
            'id',
            'uuid',
            'date',
            'invoice_no',
            'action',
            'description',
            'warehouse',
            'user'
        )

class OutboundHistorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset= User.objects.all())
    class Meta:
        model = OutboundHistory
        fields = (
            'id',
            'uuid',
            'date',
            'invoice_no',
            'action',
            'description',
            'user',
            'warehouse',
            'warehouse_to',
            'remarks',
        )

