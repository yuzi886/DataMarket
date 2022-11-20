from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seller/', views.seller, name='seller'),
    path('seller/addData', views.addData, name='addData'),
]