import json

from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q, F

from ..models import Product
from ..serializers import ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'part'

product_detail_view = ProductDetailAPIView.as_view()

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(~Q(brand='NaN')).all()
    serializer_class = ProductSerializer
    q = Product.objects.filter(part='This is a Simulation').values('remaining_stock').first()

product_list_view = ProductListAPIView.as_view()

class ProductUpdateAPIView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        product_name = body.get('product')
        request.data.update({'updated_at': timezone.now()})

        super(ProductUpdateAPIView, self).update(request, *args, **kwargs) 
        return Response({"message": f"Product {product_name} successfully updated"})


product_update_view = ProductUpdateAPIView.as_view()

@api_view(['POST'])
def update_product_stock(request, *args, **kwargs):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    invoice_date = body.get('invoice_date')
    supplier = body.get('supplier')
    value = body.get('value')
    part = body.get('part')
    queryset = Product.objects.filter(part=part)

    if not queryset: return Response({'message': 'part not found'})

    queryset.update(remaining_stock=F('remaining_stock') + value)

    return Response({'message': f'Remaining stocks increased by {value}'})


@api_view(['POST'])
def outbound_product(request, *args, **kwargs):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    value = body.get('value')
    part = body.get('part')
    queryset = Product.objects.filter(part=part)

    if not queryset: return Response({'message': 'part not found'})

    remaining_stocks = Product.objects.filter(part=part).values('remaining_stock').first()['remaining_stock']
    if remaining_stocks < value: return Response({'message': 'value larger than stocks'})

    queryset.update(remaining_stock=F('remaining_stock') - value)
    return Response({'message': f'Remaining stock decreased by {value}'})

@api_view(['POST'])
def product_search_view(request, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'
    filter_by = body.get('filterBy')
    filter_id = body.get('filterById')
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        queryset = Product.objects.filter(filter_dict, ~Q(brand='NaN')).all().order_by(sort_by)

    else:
        queryset = Product.objects.filter().all().order_by(sort_by)

    data = ProductSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}

    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)
