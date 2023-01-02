from rest_framework import generics, status
from rest_framework.decorators import api_view
from ..models import Supplier
from ..serializers import SupplierSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.utils import timezone

# class SupplierView(mixins.ListModelMixin, generics.API):
class SupplierDetailAPIView(generics.RetrieveAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    lookup_field = 'pk'

supplier_detail_view = SupplierDetailAPIView.as_view()

class SupplierListAPIView(generics.ListAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

supplier_list_view = SupplierListAPIView.as_view()

class SupplierCreateAPIView(generics.CreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = SupplierSerializer(data=body) 

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Supplier {body.get('supplier')} successfully created"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

supplier_create_view = SupplierCreateAPIView.as_view()

class SupplierUpdateAPIView(generics.UpdateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    lookup_field = 'pk'


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        supplier_name = body.get('supplier')
        request.data.update({'updated_at': timezone.now()})

        super(SupplierUpdateAPIView, self).update(request, *args, **kwargs) 
        return Response({"message": f"Supplier {supplier_name} successfully updated"})

supplier_update_view = SupplierUpdateAPIView.as_view()


@api_view(['POST'])
def supplier_search_view(request, pk=None, *args, **kwargs):

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
        queryset = Supplier.objects.filter(filter_dict).all().order_by(sort_by).values()

    else:
        queryset = Supplier.objects.filter().all().order_by(sort_by).values()

    data = SupplierSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)

@api_view(['POST'])
def supplier_delete_apiview(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    delete_ids = body.get('ids')

    for i in delete_ids:
        supplier = Supplier.objects.get(pk=i)
        supplier.delete()

    return Response({"message": f"Supplier {delete_ids} successfully deleted"})
