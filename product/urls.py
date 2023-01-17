from product.api.rest_brand import BrandDetailAPIView
from django.urls import path, include

from .api import (
    rest_brand,
    rest_supplier,
    rest_warehouse,
    rest_unit,
    rest_part_no,
    rest_job_role,
    product,
    rest_employee
)


urlpatterns = [
    # brands
    path('brand/', rest_brand.brand_list_view,  name='brand_list'),
    path('brand/<int:pk>/', rest_brand.brand_detail_view,  name='brand-detail'),
    path('brand/create/', rest_brand.brand_create_view, name='brand_create'),
    path('brand/update/<int:pk>', rest_brand.brand_update_view, name='brand_update'),
    path('brand/search/', rest_brand.brand_search_view, name='brand_search'),
    path('brand/batch_delete/', rest_brand.brand_delete_apiview, name='brand_delete'),

    #suppliers
    path('supplier/', rest_supplier.supplier_list_view,  name='supplier_list'),
    path('supplier/<int:pk>/', rest_supplier.supplier_detail_view,  name='supplier_detail'),
    path('supplier/create/', rest_supplier.supplier_create_view, name='supplier_create'),
    path('supplier/update/<int:pk>', rest_supplier.supplier_update_view, name='supplier_update'),
    path('supplier/search/', rest_supplier.supplier_search_view, name='supplier_search'),
    path('supplier/batch_delete/', rest_supplier.supplier_delete_apiview, name='supplier_delete'),

    #warehouses
    path('warehouse/', rest_warehouse.warehouse_list_view,  name='warehouse_list'),
    path('warehouse/<int:pk>/', rest_warehouse.warehouse_detail_view,  name='warehouse_detail'),
    path('warehouse/create/', rest_warehouse.warehouse_create_view, name='warehouse_create'),
    path('warehouse/update/<int:pk>', rest_warehouse.warehouse_update_view, name='warehouse_update'),
    path('warehouse/search/', rest_warehouse.warehouse_search_view, name='warehouse_search'),
    path('warehouse/batch_delete/', rest_warehouse.warehouse_delete_apiview, name='warehouse_delete'),

    #units
    path('unit/', rest_unit.unit_list_view,  name='unit_list'),
    path('unit/<int:pk>/', rest_unit.unit_detail_view,  name='unit-detail'),
    path('unit/create/', rest_unit.unit_create_view, name='unit_create'),
    path('unit/update/<int:pk>', rest_unit.unit_update_view, name='unit_update'),
    path('unit/search/', rest_unit.unit_search_view, name='unit_search'),
    path('unit/batch_delete/', rest_unit.unit_delete_apiview, name='unit_delete'),

    #job role
    path('job_role/', rest_job_role.job_role_list_view,  name='job_role_list'),
    path('job_role/<int:pk>/', rest_job_role.job_role_detail_view,  name='job_role-detail'),
    path('job_role/create/', rest_job_role.job_role_create_view, name='job_role_create'),
    path('job_role/update/<int:pk>', rest_job_role.job_role_update_view, name='job_role_update'),
    path('job_role/search/', rest_job_role.job_role_search_view, name='job_role_search'),
    path('job_role/batch_delete/', rest_job_role.job_role_delete_apiview, name='job_role_delete'),

    #part number
    path('part/', rest_part_no.part_no_list_view,  name='part_no_list'),
    path('part/<int:pk>/', rest_part_no.part_no_detail_view,  name='part_no-detail'),
    path('part/create/', rest_part_no.part_no_create_view, name='part_no_create'),
    path('part/update/<int:pk>', rest_part_no.part_no_update_view, name='part_no_update'),
    path('part/search/', rest_part_no.part_no_search_view, name='part_no_search'),
    path('part/batch_delete/', rest_part_no.part_delete_apiview, name='part_no_delete'),

    # # user
    # path('user/', rest_user.user_list_view,  name='user_list'),
    # path('user/<int:pk>/', rest_user.user_detail_view,  name='user-detail'),
    # path('user/create/', rest_user.user_create_view, name='user_create'),
    # path('user/update/<int:pk>', rest_user.user_update_view, name='user_update'),
    # path('user/search/', rest_user.user_search_view, name='user_search'),

    #product
    path('inventory/', product.product_list_view,  name='product_list'),
    path('inventory/detail/<str:part>/', product.product_detail_view,  name='product_detail'),
    path('inventory/update_stock/', product.update_product_stock,  name='product_stock_update'),
    path('inventory/update/<int:pk>', product.product_update_view, name='product_update'),
    path('inventory/search/', product.product_search_view, name='product_search'),

    # employee
    path('employee/', rest_employee.employee_list_view,  name='employee_list'),
    path('employee/<int:pk>/', rest_employee.employee_detail_view,  name='employee-detail'),
    path('employee/create/', rest_employee.employee_create_view, name='employee_create'),
    path('employee/update/<int:pk>', rest_employee.employee_update_view, name='employee_update'),
    path('employee/search/', rest_employee.employee_search_view, name='employee_search'),
    path('employee/batch_delete/', rest_employee.employee_delete_apiview, name='employee_batch_delete'),

    # inbound history
    path('inbound_history/', product.inbound_history_list_view,  name='inbound_history_list'),
    path('inbound_history/<int:pk>/', product.inbound_history_detail_view,  name='inbound_history-detail'),
    path('inbound_history/create/', product.inbound_history_create_view, name='inbound_history_create'),
    path('inbound_history/update/<int:pk>', product.inbound_history_update_view, name='inbound_history_update'),
    path('inbound_history/search/', product.inbound_history_search_view, name='inbound_history_search'),
    path('inbound_history/batch_delete/', product.inbound_history_delete_apiview, name='inbound_history_batch_delete'),
]
