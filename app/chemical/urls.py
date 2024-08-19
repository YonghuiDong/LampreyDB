# coding: utf-8

from django.urls import path, re_path
from django.conf.urls import url

from . import views


app_name = 'chemical'


urlpatterns = [
    path('', views.index, name='index'),
    path('material/create', views.material_create, name='material_create'),
    path('material/<int:material_id>/view', views.material_view, name='material_view'),
    path('material/<int:material_id>/edit', views.material_edit, name='material_edit'),
    path('material/<int:material_id>/delete', views.material_delete, name='material_delete'),
    path('material/list', views.material_list, name='material_list'),
    path('material/search', views.material_search, name='material_search'),

    path('about', views.about, name='about'),
    path('about/update', views.about_update, name='about_update'),
    path('contact', views.contact, name='contact'),
    path('contact/update', views.contact_update, name='contact_update'),
    ]
