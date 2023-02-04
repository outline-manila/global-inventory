from rest_framework import generics, status
from rest_framework.decorators import api_view
from ..models import PartNo
from ..serializers import PartNoSerializer, ProductSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

# class PartNoView(mixins.ListModelMixin, generics.API):
# generics.RetrieveAPIView, 
class PartNoDetailAPIView(generics.RetrieveAPIView):
    queryset = PartNo.objects.all()
    serializer_class = PartNoSerializer
    lookup_field = 'pk'

part_no_detail_view = PartNoDetailAPIView.as_view()

class PartNoListAPIView(generics.ListAPIView):
    queryset = PartNo.objects.all()
    serializer_class = PartNoSerializer

part_no_list_view = PartNoListAPIView.as_view()

class PartNoCreateAPIView(generics.CreateAPIView):
    queryset = PartNo.objects.all()
    serializer_class = PartNoSerializer

    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = PartNoSerializer(data=body) 
        is_valid = False

        part_name = body['part']
        part_brand = body['brand']

        queryset = PartNo.objects.filter(part=part_name, brand=part_brand)
        
        if queryset:
            return Response({"message": f"Part {part_name} with this Brand {part_brand} already exists"}, status=status.HTTP_409_CONFLICT)

        if serializer.is_valid():
            is_valid = True
            part_obj = serializer.save()
            part_id = part_obj.pk
            body['part'] = part_id
            product_serializer = ProductSerializer(data=body)

            if product_serializer.is_valid():
                product_serializer.save()
                return Response({"message": f"PartNo {body.get('part')} successfully created"}, status=status.HTTP_201_CREATED)

        errors = serializer.errors
        if is_valid: 
            errors.update(product_serializer.errors)

        error_dict = {error: errors[error][0] for error in errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

part_no_create_view = PartNoCreateAPIView.as_view()

class PartNoUpdateAPIView(generics.UpdateAPIView):
    queryset = PartNo.objects.all()
    serializer_class = PartNoSerializer
    lookup_field = 'pk'


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        part_no_name = body.get('part')
        request.data.update({'updated_at': timezone.now()})

        pk = kwargs['pk']

        super(PartNoUpdateAPIView, self).update(request, *args, **kwargs)
        return Response({"message": f"PartNo {part_no_name} successfully updated"})


part_no_update_view = PartNoUpdateAPIView.as_view()


@api_view(['POST'])
def part_no_search_view(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'
    filter_by = body.get('filterBy')
    filter_id = body.get('filterId')
    search_key = body.get('searchKey')
    filter_dict = None

    if (filter_by and filter_id) or search_key:
        filter_dict = {}

        if filter_by and filter_id and None:
            filter_dict = {filter_dict[filter_by]: filter_id}
        if search_key: filter_dict['part__icontains'] = search_key

    if filter_dict:
        queryset = PartNo.objects.filter(**filter_dict).all().order_by(sort_by)

    else:
        queryset = PartNo.objects.filter().all().order_by(sort_by)

    result = {}
    if not (current_page and page_size):
        result['data'] = queryset.values()
        return Response(result)

    data = PartNoSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)

@api_view(['POST'])
def part_delete_apiview(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    delete_ids = body.get('ids')

    for i in delete_ids:
        part = PartNo.objects.get(pk=i)
        part.delete()

    return Response({"message": f"Parts {delete_ids} successfully deleted"})

@api_view(['POST'])
def bulk_create_parts(request):
    if "csv_file" not in request.FILES:
        return Response({"error": "No CSV file found in request"}, status=status.HTTP_400_BAD_REQUEST)

    csv_file = request.FILES["csv_file"]

    if not csv_file.name.endswith('.csv'):
        return Response({"error": "File is not a CSV file"}, status=status.HTTP_400_BAD_REQUEST)

    # Read the csv file
    parts = []
    file_data = csv_file.read().decode("UTF-8")
    lines = file_data.split("\n")
    header = None
    lines = lines[:20]
    print(lines)
    for line in lines:
        if header is None:
            header = line.split(",")
        else:
            part = line.split(",")
            part_dict = dict(zip(header, part))
            parts.append(part_dict)

    # Check if there is a duplicate part with the same brand
    brand_part_combinations = []
    print("##"*50)
    for part in parts:
        brand_part_combination = (part['brand'], part['part'])
        if brand_part_combination in brand_part_combinations:
            # return Response({"error": f"Duplicate part with brand '{part['brand']}' and part '{part['part']}' found in CSV file"}, status=status.HTTP_400_BAD_REQUEST)
            print(f"DUPLICATE FOUND {part['brand']}' and part '{part['part']} SKIPPING THESE")
        brand_part_combinations.append(brand_part_combination)
    print("##"*50)


    serializer = PartNoSerializer(data=parts, many=True)
    if serializer.is_valid():
        part_list = serializer.save()
        print(part_list)
        # part_obj = serializer.save()
        # part_id = part_obj.pk
        # ['part'] = part_id
        # product_serializer = ProductSerializer(data=body)

        # if product_serializer.is_valid():
        #     product_serializer.save()
        print('PART LIST LEN', len(part_list))
        for part in part_list:
            data={}
            data['part'] = part.id
            data['brand'] = part.brand.brand
            data['description'] = part.description
            data['other_part_no'] = part.other_part_no
            
            product_serializer = ProductSerializer(data=data)
            print('saving', data)
            if product_serializer.is_valid():
                print('IS VALID')
                product_serializer.save()
            else:
                return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
