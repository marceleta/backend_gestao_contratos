from rest_framework import serializers
from .models import Telefone, Estado

class TelefoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefone
        fields = ['numero', 'tipo']


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['sigla', 'nome']