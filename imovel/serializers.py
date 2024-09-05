from rest_framework import serializers
from .models import Imovel
from rest_framework import serializers
from .models import TransacaoImovel

class ImovelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Imovel
        fields = [
            'id', 'nome', 'endereco', 'bairro', 'cidade', 'estado', 'cep', 'area_total', 
            'area_util', 'tipo_imovel', 'num_quartos', 'num_banheiros', 'num_vagas_garagem',
            'ano_construcao', 'caracteristicas_adicionais', 'numero_registro', 
            'situacao_fiscal', 'certidoes_licencas', 'disponibilidade', 'data_cadastro'
        ]
        

class TransacaoImovelSerializer(serializers.ModelSerializer):
    imovel = ImovelSerializer(read_only=True)

    class Meta:
        model = TransacaoImovel
        fields = [
            'id', 'imovel', 'tipo_transacao', 'valor', 'condicoes_pagamento', 
            'data_disponibilidade'
        ]
