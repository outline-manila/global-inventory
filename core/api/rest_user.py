from rest_framework import generics
from rest_framework.decorators import api_view
from ..models import User

from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import serializers



class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'uuid', 
            'email', 
            'employee_id', 
            'first_name', 
            'last_name', 
            'joined_on'
        )


# class UserView(mixins.ListModelMixin, generics.API):
# generics.RetrieveAPIView, 
class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

user_detail_view = UserDetailAPIView.as_view()

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

user_list_view = UserListAPIView.as_view()

# class UserCreateAPIView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# user_create_view = UserCreateAPIView.as_view()

class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

user_update_view = UserUpdateAPIView.as_view()

@api_view(['POST'])
def user_detail_by_token(request, *args, **kwargs):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)


    

@api_view(['POST'])
def user_search_view(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    # sort_by = body.get('sortBy') or 'last_name'
    filter_by = body.get('filterBy') and None
    filter_id = body.get('filterId') and None
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        queryset = User.objects.filter(**filter_dict).all().order_by().values()

    else:
        queryset = User.objects.filter().all().order_by().values()

    data = UserSerializer(queryset, many=True).data
    p = Paginator(data, page_size)

    # result = {}
    # result['total'] = p.count
    # result['numPages'] = p.num_pages
    # result['data'] = p.page(current_page).object_list

    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)
