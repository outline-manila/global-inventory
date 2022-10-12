from django.urls import path

from .api import rest_user

urlpatterns = [
    # user
    path('user/', rest_user.user_list_view,  name='user_list'),
    path('user/<int:pk>/', rest_user.user_detail_view,  name='user-detail'),
    path('user/update/<int:pk>', rest_user.user_update_view, name='user_update'),
    path('user/search/', rest_user.user_search_view, name='user_search'),

]
