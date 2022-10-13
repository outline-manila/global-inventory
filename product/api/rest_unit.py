from rest_framework import generics, status
from rest_framework.decorators import api_view
from ..models import Unit
from ..serializers import UnitSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# class UnitView(mixins.ListModelMixin, generics.API):
# generics.RetrieveAPIView, 
class UnitDetailAPIView(generics.RetrieveAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    lookup_field = 'pk'

unit_detail_view = UnitDetailAPIView.as_view()

class UnitListAPIView(generics.ListAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

unit_list_view = UnitListAPIView.as_view()

class UnitCreateAPIView(generics.CreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = UnitSerializer(data=body) 

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Unit {body.get('unit')} successfully created"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

unit_create_view = UnitCreateAPIView.as_view()

class UnitUpdateAPIView(generics.UpdateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    lookup_field = 'pk'


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        serializer = UnitSerializer(data=body) 

        unit_name = body.get('unit')

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Unit {unit_name} successfully updated"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)
unit_update_view = UnitUpdateAPIView.as_view()


@api_view(['POST'])
def unit_search_view(request, pk=None, *args, **kwargs):

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
        queryset = Unit.objects.filter(filter_dict).all().order_by(sort_by).values()

    else:
        queryset = Unit.objects.filter().all().order_by(sort_by).values()

    data = UnitSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)
