from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import KanbanCardViewSet

# Cria o roteador e registra o ViewSet
router = DefaultRouter()
router.register(r'kanbancards', KanbanCardViewSet, basename='kanbancard')

urlpatterns = [
    path('', include(router.urls)),
]
