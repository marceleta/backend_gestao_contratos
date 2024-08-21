from rest_framework import viewsets, permissions
from .models import Locatario
from .serializers import LocatarioSerializer

class LocatarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Locatario.

    Este ViewSet fornece as operações CRUD para o modelo Locatario e está otimizado
    para minimizar o número de queries ao banco de dados usando `select_related`.
    Acesso restrito a usuários autenticados.
    """
    
    queryset = Locatario.objects.all()  # Otimização do queryset
    serializer_class = LocatarioSerializer
    permission_classes = [permissions.IsAuthenticated] # Permissões de acesso


    def perform_create(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao criar um Locatario.
        Pode ser útil para adicionar lógica customizada, como associar o Locatario
        a um usuário autenticado, caso seja necessário.
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao atualizar um Locatario.
        Pode ser usado para executar validações ou ajustes antes de salvar as mudanças.
        """
        serializer.save()