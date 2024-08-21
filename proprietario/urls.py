from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProprietarioViewSet, RepresentanteViewSet

# Configuração do DefaultRouter para o app proprietario
router = DefaultRouter(trailing_slash=False)
router.register(r'proprietarios', ProprietarioViewSet, basename='proprietario')
router.register(r'representantes', RepresentanteViewSet, basename='representante')



urlpatterns = [
    path('', include(router.urls)),
]