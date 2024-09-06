from rest_framework import serializers
from .models import Imovel, TransacaoImovel, SituacaoFiscal
from rest_framework import serializers


class SituacaoFiscalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SituacaoFiscal
        fields = ['imovel','tipo', 'descricao', 'data_referencia', 'data_atualizacao']


class TransacaoImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransacaoImovel
        fields = ['imovel','tipo_transacao', 'valor', 'comissao', 'condicoes_pagamento', 'data_disponibilidade']

    def create(self, validated_data):
        transacao = TransacaoImovel.objects.create(**validated_data)

        return transacao


class ImovelSerializer(serializers.ModelSerializer):
    situacoes_fiscais = SituacaoFiscalSerializer(many=True, required=False)  # Relacionamento many-to-one
    transacoes = TransacaoImovelSerializer(many=True, required=False)  # Relacionamento many-to-one

    class Meta:
        model = Imovel
        fields = [
            'id', 'nome', 'endereco', 'bairro', 'cidade', 'estado', 'cep', 'area_total', 
            'area_util', 'tipo_imovel', 'num_quartos', 'num_banheiros', 'num_vagas_garagem',
            'ano_construcao', 'caracteristicas_adicionais', 'numero_registro', 
            'situacoes_fiscais', 'transacoes', 'disponibilidade', 'data_cadastro'
        ]