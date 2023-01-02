import json

from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Brand
from ..serializers import BrandSerializer


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

    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = BrandSerializer(data=body) 

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Brand {body.get('brand')} successfully created"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

brand_create_view = BrandCreateAPIView.as_view()

class BrandUpdateAPIView(generics.UpdateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        brand_name = body.get('brand')
        request.data.update({'updated_at': timezone.now()})

        super(BrandUpdateAPIView, self).update(request, *args, **kwargs) 
        return Response({"message": f"Brand {brand_name} successfully updated"})


brand_update_view = BrandUpdateAPIView.as_view()


@api_view(['POST'])
def brand_search_view(request, *args, **kwargs):

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
    result['metadata'] = {}

    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)


@api_view(['POST'])
def brand_delete_apiview(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    delete_ids = body.get('ids')

    for i in delete_ids:
        brand = Brand.objects.get(pk=i)
        brand.delete()

    return Response({"message": f"Brands {delete_ids} successfully deleted"})