from rest_framework import generics
from rest_framework.decorators import api_view
from ..models import Brand
from ..serializers import BrandSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# class BrandView(mixins.ListModelMixin, generics.API):
# generics.RetrieveAPIView, 
class BrandDetailAPIView(generics.RetrieveAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'pk'

brand_detail_view = BrandDetailAPIView.as_view()

class BrandListAPIView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

brand_list_view = BrandListAPIView.as_view()

class BrandCreateAPIView(generics.CreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

brand_create_view = BrandCreateAPIView.as_view()

class BrandUpdateAPIView(generics.UpdateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'pk'

brand_update_view = BrandUpdateAPIView.as_view()


@api_view(['POST'])
def brand_search_view(request, pk=None, *args, **kwargs):

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
        queryset = Brand.objects.filter(filter_dict).all().order_by(sort_by).values()

    else:
        queryset = Brand.objects.filter().all().order_by(sort_by).values()

    data = BrandSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['total'] = p.count
    result['numPages'] = p.num_pages
    result['metadata'] = p.page(current_page).object_list

    return Response(result)
