from django.urls import path, include
from rest_framework.routers import DefaultRouter
from locador.views import LocadorViewSet

router = DefaultRouter()
router.register(r'locadores', LocadorViewSet, basename='locador')

urlpatterns = [
    path('', include(router.urls)),
]
