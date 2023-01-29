import json

from django.contrib.auth.decorators import user_passes_test
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core import serializers

# from models.CustomUserManager import create_user
from ..models import User


# @user_passes_test(lambda u: u.is_superuser)
@api_view(['POST'])
def post_create_user(request):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    is_super_user = body.get('is_superuser', None)
    is_super_user = True
    email = body['email']
    first_name = body['first_name']
    last_name = body['last_name']
    middle_name = body.get('middle_name')
    password = body.get('password')
    employee_id = body.get('employee_id')

    # custom_user_service = User()

    if is_super_user:
        user = User.objects.create_superuser(email, first_name, middle_name, last_name, password, employee_id)
    
    else:
        user = User.objects.create_user(email, first_name, last_name, password)

    print(type(user))
    print(user)
    print("#"*100)
    user = serializers.serialize('json', [user])
    return Response(json.loads(user), status=status.HTTP_201_CREATED)



