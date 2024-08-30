from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, EstadoViewSet

# Definindo o router para criar automaticamente as rotas padrão para EstadoViewSet
router = DefaultRouter()
router.register(r'estados', EstadoViewSet, basename='estado')

# Definindo as rotas detalhadas para o ClienteViewSet
cliente_list = ClienteViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

cliente_detail = ClienteViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

search_by_nome = ClienteViewSet.as_view({
    'get': 'search_by_nome',
})

urlpatterns = [
    # Rotas geradas automaticamente pelo router para EstadoViewSet
    path('', include(router.urls)),

    # Rota para listar e criar clientes
    path('clientes/', cliente_list, name='cliente-list'),

    # Rota para detalhar, atualizar, e deletar clientes
    path('clientes/<int:pk>/', cliente_detail, name='cliente-detail'),

    # Rota para a busca de clientes por nome
    path('clientes/search/', search_by_nome, name='cliente-search_by_nome'),
]
