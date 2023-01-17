from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         data = super().get_token(user)
#         data['email'] = user.email
    
#         data['user'] = user.__dict__

#         print('--'*100)
#         print(user.__dict__)
#         print('--'*100)

#         return data

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
    def validate(self, user):
        data = super().validate(user)
        refresh = self.get_token(self.user)
        data['user_info'] = {}

        print(self.user.__dict__)
        data['user_info']['email'] = self.user.email
        data['user_info']['id'] = self.user.id
        data['user_info']['first_name'] = self.user.first_name
        data['user_info']['middle_name'] = self.user.middle_name
        data['user_info']['last_name'] = self.user.last_name
        data['user_info']['employee_id'] = self.user.employee_id
        data['user_info']['job_role_id'] = self.user.job_role_id

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def getRoutes(request):
    routes=[
        'api/token',
        'api/token/refresh'
    ]

    return Response(routes)