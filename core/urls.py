from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstadoViewSet

#Configuração do DefaultRouter para o app proprietario
router = DefaultRouter(trailing_slash=False)
router.register(r'estados', EstadoViewSet, basename='estado')

urlpatterns = [
    path('', include(router.urls))
]