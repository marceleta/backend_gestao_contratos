from rest_framework import serializers
from .models import (
    Kanban, KanbanCard, KanbanColumnOrder
)
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class KanbanCardSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.all())
    class Meta:
        model = KanbanCard
        fields = [
            'id', 'lead_nome', 'descricao', 'data_criacao', 'ultima_atualizacao', 'data_prazo',
            'cor_atual', 'dados_adicionais', 'data_visita', 'observacoes_visita', 'visita_realizada',
            'visita_reagendada', 'valor_final', 'tipo_garantia', 'prazo_vigencia', 'metodo_pagamento',
            'status_negociacao', 'documentos_anexados', 'status_documentacao', 'resultado_analise_credito',
            'data_assinatura', 'contrato_assinado', 'content_type', 'object_id'
        ]


class KanbanColumnSerializer(serializers.ModelSerializer):
    cards = KanbanCardSerializer(many=True, read_only=True, source='kanban_cards')

    class Meta:
        model = KanbanColumnOrder
        fields = ['id', 'kanban', 'coluna_content_type', 'coluna_object_id', 'coluna', 'posicao', 'cards']

    def validate(self, attrs):
        """
        Valida se o ContentType e o objeto referenciado são válidos.
        """
        content_type = attrs.get('coluna_content_type')
        object_id = attrs.get('coluna_object_id')

        if content_type and object_id:
            model_class = content_type.model_class()
            if not model_class:
                raise serializers.ValidationError("Tipo de conteúdo inválido.")
            if not model_class.objects.filter(id=object_id).exists():
                raise serializers.ValidationError("Objeto referenciado não encontrado.")
        return attrs

    def create(self, validated_data):
        """
        Cria uma nova coluna e associa ao Kanban.
        """
        return KanbanColumnOrder.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Atualiza os dados da coluna no Kanban.
        """
        instance.posicao = validated_data.get('posicao', instance.posicao)
        instance.save()
        return instance



class KanbanSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    colunas = KanbanColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Kanban
        fields = ['id', 'nome', 'descricao', 'data_criacao', 'ultima_atualizacao', 'usuario', 'colunas']

    def create(self, validated_data):
        usuario = validated_data.get('usuario')
        kanban, created = Kanban.objects.get_or_create(usuario=usuario)
        return kanban
