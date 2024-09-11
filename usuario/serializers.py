from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):

    permissoes = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'permissoes']

    def get_permissoes(self, obj):
        # Retorna todas as permissões do usuário
        return list(obj.get_all_permissions())