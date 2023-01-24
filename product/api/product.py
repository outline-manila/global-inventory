import json

from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q, F

from ..models import Product, invoice_number, InboundHistory, OutboundHistory
from ..serializers import ProductSerializer, InboundHistorySerializer, OutboundHistorySerializer


def generate_action(parts: list, action):

    part_string = ''

    if not parts:
        part_string = ''
    elif len(parts) == 1:
        part_string = f'Part Number {str(parts[0])}'
    elif len(parts) == 2:
       part_string =  f"Part Numbers {parts[0]} and {parts[1]}"
    else:
        last_element = str(parts.pop())
        part_string =  f"Part Numbers {', '.join(map(str, parts))}, and {last_element}"

    action_string = f'{action} {part_string}'

    return action_string

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
    warehouse = body.get('warehouse')
    parts = body.get('product')

    part_list = [ part['part'] for part in parts ]
    for part in parts:
        inbound_dict = {}
        inbound_dict['unit'] = part.get('unit')
        inbound_dict['part'] = part.get('part')
        inbound_dict['supplier'] = supplier
        inbound_dict['warehouse'] = warehouse
        quantity = part.get('quantity')

        queryset = Product.objects.filter(part=part.get('part'))
        queryset.update(remaining_stock=F('remaining_stock') + quantity, **inbound_dict)

    reference_number =  update_inbound_history(body)
    # return reference_number

    return Response({'message': f'Remaining stocks increased in {part_list}. Invoice Number: {reference_number}'})

def update_inbound_history(body):

    products = body.get('product')

    parts = [ product['part'] for product in products ]
    action = generate_action(parts, 'Added stock in')
    invoice_date = body.get('invoice_date')
    # product_id = 
    user_id = 1

    data = {}
    data['description'] = 'Add'
    # data['product'] = product_id
    data['date']: invoice_date
    data['invoice_no'] = body.get('invoice_no')
    data['action'] = action
    data['user'] = user_id
    
    inbound_serializer = InboundHistorySerializer(data=data)

    if inbound_serializer.is_valid():
        inbound_serializer.save()
        return  data['invoice_no']

    
    error_dict = {error: inbound_serializer.errors[error][0] for error in inbound_serializer.errors}

    print(error_dict)

    return Response(error_dict, status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def outbound_product(request, *args, **kwargs):


    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    parts = body.get('product')

    part_list = [ part['part'] for part in parts ]
    for part_item in parts:
        inbound_dict = {}
        part = part_item.get('part')
        inbound_dict['part'] = part
        quantity = part_item.get('quantity')
        unit = part_item.get('unit')

        queryset = Product.objects.filter(part=part)
        print(queryset)
        if not queryset: return Response({'message': 'part not found'}, status=status.HTTP_404_NOT_FOUND)
        remaining_stocks = Product.objects.filter(part=part).values('remaining_stock').first()['remaining_stock']
        if remaining_stocks < quantity: return Response({'message': 'value larger than stocks'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset.update(remaining_stock=F('remaining_stock') - quantity, unit=unit)

    reference_number =  update_outbound_history(body)

    print(reference_number)

    return Response({'message': f'Remaining stocks decreased in {part_list}. Invoice Number: {reference_number}'})

def update_outbound_history(body):

    products = body.get('product')

    parts = [ product['part'] for product in products ]

    action = generate_action(parts, 'Decreased stock in')
    invoice_date = body.get('invoice_date')
    user_id = body.get('user_id')
    warehouse = body.get('warehouse')

    data = {}
    data['description'] = 'Checkout'
    data['date']: invoice_date
    data['action'] = action
    data['user'] = user_id
    data['warehouse'] = warehouse
    
    outbound_serializer = OutboundHistorySerializer(data=data)

    if outbound_serializer.is_valid():
        outbound_serializer.save()
        return Response({"message": f"Outbound successfully created"})
    
    error_dict = {error: outbound_serializer.errors[error][0] for error in outbound_serializer.errors}
    print('ERROR', error_dict)
    return Response(error_dict, status=status.HTTP_409_CONFLICT)

##


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

###################### Inbound History ############################


class InboundHistoryDetailAPIView(generics.RetrieveAPIView):
    queryset = InboundHistory.objects.all()
    serializer_class = InboundHistorySerializer
    lookup_field = 'pk'

inbound_history_detail_view = InboundHistoryDetailAPIView.as_view()

class InboundHistoryListAPIView(generics.ListAPIView):
    queryset = InboundHistory.objects.all()
    serializer_class = InboundHistorySerializer

inbound_history_list_view = InboundHistoryListAPIView.as_view()

class InboundHistoryCreateAPIView(generics.CreateAPIView):
    queryset = InboundHistory.objects.all()
    serializer_class = InboundHistorySerializer

    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = InboundHistorySerializer(data=body) 

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"InboundHistory {body.get('inbound_history')} successfully created"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

inbound_history_create_view = InboundHistoryCreateAPIView.as_view()

class InboundHistoryUpdateAPIView(generics.UpdateAPIView):
    queryset = InboundHistory.objects.all()
    serializer_class = InboundHistorySerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        inbound_history_name = body.get('inbound_history')
        request.data.update({'updated_at': timezone.now()})

        super(InboundHistoryUpdateAPIView, self).update(request, *args, **kwargs) 
        return Response({"message": f"InboundHistory {inbound_history_name} successfully updated"})


inbound_history_update_view = InboundHistoryUpdateAPIView.as_view()


@api_view(['POST'])
def inbound_history_search_view(request, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'
    filter_by = body.get('filterBy')
    if filter_by:
        if body.get('filterBy') == 'user':
            filter_by = f"{body.get('filterBy')}"
        else:
            filter_by = f"{body.get('filterBy')}__contains"

    filter_id = body.get('filterId')
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        print(filter_dict)
        queryset = InboundHistory.objects.filter(**filter_dict).all().order_by(sort_by)

    else:
        queryset = InboundHistory.objects.filter().all().order_by(sort_by)

    data = InboundHistorySerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}

    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)


@api_view(['POST'])
def inbound_history_delete_apiview(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    delete_ids = body.get('ids')

    for i in delete_ids:
        inbound_history = InboundHistory.objects.get(pk=i)
        inbound_history.delete()

    return Response({"message": f"InboundHistorys {delete_ids} successfully deleted"})

@api_view(['POST'])
def outbound_history_search_view(request, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'
    filter_by = body.get('filterBy')
    if filter_by:
        if body.get('filterBy') == 'user':
            filter_by = f"{body.get('filterBy')}"
        else:
            filter_by = f"{body.get('filterBy')}__contains"

    filter_id = body.get('filterId')
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        print(filter_dict)
        queryset = OutboundHistory.objects.filter(**filter_dict).all().order_by(sort_by)

    else:
        queryset = OutboundHistory.objects.filter().all().order_by(sort_by)

    data = OutboundHistorySerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}

    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)



    