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

        print('---'*100)
        print('Body:', body)
        print('---'*100)

        serializer = PartNoSerializer(data=body) 
        product_serializer = ProductSerializer(data=body)
        is_valid = False

        if serializer.is_valid():
            is_valid = True
            serializer.save()

            if product_serializer.is_valid():
                product_serializer.save()
            return Response({"message": f"PartNo {body.get('part')} successfully created"})

        errors = serializer.errors
        if is_valid: errors += product_serializer.errors

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
    filter_id = body.get('filterById')
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        queryset = PartNo.objects.filter(filter_dict).all().order_by(sort_by).values()

    else:
        queryset = PartNo.objects.filter().all().order_by(sort_by).values()

    data = PartNoSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)
