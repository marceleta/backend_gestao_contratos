from django.urls import path, include
from rest_framework.routers import DefaultRouter
from imovel.views import ImovelViewSet, SituacaoFiscalViewSet, TransacaoImovelViewSet

# Criação do roteador padrão do Django REST Framework
router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet, basename='imovel')
router.register(r'situacoes-fiscais', SituacaoFiscalViewSet, basename='situacaofiscal')
router.register(r'transacoes-imoveis', TransacaoImovelViewSet, basename='transacaoimovel')

# Inclusão das rotas no urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]