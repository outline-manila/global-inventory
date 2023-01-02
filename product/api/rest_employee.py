from rest_framework import generics, status
from rest_framework.decorators import api_view
from ..models import Employee
from ..serializers import EmployeeSerializer
from django.core.paginator import Paginator
import json
from rest_framework.response import Response
from django.utils import timezone

# class EmployeeView(mixins.ListModelMixin, generics.API):
class EmployeeDetailAPIView(generics.RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'pk'

employee_detail_view = EmployeeDetailAPIView.as_view()

class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

employee_list_view = EmployeeListAPIView.as_view()

class EmployeeCreateAPIView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def create(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        serializer = EmployeeSerializer(data=body) 
        employee_name = f"{body.get('first_name') or ''} {body.get('last_name') or ''}"
        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"Employee {employee_name} successfully created"})

        error_dict = {error: serializer.errors[error][0] for error in serializer.errors}
        return Response(error_dict, status=status.HTTP_409_CONFLICT)

employee_create_view = EmployeeCreateAPIView.as_view()

class EmployeeUpdateAPIView(generics.UpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'pk'


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        employee_name = f"{body.get('first_name') or ''} {body.get('last_name') or ''}"
        request.data.update({'updated_at': timezone.now()})

        print('Here we')
        super(EmployeeUpdateAPIView, self).update(request, *args, **kwargs) 
        print('asd')
        # Employee.objects.filter(pk=kwargs['pk']).update(**body) 
        return Response({"message": f"Employee {employee_name} successfully updated"})

employee_update_view = EmployeeUpdateAPIView.as_view()


@api_view(['POST'])
def employee_search_view(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    current_page = body.get('currentPage') 
    page_size = body.get('pageSize') 
    sort_by = body.get('sortBy') or '-updated_at'
    sort_by = _parse_sort(body.get('sortBy'), body.get('sortKey')) or '-updated_at'
    filter_by = body.get('filterBy')
    filter_id = body.get('filterId')
    filter_dict = None

    if filter_by and filter_id: filter_dict = {filter_by: filter_id}

    if filter_dict:
        queryset = Employee.objects.filter(**filter_dict).all().order_by(sort_by)

    else:
        queryset = Employee.objects.filter().all().order_by(sort_by)

    data = EmployeeSerializer(queryset, many=True).data

    print(data)

    p = Paginator(data, page_size)

    result = {}
    result['metadata'] = {}
    result['metadata']['total'] = p.count
    result['metadata']['numPages'] = p.num_pages
    result['data'] = p.page(current_page).object_list

    return Response(result)


def _parse_sort(sort_by, sort_key):
    if not (sort_by, sort_key):return 
    if sort_by not in {'asc', 'desc'}: return

    if sort_by == 'asc': return sort_key
    return '-'+sort_key

@api_view(['POST'])
def employee_delete_apiview(request, pk=None, *args, **kwargs):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    delete_ids = body.get('ids')

    for i in delete_ids:
        employee = Employee.objects.get(pk=i)
        employee.delete()

    return Response({"message": f"Employees {delete_ids} successfully deleted"})
