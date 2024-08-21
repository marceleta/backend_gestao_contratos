from rest_framework import viewsets, permissions
from .models import Proprietario, Representante
from .serializers import ProprietarioSerializer, RepresentanteSerializer


class ProprietarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Proprietários.

    Este ViewSet fornece as operações CRUD para o modelo Proprietario e está otimizado
    para minimizar o número de queries ao banco de dados usando `select_related`.
    Acesso restrito a usuários autenticados.
    """
    queryset = Proprietario.objects.all().select_related('estado')  # Otimização do queryset
    serializer_class = ProprietarioSerializer
    permission_classes = [permissions.IsAuthenticated]  # Permissões de acesso

    def perform_create(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao criar um Proprietário.
        Pode ser útil para adicionar lógica customizada, como associar o proprietário
        a um usuário autenticado, caso seja necessário.
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao atualizar um Proprietário.
        Pode ser usado para executar validações ou ajustes antes de salvar as mudanças.
        """
        serializer.save()


class RepresentanteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Representantes.

    Este ViewSet fornece as operações CRUD para o modelo Representante.
    Acesso restrito a usuários autenticados.
    """
    queryset = Representante.objects.all()
    serializer_class = RepresentanteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao criar um Proprietário.
        Pode ser útil para adicionar lógica customizada, como associar o proprietário
        a um usuário autenticado, caso seja necessário.
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Método sobrescrito para adicionar lógica adicional ao atualizar um Proprietário.
        Pode ser usado para executar validações ou ajustes antes de salvar as mudanças.
        """
        serializer.save()