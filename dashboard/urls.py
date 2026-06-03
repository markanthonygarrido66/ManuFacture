from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('yield/input/', views.yield_input, name='yield_input'),
]
