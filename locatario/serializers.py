from rest_framework import serializers
from .models import Locatario
from core.models import Telefone
from core.serializers import TelefoneSerializer

class LocatarioSerializer(serializers.ModelSerializer):

    telefones = TelefoneSerializer(many=True)

    class Meta:
        model = Locatario
        fields = '__all__'


    def create(self, validated_data):
        telefones_data = validated_data.pop('telefones')
        locatario = Locatario.objects.create(**validated_data)
        for telefone_data in telefones_data:
            Telefone.objects.create(pessoa=locatario, **telefone_data)

        return locatario
    
    def update(self, instance, validated_data):
        telefones_data = validated_data.pop('telefones')
        instance = super().update(instance, validated_data)

        #Atualiza os telefones associados
        instance.telefones.all().delete()
        for telefone_data in telefones_data:
            Telefone.objects.create(pessoa=instance, **telefone_data)

        return instance