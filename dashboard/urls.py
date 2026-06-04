from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .api_views import MaterialPurchaseAPIViewSet

app_name = 'dashboard'

router = DefaultRouter()
router.register(r'materials', MaterialPurchaseAPIViewSet, basename='materials')

urlpatterns = [
    path('', views.index, name='index'),
    path('yield/input/', views.yield_input, name='yield_input'),
    path('api/', include(router.urls)),
    path('', include(router.urls)),
]
