import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication
import json

from core.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def get_user_by_token(request, *args, **kwargs):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    token = body.get('token')
    secret_key = "django-insecure-subx%4i+bs2(*c%xj)_a5b(672+#*9ge1mw1kl8b9fl_w&7%)%"
    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])

    user_id = decoded_token['user_id']    
    user = User.objects.get(pk=user_id)
    return Response({'user_id': user.id, 'username': user.email, 'first_name': user.first_name, 'last_name': user.last_name})
