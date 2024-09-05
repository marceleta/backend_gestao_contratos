from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocPessoaFisicaViewSet, DocPessoaJuridicaViewSet, FotosVideoImovelViewSet, DocumentoImovelViewSet

router = DefaultRouter()
router.register(r'doc-pessoa-fisica', DocPessoaFisicaViewSet, basename='docpessoafisica')
router.register(r'doc-pessoa-juridica', DocPessoaJuridicaViewSet, basename='docpessoajuridica')
router.register(r'fotos-video-imovel', FotosVideoImovelViewSet, basename='fotosvideoimovel')
router.register(r'documento-imovel', DocumentoImovelViewSet, basename='documentoimovel')

urlpatterns = [
    path('', include(router.urls)),
]
