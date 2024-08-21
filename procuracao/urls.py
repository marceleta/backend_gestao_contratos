from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcuracaoViewSet


router = DefaultRouter()
router.register(r'procuracoes', ProcuracaoViewSet, basename='procuracao')

urlpatterns = [
    path('', include(router.urls))
]
