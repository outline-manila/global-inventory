from rest_framework import generics
from rest_framework.decorators import api_view
from ..models import Warehouse
from ..serializers import WarehouseSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response

class WarehouseDetailAPIView(generics.RetrieveAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    lookup_field = 'pk'

warehouse_detail_view = WarehouseDetailAPIView.as_view()

class WarehouseListAPIView(generics.RetrieveAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

warehouse_list_view = WarehouseListAPIView.as_view()

class WarehouseCreateAPIView(generics.CreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

warehouse_create_view = WarehouseCreateAPIView.as_view()

class WarehouseUpdateAPIView(generics.UpdateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    lookup_field = 'pk'

warehouse_update_view = WarehouseUpdateAPIView.as_view()

@api_view(['POST'])
def warehouse_search_view(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if not body: return

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize')
    sort_by = body.get('sortBy') or '-updated_at'
    filter_by = body.get('filterBy')
    filter_id = body.get('filterById')
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        queryset = Warehouse.objects.filter(filter_dict).all().order_by(sort_by).values()

    else:
        queryset = Warehouse.objects.filter().all().order_by(sort_by).values()

    data = WarehouseSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['total'] = p.count
    result['numPages'] = p.num_pages
    result['metadata'] = p.page(current_page).object_list

    return Response(result)
