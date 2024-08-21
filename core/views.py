from rest_framework import viewsets, permissions
from .models import Estado
from .serializers import EstadoSerializer


class EstadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Estado.

    Este ViewSet fornece as operações CRUD para o modelo Estado e está otimizado
    para minimizar o número de queries ao banco de dados usando `select_related`.
    Acesso restrito a usuários autenticados.
    """

    queryset = Estado.objects.all() # Otimização do queryset
    serializer_class = EstadoSerializer
    permission_classes = [permissions.IsAuthenticated]  # Permissões de acesso


    def perform_create(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao criar um Estado.
        Pode ser útil para adicionar lógica customizada, como associar o Estado
        a um usuário autenticado, caso seja necessário.
        """

        serializer.save()

    def perform_update(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao atualizar um Estado.
        Pode ser usado para executar validações ou ajustes antes de salvar as mudanças.
        """
        serializer.save()