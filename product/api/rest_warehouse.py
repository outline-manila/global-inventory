from rest_framework import generics, status
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

class WarehouseListAPIView(generics.ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

warehouse_list_view = WarehouseListAPIView.as_view()

class WarehouseCreateAPIView(generics.CreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = WarehouseSerializer(data=body) 

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Warehouse {body.get('warehouse')} successfully created"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

warehouse_create_view = WarehouseCreateAPIView.as_view()

class WarehouseUpdateAPIView(generics.UpdateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    lookup_field = 'pk'


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        serializer = WarehouseSerializer(data=body) 

        warehouse_name = body.get('warehouse')

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Warehouse {warehouse_name} successfully updated"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

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
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)
