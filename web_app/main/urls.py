from django.urls import path
from . import views

urlpatterns = [
    path('', views.city_list, name='city_list'),
    path('cities/<int:city_id>/', views.point_of_interest_list, name='point_of_interest_list'),
   path('point/<int:point_id>/', views.point_of_interest_detail, name='point_of_interest_detail'),
]
