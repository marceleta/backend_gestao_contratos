from django.urls import path, include
from rest_framework.routers import DefaultRouter
from kanban.views import KanbanViewSet, KanbanColumnViewSet, KanbanColumnOrderViewSet

# Criação do roteador do Django Rest Framework
router = DefaultRouter()
router.register(r'kanban', KanbanViewSet, basename='kanban')
router.register(r'colunas', KanbanColumnViewSet, basename='kanban-column')
router.register(r'kanbancolumnorder', KanbanColumnOrderViewSet, basename='kanbancolumnorder')

# URL patterns, incluindo as rotas do roteador
urlpatterns = [
    path('', include(router.urls)),
]
