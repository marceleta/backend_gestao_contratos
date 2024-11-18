from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .models import Kanban, KanbanCard, KanbanColumnOrder
from .serializers import KanbanSerializer, KanbanCardSerializer, KanbanColumnSerializer
from .models import AbstractKanbanColumn
from django.contrib.contenttypes.models import ContentType

class KanbanViewSet(viewsets.ViewSet):
    """ViewSet para recuperar o Kanban do usuário autenticado."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            kanban = Kanban.objects.get(usuario=request.user)
            serializer = KanbanSerializer(kanban)
            return Response(serializer.data)
        except Kanban.DoesNotExist:
            return Response({"error": "Kanban não encontrado."}, status=status.HTTP_404_NOT_FOUND)


class KanbanCardViewSet(viewsets.ModelViewSet):
    """ViewSet para criar e atualizar KanbanCards."""
    queryset = KanbanCard.objects.all()
    serializer_class = KanbanCardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        object_id = self.request.data.get('object_id')

        try:
            coluna_content_type = ContentType.objects.get(id=self.request.data.get('content_type'))
            coluna_model = coluna_content_type.model_class()

            # Verifica se a coluna é válida e implementa AbstractKanbanColumn
            if not issubclass(coluna_model, AbstractKanbanColumn):
                raise ValidationError("A coluna deve ser um modelo que implementa AbstractKanbanColumn.")

            # Recupera a instância da coluna
            coluna = coluna_model.objects.get(id=object_id)

            # Salva o card associado à coluna
            serializer.save(content_type=coluna_content_type, object_id=coluna.id)
        except ContentType.DoesNotExist:
            raise ValidationError({"content_type": "Tipo de conteúdo inválido."})
        except coluna_model.DoesNotExist:
            raise ValidationError({"object_id": "Coluna não encontrada."})


    def perform_update(self, serializer):
        object_id = self.request.data.get('object_id')
        content_type_id = self.request.data.get('content_type')

        try:
            if object_id and content_type_id:  # Apenas valida se esses campos foram fornecidos
                coluna_content_type = ContentType.objects.get(id=content_type_id)
                coluna_model = coluna_content_type.model_class()

                # Verifica se a coluna é válida e implementa AbstractKanbanColumn
                if not issubclass(coluna_model, AbstractKanbanColumn):
                    raise serializers.ValidationError(
                        {"content_type": "A coluna deve ser um modelo que implementa AbstractKanbanColumn."}
                    )

                # Recupera a instância da coluna
                coluna = coluna_model.objects.get(id=object_id)

                # Aplica os dados do serializer antes da validação
                serializer.is_valid(raise_exception=True)
                card = serializer.save()

                # Valida os campos obrigatórios para a nova coluna
                coluna.validar_campos(card)

                # Atualiza o card associado à nova coluna
                serializer.save(content_type=coluna_content_type, object_id=coluna.id, partial=True)
            else:
                # Atualização parcial sem alterar `object_id` ou `content_type`
                serializer.save(partial=True)

        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"content_type": ["Tipo de conteúdo inválido."]})
        except coluna_model.DoesNotExist:
            raise serializers.ValidationError({"object_id": ["Coluna não encontrada."]})
        except ValidationError as e:
            raise serializers.ValidationError({"detalhes_validacao": e.messages})



class KanbanColumnViewSet(viewsets.ViewSet):
    """ViewSet para criar novas colunas no Kanban."""
    permission_classes = [IsAuthenticated]

    def create(self, request):
        kanban_id = request.data.get('kanban_id')
        nome = request.data.get('nome')
        prazo_alerta = request.data.get('prazo_alerta')
        posicao = request.data.get('posicao', None)

        if not all([kanban_id, nome, prazo_alerta]):
            return Response({"error": "Campos obrigatórios: kanban_id, nome, prazo_alerta."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            kanban = Kanban.objects.get(id=kanban_id, usuario=request.user)
        except Kanban.DoesNotExist:
            return Response({"error": "Kanban não encontrado ou não pertence ao usuário."}, 
                            status=status.HTTP_404_NOT_FOUND)
        

        # Define a posição padrão caso não seja fornecida
        if posicao is None:
            posicao = kanban.colunas.count() + 1

        # Cria uma nova coluna estendendo AbstractKanbanColumn
        column_data = {
            'nome': nome,
            'prazo_alerta': prazo_alerta
        }
        column_class = type(f"{nome.replace(' ', '')}Column", (AbstractKanbanColumn,), {})
        new_column = column_class.objects.create(**column_data)

        # Adiciona a coluna ao Kanban
        column_order = KanbanColumnOrder.objects.create(
            kanban=kanban,
            coluna_content_type=ContentType.objects.get_for_model(column_class),
            coluna_object_id=new_column.id,
            posicao=posicao
        )

         # Retorna informações detalhadas da nova coluna
        return Response(
            {
                "success": "Coluna criada com sucesso.",
                "coluna": {
                    "id": new_column.id,
                    "nome": new_column.nome,
                    "posicao": column_order.posicao
                }
            },
            status=status.HTTP_201_CREATED
        )