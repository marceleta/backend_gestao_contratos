from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from usuario.models import Usuario
from usuario.serializers import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Ajusta dinamicamente as permissões de acordo com a ação do ViewSet.
        """
        # Apenas administradores podem criar e excluir usuários
        if self.action in ['create', 'destroy', 'list']:  
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Usuário pode acessar seus próprios dados, admin pode acessar todos
            self.permission_classes = [permissions.IsAuthenticated]

        return super().get_permissions()
    
    def get_queryset(self):
        # Administradores podem ver todos os usuários
        if self.request.user.is_staff:
            return Usuario.objects.all().order_by('first_name')
        # Usuários comuns só acessam e atualizam seus próprios dados
        return Usuario.objects.filter(id=self.request.user.id).order_by('first_name')
