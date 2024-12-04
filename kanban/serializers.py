from rest_framework import serializers
from .models import Kanban, KanbanCard, KanbanColumnOrder, KanbanColumn
from django.contrib.auth import get_user_model

User = get_user_model()


class KanbanColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanColumn
        fields = ['id', 'nome', 'meta_dados', 'prazo_alerta', 'cor_inicial', 'cor_alerta']
        read_only_fields = ['id']  # O campo `id` será somente leitura
    @staticmethod
    def _validate_hex_color(value):
        """
            Valida se o valor fornecido é um código hexadecimal de cor válido.
            O valor deve começar com '#' e ter 4 ou 7 caracteres.

            Args:
                value (str): O valor a ser validado.

            Returns:
                str: O valor validado se for correto.

            Raises:
                serializers.ValidationError: Se o valor não for um código hexadecimal válido.
        """
        if not value.startswith('#') or len(value) not in [4, 7]:
            raise serializers.ValidationError("O campo deve ser um código hexadecimal válido.")
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError("O campo deve ser um código hexadecimal válido.")
        return value

    def validate_cor_inicial(self, value):
        return self._validate_hex_color(value)

    def validate_cor_alerta(self, value):
        return self._validate_hex_color(value)



class KanbanCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanCard
        fields = ['id', 'lead_nome', 'descricao', 'data_criacao', 'ultima_atualizacao', 'data_prazo', 'cor_atual', 'dados_adicionais', 'coluna']
        read_only_fields = ['id', 'data_criacao', 'ultima_atualizacao', 'cor_atual']


class KanbanColumnOrderSerializer(serializers.ModelSerializer):
    coluna_id = serializers.PrimaryKeyRelatedField(queryset=KanbanColumn.objects.all(), source='coluna')
    kanban_id = serializers.PrimaryKeyRelatedField(queryset=Kanban.objects.all(), source='kanban')

    class Meta:
        model = KanbanColumnOrder
        fields = ['id', 'coluna_id', 'kanban_id', 'posicao']

    def create(self, validated_data):
        #print(f'validated_data {validated_data}')
        # Extraímos `kanban` e `coluna` dos dados validados
        kanban = validated_data.pop('kanban')
        coluna = validated_data.pop('coluna')
        posicao = validated_data.pop('posicao')
        # Criamos a instância usando esses dados
        return KanbanColumnOrder.adicionar_e_reordenar(kanban=kanban, coluna=coluna, posicao=posicao)

    def update(self, instance, validated_data):
        # Extraímos os dados validados
        kanban = validated_data.get('kanban', instance.kanban)
        coluna = validated_data.get('coluna', instance.coluna)
        posicao = validated_data.get('posicao', instance.posicao)
        
        # Usamos o método associar_coluna para atualizar a instância
        updated_instance = KanbanColumnOrder.adicionar_e_reordenar(
            kanban=kanban,
            coluna=coluna,
            posicao=posicao
        )
        return updated_instance



class KanbanSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)  # Exibe o nome do usuário como string
    colunas = KanbanColumnOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Kanban
        fields = ['id', 'nome', 'descricao', 'data_criacao', 'ultima_atualizacao', 'usuario', 'colunas']
        read_only_fields = ['id', 'data_criacao', 'ultima_atualizacao', 'usuario']

    def validate(self, data):
        # Verifica se campos de somente leitura foram incluidos no payload
        for field in self.Meta.read_only_fields:
            if field in data:
                raise serializers.ValidationError({field: f'O campo `{field}` é somente leitura e não pode ser alterado.'})
            
        return data

