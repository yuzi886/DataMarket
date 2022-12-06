from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<ID>/', views.detail, name='detail'),
]
"""    path('seller/', views.seller, name='seller'),
    path('seller/addData', views.addData, name='addData'),
    path('buyer/', views.buyer, name='buyer'),
    path('dataList/', views.dataList, name='dataList'),"""