from rest_framework import generics, status
from rest_framework.decorators import api_view
from ..models import JobRole
from ..serializers import JobRoleSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.utils import timezone

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

    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = JobRoleSerializer(data=body) 

        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"JobRole {body.get('job_role')} successfully created"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

job_role_create_view = JobRoleCreateAPIView.as_view()

class JobRoleUpdateAPIView(generics.UpdateAPIView):
    queryset = JobRole.objects.all()
    serializer_class = JobRoleSerializer
    lookup_field = 'pk'


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        job_role_name = body.get('job_role')
        request.data.update({'updated_at': timezone.now()})

        super(JobRoleUpdateAPIView, self).update(request, *args, **kwargs) 
        return Response({"message": f"JobRole {job_role_name} successfully updated"})


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
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)

@api_view(['POST'])
def job_role_delete_apiview(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    delete_ids = body.get('ids')

    for i in delete_ids:
        job_role = JobRole.objects.get(pk=i)
        job_role.delete()

    return Response({"message": f"Job roles {delete_ids} successfully deleted"})