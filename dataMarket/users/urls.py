from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<ID>/', views.detail, name='detail'),
    path('download/<ID>/', views.download, name='download'),
    path('add_cart/<ID>/', views.add_cart, name='add_cart'),
    path('shop_cart/',views.shop_cart, name = 'shop_cart'),
    path('formula/',views.formula, name = 'formula'),
    path('formula/add/',views.formula_add, name = 'formula_add'),
]
"""    path('seller/', views.seller, name='seller'),
    path('seller/addData', views.addData, name='addData'),
    path('buyer/', views.buyer, name='buyer'),
    path('dataList/', views.dataList, name='dataList'),"""