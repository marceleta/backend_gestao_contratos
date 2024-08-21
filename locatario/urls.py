from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocatarioViewSet

#Configuração do DefaultRouter para o app locatario
router = DefaultRouter(trailing_slash=False)
router.register(r'locatario', LocatarioViewSet, basename='locatario')

urlpatterns = [
    path('', include(router.urls)),
]