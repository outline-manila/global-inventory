import json

from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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


def generate_action(parts_list: list):

    return ', '.join(['{} - ({}) - {}'.format(part['part_name'], part['qty'], part['brand']) for part in parts_list])

# class ProductDetailAPIView(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ReturnProductSerializer
#     lookup_field = 'part'

# product_detail_view = ProductDetailAPIView.as_view()
@api_view(["GET"])
def product_detail_view(request, part_id):
    part = get_object_or_404(PartNo, pk=part_id)
    result = PartNoSerializer(part, many=False).data
    part_name = result['part'] 
    return Response({"M": part_name})

@api_view(["POST"])
def get_by_part_warehouse(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    part_id = body.get('part_id')
    brand = body.get('brand')
    part_name = body.get('part')
    if part_name :
        obj = PartNo.objects.filter(part=part_name, brand=brand).first()
        part_id = obj.id

    warehouse = body.get('warehouse')

    filter_dict = {}
    filter_dict['part'] = part_id
    filter_dict['brand'] = brand
    filter_dict['warehouse'] = warehouse

    queryset = Product.objects.filter(**filter_dict).first()

    if not queryset:
        part_obj = get_object_or_404(PartNo, pk=part_id)
        result = PartNoSerializer(part_obj, many=False).data
        return Response(result)
    
    return Response(ReturnProductSerializer(queryset).data)

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(~Q(warehouse=None)).all()
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
        inbound_dict['brand'] = part.get('brand')
        quantity = part.get('quantity')

        queryset = Product.objects.filter(part=part.get('part'), warehouse=warehouse)
        if not queryset:
            inbound_dict['remaining_stock'] = part.get('quantity')
            product_serializer = ProductSerializer(data=inbound_dict)
            if product_serializer.is_valid():
                product_serializer.save()
            else:
                error_dict = {error: product_serializer.errors[error][0] for error in product_serializer.errors}
                return Response(error_dict, status=status.HTTP_409_CONFLICT)
        else:        
            queryset.update(remaining_stock=F('remaining_stock') + quantity, **inbound_dict)

    reference_number =  update_inbound_history(body)
    # return reference_number

    return Response({'message': f'Remaining stocks increased in {part_list}. Invoice Number: {reference_number}'})

def update_inbound_history(body):

    products = body.get('product')

    part_list = [ 
        {
            "part_name": PartNo.objects.get(pk=product.get('part')).part,
            "qty": product.get('quantity'),
            "brand": product.get('brand')

        } for product in products
     ]

    # parts = [ product['part'] for product in products ]
    # part_names = [ PartNo.objects.get(pk=part).part for part in parts ]
    action = generate_action(part_list)
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

    for part_item in parts:
        part_id = part_item.get('part_id')
        brand = part_item.get('brand')
        quantity = part_item.get('quantity')
        unit = part_item.get('unit')

        queryset = Product.objects.filter(part=part_id, warehouse=body.get('warehouse_from'))
        if not queryset: return Response({'message': 'part not found'}, status=status.HTTP_404_NOT_FOUND)
        remaining_stocks = Product.objects.filter(part=part_id, warehouse=body.get('warehouse_from')).values('remaining_stock').first()['remaining_stock']
        print(f"Remaining Stocks of {part_id} is {remaining_stocks}, quantity is {quantity} ")

        if remaining_stocks < quantity: return Response({'message': 'value larger than stocks'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset.update(remaining_stock=F('remaining_stock') - quantity, unit=unit)

    reference_number =  update_outbound_history(body)

    print(reference_number)

    return Response({'message': f'Remaining stocks decreased in {parts}. Invoice Number: {reference_number}'})

def update_outbound_history(body):

    print('body', body)

    products = body.get('product')

    part_list = [ 
        {
            "part_name": PartNo.objects.get(pk=product.get('part_id')).part,
            "qty": product.get('quantity'),
            "brand": product.get('brand')

        } for product in products
     ]

    action = generate_action(part_list)
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

    filter_dict = None
    filter_by = f"{body.get('filterBy')}__{body.get('filterBy')}__contains"
    filter_id = body.get('filterId')
    search_key = body.get('searchKey')
    warehouse = body.get('warehouse')

    if warehouse:
        filter_dict = {"warehouse": warehouse}
    if (filter_by and filter_id) or search_key:
        if not warehouse:
            filter_dict = {}

        if filter_by and filter_id:
            filter_dict[filter_by] = filter_id
        if search_key: filter_dict['part__part__contains'] = search_key

    result = {}
    if not (current_page and page_size):
        if filter_dict:
            result['data'] = ReturnProductSerializer(Product.objects.filter(**filter_dict).all().order_by(sort_by), many=True).data
        else:
            result['data'] = ReturnProductSerializer(Product.objects.filter().all().order_by(sort_by), many=True).data
        return Response(result)

    if filter_dict:
        p = Paginator(Product.objects.filter(**filter_dict).order_by(sort_by), page_size)
    else:
        p = Paginator(Product.objects.filter().all(), page_size)

    result = {}
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = ReturnProductSerializer(p.page(current_page).object_list, many=True).data

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

#### DANGER ####
@api_view(['POST', 'GET'])
def bulk_create_product(request):

    part_object_list = PartNo.objects.filter().all()
    for part in part_object_list:
        data={}
        data['part'] = part.id
        data['brand'] = part.brand.brand
        data['description'] = part.description
        data['alternatives'] = part.alternatives
        data['warehouse'] = 'Main Warehouse'
        
        product_serializer = ProductSerializer(data=data)
        if product_serializer.is_valid():
            product_serializer.save()
        else:
            print("PROBLEM WITH THIS PRODUCT, SKIPPING")
            return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
    return Response(product_serializer.data, status=status.HTTP_201_CREATED)

    