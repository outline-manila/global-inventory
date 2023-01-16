import json

from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q, F

from ..models import Product, invoice_number, InboundHistory, OutboundHistory
from ..serializers import ProductSerializer, InboundHistorySerializer, OutboundHistorySerializer


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
    unit = body.get('unit')
    supplier = body.get('supplier')
    warehouse = body.get('warehouse')
    value = body.get('value')
    part = body.get('part')
    # filter_dict = {}

    # if unit is not None:
    #     filter_dict['unit'] = unit

    # if warehouse is not None:
    #     filter_dict['warehouse'] = warehouse

    # if supplier is not None:
    #     filter_dict['supplier'] = supplier

    queryset = Product.objects.filter(part=part)

    if not queryset: return Response({'message': 'part not found'})
    queryset.update(remaining_stock=F('remaining_stock') + value, supplier=supplier, warehouse=warehouse, unit=unit)

    return update_inbound_history(body)


    return Response({'message': f'Remaining stocks increased by {value}'})

def update_inbound_history(body):
    
    invoice_date = body.get('invoice_date')
    warehouse = body.get('warehouse')
    # part = body.get('part')
    action = 'TODO make action dynamic'
    product_id = 16
    user_id = 1
    data = {}
    data['product_id'] = product_id
    data['date']: invoice_date
    data['invoice_no'] = invoice_number()
    data['part'] = '2s224'
    data['warehouse'] = warehouse
    data['action'] = action
    data['user_id'] = user_id
    
    inbound_serializer = InboundHistorySerializer(data=data)

    if inbound_serializer.is_valid():
        inbound_serializer.save()
        return Response({"message": f"Created inbound history with Invoice Number {data['invoice_no']}"})

    error_dict = {error: InboundHistorySerializer.errors[error][0] for error in InboundHistorySerializer.errors}
    return Response(error_dict, status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def outbound_product(request, *args, **kwargs):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    value = body.get('value')
    part = body.get('part')
    queryset = Product.objects.filter(part=part)

    if not queryset: return Response({'message': 'part not found'}, status=status.HTTP_404_NOT_FOUND)

    remaining_stocks = Product.objects.filter(part=part).values('remaining_stock').first()['remaining_stock']
    if remaining_stocks < value: return Response({'message': 'value larger than stocks'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    queryset.update(remaining_stock=F('remaining_stock') - value)

    # invoice_no = invoice_number(OutboundHistory)

    return Response({'message': f'Remaining stock decreased by {value}'})

def update_outbound_history(body):
    invoice_date = body.get('invoice_date')
    warehouse = body.get('warehouse')
    # part = body.get('part')
    action = 'TODO make action dynamic'
    product_id = 16
    user_id = 1
    data = {}
    data['product_id'] = product_id
    data['date']: invoice_date
    data['invoice_no'] = invoice_number()
    data['part'] = '2s224'
    data['warehouse'] = warehouse
    data['action'] = action
    data['user_id'] = user_id
    
    outbound_serializer = OutboundHistorySerializer(data=data)

    if outbound_serializer.is_valid():
        outbound_serializer.save()
        return Response({"message": f"Outbound successfully created"})

    error_dict = {error: OutboundHistorySerializer.errors[error][0] for error in InboundHistorySerializer.errors}
    return Response(error_dict, status=status.HTTP_409_CONFLICT)


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
