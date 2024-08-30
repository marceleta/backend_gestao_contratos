from rest_framework import serializers
from .models import Locatario
from core.models import Telefone
from core.serializers import TelefoneSerializer

class LocatarioSerializer(serializers.ModelSerializer):

    telefones = TelefoneSerializer(many=True)

    class Meta:
        model = Locatario
        fields = '__all__'
