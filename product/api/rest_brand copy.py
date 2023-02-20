from rest_framework import generics
from rest_framework.decorators import api_view
from ..models import JobRole
from ..serializers import JobRoleSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# class JobRoleView(mixins.ListModelMixin, generics.API):
# generics.RetrieveAPIView, 
class JobRoleDetailAPIView(generics.RetrieveAPIView):
    queryset = JobRole.objects.all()
    serializer_class = JobRoleSerializer
    lookup_field = 'pk'

job_role_detail_view = JobRoleDetailAPIView.as_view()

class JobRoleListAPIView(generics.ListAPIView):
    queryset = JobRole.objects.all()
    serializer_class = JobRoleSerializer

job_role_list_view = JobRoleListAPIView.as_view()

class JobRoleCreateAPIView(generics.CreateAPIView):
    queryset = JobRole.objects.all()
    serializer_class = JobRoleSerializer

job_role_create_view = JobRoleCreateAPIView.as_view()

class JobRoleUpdateAPIView(generics.UpdateAPIView):
    queryset = JobRole.objects.all()
    serializer_class = JobRoleSerializer
    lookup_field = 'pk'

job_role_update_view = JobRoleUpdateAPIView.as_view()


@api_view(['POST'])
def job_role_search_view(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'
    filter_by = body.get('filterBy')
    filter_id = body.get('filterId')
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        queryset = JobRole.objects.filter(**filter_dict).all().order_by(sort_by).values()

    else:
        queryset = JobRole.objects.filter().all().order_by(sort_by).values()

    data = JobRoleSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['total'] = p.count
    result['numPages'] = p.num_pages
    result['metadata'] = p.page(current_page).object_list

    return Response(result)



from django.db.models import Q, Prefetch

@api_view(['POST'])
def product_search_view(request, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'

    filter_by = f"{body.get('filterBy')}__{body.get('filterBy')}__contains"
    filter_id = body.get('filterId')
    filter_dict = None
    search_key = body.get('searchKey')
    warehouse = body.get('warehouse')

    select_related_fields = ['part']

    if warehouse:
        filter_dict = {"warehouse": warehouse}
    if (filter_by and filter_id) or search_key:
        if not warehouse:   
            filter_dict = {}

        if filter_by and filter_id:
            filter_dict[filter_by] = filter_id
        if search_key: filter_dict['part__part__contains'] = search_key

    # products = Product.objects.filter().order_by(sort_by)
    # products = Product.objects.select_related('part').filter().order_by(sort_by)
    # products = Product.objects.filter()


    # if select_related_fields:
    #     products = products.select_related(*select_related_fields)

    # if prefetch_related_fields:
    #     products = products.prefetch_related(*prefetch_related_fields)

    # result = {}

    # if not (current_page and page_size):
    #     result['data'] = ReturnProductSerializer(Product.objects.select_related('part').filter().order_by(sort_by), many=True).data
    #     return Response(result)

    # # p = Paginator(Product.objects.select_related('part').filter().order_by(sort_by), page_size)
    # p = Paginator(Product.objects.select_related('part').filter().order_by(sort_by), page_size)


    # result['metadata'] = {}
    # result['metadata']['total'] = p.count
    # result['metadata']['numPages'] = p.num_pages
    # # result['data'] = p.page(current_page).object_list
    # result['data'] = ReturnProductSerializer(p.page(current_page).object_list, many=True).data

    # return Response(result)