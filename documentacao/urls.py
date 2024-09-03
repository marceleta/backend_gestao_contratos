from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocPessoaFisicaViewSet, DocPessoaJuridicaViewSet

router = DefaultRouter()
router.register(r'doc-pessoa-fisica', DocPessoaFisicaViewSet, basename='docpessoafisica')
router.register(r'doc-pessoa-juridica', DocPessoaJuridicaViewSet, basename='docpessoajuridica')

urlpatterns = [
    path('', include(router.urls)),
]
