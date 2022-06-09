"""carpentry URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
app_name = 'boards'
from django.contrib import admin
from .models import Package
#from django.conf.urls import url
from django.urls import path,include,re_path
from django.views.generic import TemplateView
from rest_framework import routers, serializers, viewsets
from . import views

router = routers.DefaultRouter()
router.register(r'api/package', views.PackageViewSet)
router.register(r'api/index', views.IndexViewSet)
router.register(r'api/supplier', views.SupplierViewSet)

urlpatterns = [
    path('', views.home,name='home'),
    path('', include(router.urls)),
    re_path(r'^loginlocal/$', views.loginlocal,name='loginlocal'),
    re_path(r'^logoutlocal/$', views.logoutlocal,name='logoutlocal'),
 
    re_path(r'^scanner/load/$', views.scanner_load,name='scanner_load'),
    re_path(r'^scanner/load2/$', views.scanner_load2,name='scanner_load2'),
    
    re_path(r'^admission/$', views.admission,name='admission'),
    re_path(r'^suppliers/$', views.suppliers,name='suppliers'),
    re_path(r'^suppliers_add/$', views.suppliers_add,name='suppliers_add'),
    re_path(r'^packages/$', views.packages,name='packages'),
    re_path(r'^packages_filter/$', views.packages_filter,name='packages_filter'),
    re_path(r'^indexes/$', views.indexes,name='indexes'),
    re_path(r'^info_del/$', views.info_del,name='info_del'),
    re_path(r'^indexes_add/$', views.indexes_add,name='indexes_add'),
    re_path(r'^index_report/$', views.index_report,name='index_report'),
    re_path(r'^index_report2/$', views.index_report2,name='index_report2'),
    re_path(r'^index_report3/$', views.index_report3,name='index_report3'),
    re_path(r'^suppliers_report/$', views.suppliers_report,name='suppliers_report'),
    re_path(r'^packages_delivery/$',views.packages_delivery,name='packages_delivery'),
    #re_path(r'^packages_delivery_edit/$',views.packages_delivery_edit,name='packages_delivery_edit'),
    path('packages_delivery_edit/<slug:wz>',views.packages_delivery_edit,name='packages_delivery_edit'),
    path('packages_edit/<int:pk>',views.packages_edit,name='packages_edit'),
    path('packages_edit2/<int:pk>',views.packages_edit,name='packages_edit'), 

    path('packages_history/<int:pk>',views.packages_history,name='packages_history'),
    path('packages_index/<int:pk>/<slug:wz>',views.packages_index,name='packages_index'),
    path('suppliers_del/<int:pk>',views.suppliers_del,name='suppliers_del'),
    path('indexes_del/<int:pk>',views.indexes_del,name='indexes_del'),
    path('packages_del/<int:pk>',views.packages_del,name='packages_del'),
    path('packages_del_delivery/<int:pk>',views.packages_del_delivery,name='packages_del_delivery'),
    path('print_label/<str:prt>/<int:pk>',views.print_label,name='print_label'),
    path('stany_produkcja/',views.stany_produkcja,name='stany_produkcja'),
    path('stany_magazyn/',views.stany_magazyn,name='stany_magazyn'),
    path('stany_lacznie/',views.stany_lacznie,name='stany_lacznie'),
    path('zuzycie/',views.zuzycie,name='zuzycie'),
    path('zuzycie_log/',views.zuzycie_log,name='zuzycie_log'),
    path('inventory_rep/',views.inventory_rep,name='inventory_rep'),
    path('add_inv_arch/',views.add_inv_arch,name='add_inv_arch'),
    path('inventory_arch/',views.inventory_arch,name='inventory_arch'),
    path('inventory_move/',views.inventory_move,name='inventory_move'),
    path('inventory_retrieve/', views.inventory_retrieve.as_view()),
    path('scanner/load3/read_package/<str:pk>', views.scanner_load3_read_package,name='scanner_load3_read_package'),
    path('scanner/load3/warehouse_package/<str:pk>/<str:length>', views.scanner_load3_warehouse_package,name='scanner_load3_warehouse_package'),
    path('scanner/load3/prd_package/<str:pk>/<str:length>', views.scanner_load3_prd_package,name='scanner_load3_prd_package'),
    path('scanner/load3/closed_package/<str:pk>/<str:length>', views.scanner_load3_closed_package,name='scanner_load3_closed_package'),
    path('scanner/load3/login/<str:id>/<str:host>/<str:name>', views.scanner_load3_login,name='scanner_load3_login'),
    path('scanner/load3/logout/<str:host>', views.scanner_load3_logout,name='scanner_load3_logout'),

    #serializers
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))




]
