import json

from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q, F
from itertools import chain
from ..models import Product, invoice_number, InboundHistory, OutboundHistory, PartNo
from core.models import User
from ..serializers import (
        ProductSerializer,
        InboundHistorySerializer,
        OutboundHistorySerializer,
        InboundHistoryCreateSerializer,
        OutboundHistoryCreateSerializer,
        ReturnProductSerializer,
        PartNoSerializer
    )


def generate_action(parts: list, action):

    part_string = ''

    if not parts:
        part_string = ''
    elif len(parts) == 1:
        part_string = f'Part {str(parts[0])}'
    elif len(parts) == 2:
       part_string =  f"Parts {parts[0]} and {parts[1]}"
    else:
        last_element = str(parts.pop())
        part_string =  f"Parts {', '.join(map(str, parts))}, and {last_element}"

    action_string = f'{action} {part_string}'

    return action_string

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'part'

product_detail_view = ProductDetailAPIView.as_view()

@api_view(["POST"])
def get_by_part_warehouse(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    part = body.get('part')
    brand = body.get('brand')
    warehouse = body.get('warehouse')

    filter_dict = {}
    filter_dict['part'] = part
    filter_dict['brand'] = brand
    warehouse['warehouse'] = warehouse

    queryset = Product.objects.filter(**filter_dict).first()

    if not queryset:
        part_obj = PartNo.object.filter(part=part).first()
        result = PartNoSerializer(part_obj)
        return Response(result)
    
    return ProductSerializer(queryset)

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(~Q(brand='NaN')).all()
    serializer_class = ReturnProductSerializer

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
    action = generate_action(parts, 'Added ')
    invoice_date = body.get('invoice_date')

    data = {}
    data['description'] = 'Add'
    data['date']: invoice_date
    data['invoice_no'] = body.get('invoice_no')
    data['action'] = action
    data['user'] = body.get('user_id')
    data['warehouse'] = body.get('warehouse')
    data['supplier'] = body.get('supplier')
    
    inbound_serializer = InboundHistoryCreateSerializer(data=data)

    if inbound_serializer.is_valid():
        inbound_serializer.save()
        return  data['invoice_no']

    print(inbound_serializer.errors)
    error_dict = {error: inbound_serializer.errors[error][0] for error in inbound_serializer.errors}


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

    action = generate_action(parts, 'Decreased')
    invoice_date = body.get('invoice_date')
    user_id = body.get('user_id')
    warehouse = body.get('warehouse_from')
    warehouse_to = body.get('warehouse_to')
    remarks = body.get('remarks')

    data = {}
    data['description'] = 'Checkout'
    data['date']: invoice_date
    data['action'] = action
    data['user'] = user_id
    data['warehouse'] = warehouse
    data['warehouse_to'] = warehouse_to
    data['remarks'] = remarks
    
    outbound_serializer = OutboundHistoryCreateSerializer(data=data)

    if outbound_serializer.is_valid():
        outbound_serializer.save()
        return Response({"message": f"Outbound successfully created"})
    
    error_dict = {error: outbound_serializer.errors[error][0] for error in outbound_serializer.errors}
    return Response(error_dict, status=status.HTTP_409_CONFLICT)

##


@api_view(['POST'])
def product_search_view(request, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'
    filter_by = f"{body.get('filterBy')}__{body.get('filterBy')}__contains"
    filter_by = 'alternatives__contains'
    print(filter_by)
    filter_id = body.get('filterId')
    filter_dict = None
    search_key = body.get('searchKey')

    if (filter_by and filter_id) or search_key:
        filter_dict = {}

        if filter_by and filter_id:
            filter_dict[filter_by] = filter_id
        if search_key: filter_dict['part__part__contains'] = search_key

    if filter_dict:
        queryset = Product.objects.filter(**filter_dict).all().order_by(sort_by)

    else:
        queryset = Product.objects.filter().all().order_by(sort_by)

    result = {}
    if not (current_page and page_size):
        result['data'] = ReturnProductSerializer(queryset, many=True).data
        return Response(result)

    data = ReturnProductSerializer(queryset, many=True).data
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
            filter_id = body.get('filterId')
            user_id_first = User.objects.filter(first_name__contains=filter_id).values('id')
            user_id_last = User.objects.filter(last_name__contains=filter_id).values('id')
            user_id_list = list(chain(user_id_first,user_id_last))
            user_id_list = list(set([item for d in user_id_list for item in d.values()]))
            queryset = InboundHistory.objects.filter(user__in=user_id_list).all().order_by(sort_by)
        else:
            filter_by = f"{body.get('filterBy')}__contains"
            filter_id = body.get('filterId')

    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict and filter_by != 'user':
        queryset = InboundHistory.objects.filter(**filter_dict).all().order_by(sort_by)

    if not filter_dict:
        queryset = InboundHistory.objects.filter().all().order_by(sort_by)

    data = InboundHistorySerializer(queryset, many=True).data

    # print(f"Hello {data}")

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
            filter_id = body.get('filterId')
            user_id_first = User.objects.filter(first_name__contains=filter_id).values('id')
            user_id_last = User.objects.filter(last_name__contains=filter_id).values('id')
            user_id_list = list(chain(user_id_first,user_id_last))
            user_id_list = list(set([item for d in user_id_list for item in d.values()]))
            queryset = OutboundHistory.objects.filter(user__in=user_id_list).all().order_by(sort_by)
        else:
            filter_by = f"{body.get('filterBy')}__contains"
            filter_id = body.get('filterId')

    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict and filter_by != 'user':
        queryset = OutboundHistory.objects.filter(**filter_dict).all().order_by(sort_by)

    if not filter_dict:
        queryset = OutboundHistory.objects.filter().all().order_by(sort_by)

    data = OutboundHistorySerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}

    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)



    