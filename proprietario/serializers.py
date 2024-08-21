from rest_framework import serializers
from .models import Proprietario, Representante
from core.serializers import TelefoneSerializer
from core.models import Telefone
class ProprietarioSerializer(serializers.ModelSerializer):
    
    telefones = TelefoneSerializer(many=True)
    
    class Meta:
        model = Proprietario
        fields = '__all__'


    def create(self, validated_data):
        telefones_data = validated_data.pop('telefones')
        proprietario = Proprietario.objects.create(**validated_data)
        for telefone_data in telefones_data:
            Telefone.objects.create(pessoa=proprietario, **telefone_data)

        return proprietario
    

    def update(self, instance, validated_data):
        telefones_data = validated_data.pop('telefones')
        instance = super().update(instance, validated_data)

        instance.telefones.all().delete()
        for telefone_data in telefones_data:
            Telefone.objects.create(pessoa=instance, **telefone_data)

        return instance



class RepresentanteSerializer(serializers.ModelSerializer):

    telefones = TelefoneSerializer(many=True)

    class Meta:
        model = Representante
        fields = '__all__'


    def create(self, validated_data):
        telefones_data = validated_data.pop('telefones')
        representante = Representante.objects.create(**validated_data)
        for telefone_data in telefones_data:
            Telefone.objects.create(pessoa=representante, **telefone_data)

        return representante
    

    def update(self, instance, validated_data):
        telefones_data = validated_data.pop('telefones')
        instance = super().update(instance, validated_data)

        instance.telefones.all().delete()
        for telefone_data in telefones_data:
            Telefone.objects.create(pessoa=instance, **telefone_data)

        return instance

