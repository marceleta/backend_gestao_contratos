from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Kanban, KanbanColumnOrder, KanbanCard, KanbanColumn
from .serializers import KanbanSerializer, KanbanColumnSerializer, KanbanColumnOrderSerializer, KanbanCardSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class KanbanViewSet(viewsets.ViewSet):

    """
    ViewSet para retornar as informações do Kanban de um usuário específico,
    incluindo as colunas associadas e os cards de cada coluna.
    """

    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, pk=None):
        # Obtém o usuário pelo ID (`pk` recebido na URL)
        user = get_object_or_404(User, pk=pk)

        # Obtém o Kanban associado ao usuário
        kanban = get_object_or_404(Kanban, usuario=user)

        # Serializa o Kanban, incluindo as colunas e os cards
        serializer = KanbanSerializer(kanban)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def colunas_e_cards(self, request, pk=None):
        """
        Endpoint para retornar as colunas e os cards associados ao Kanban do usuário.
        """
        user = get_object_or_404(User, pk=pk)

        # Obtém o Kanban associado ao usuário
        kanban = get_object_or_404(Kanban, usuario=user)

        # Otimiza a consulta para buscar todas as colunas e os cards relacionados
        colunas = KanbanColumnOrder.objects.filter(kanban=kanban).select_related('coluna')
        cards = KanbanCard.objects.filter(coluna__in=[coluna.coluna for coluna in colunas])

        # Monta a resposta com informações do Kanban, colunas e cards
        #print(f'KanbanSerializer(kanban).data[kanban]: {KanbanSerializer(kanban).data}')
        response_data = {
            "kanban": {
                'id': KanbanSerializer(kanban).data['id'],
                'nome': KanbanSerializer(kanban).data['nome'],
                'descricao': KanbanSerializer(kanban).data['descricao'],
                'ultima_atualizacao': KanbanSerializer(kanban).data['ultima_atualizacao'],

            },
            
            "colunas": [
                {
                    "coluna": {
                        "id": coluna.coluna.id,
                        "nome": coluna.coluna.nome,
                        "posicao": coluna.posicao,
                        "cards": [
                            {
                                "id": card.id,
                                "lead_nome": card.lead_nome,
                                "descricao": card.descricao,
                                "data_prazo": card.data_prazo,
                                "cor_atual": card.cor_atual
                            }
                            for card in cards if card.coluna.id == coluna.coluna.id
                    ]
                    },
                    
                }
                for coluna in colunas
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class KanbanColumnViewSet(viewsets.ModelViewSet):
    """
    ViewSet para criar e atualizar colunas do Kanban.
    """
    queryset = KanbanColumn.objects.all()
    serializer_class = KanbanColumnSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Cria uma nova coluna do Kanban.
        Os campos exigidos são `nome` e `prazo_alerta`.
        """
        # Somente `nome` e `prazo_alerta` são requeridos na criação
        data = {
            'nome': request.data.get('nome'),
            'prazo_alerta': request.data.get('prazo_alerta'),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def atualizar_nome_ou_prazo(self, request, pk=None):
        """
        Atualiza o `nome` ou o `prazo_alerta` da coluna.
        """
        # Obtém a coluna pelo ID (`pk` recebido na URL)
        coluna = get_object_or_404(KanbanColumn, pk=pk)

        # Atualização parcial permitida para `nome` ou `prazo_alerta`
        data = {}
        if 'nome' in request.data:
            data['nome'] = request.data['nome']
        if 'prazo_alerta' in request.data:
            data['prazo_alerta'] = request.data['prazo_alerta']

        serializer = self.get_serializer(coluna, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class KanbanColumnOrderViewSet(viewsets.ViewSet):
    """
    ViewSet para criar, atualizar e listar colunas de um Kanban.
    """
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Cria uma nova ordem de coluna do Kanban.
        Recebe um ID de Kanban, um ID de coluna e uma posição.
        """
        data = {
            'kanban_id': request.data.get('kanban_id'),
            'coluna_id': request.data.get('coluna_id'),
            'posicao': request.data.get('posicao'),
        }
        serializer = KanbanColumnOrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['patch'])
    def atualizar_posicao(self, request, pk=None):
        """
        Atualiza a posição de uma coluna.
        Recebe um ID de Kanban, um ID de coluna e uma nova posição.
        """
        kanban_column_order = get_object_or_404(KanbanColumnOrder, pk=pk)

        data = {
            'kanban_id': request.data.get('kanban_id'),
            'coluna_id': request.data.get('coluna_id'),
            'posicao': request.data.get('posicao'),
        }
        serializer = KanbanColumnOrderSerializer(kanban_column_order, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def listar_colunas(self, request):
        """
        Lista todas as colunas de um Kanban.
        Recebe um ID de Kanban.
        """
        kanban_id = request.query_params.get('kanban_id')
        kanban = get_object_or_404(Kanban, pk=kanban_id)
        colunas = KanbanColumnOrder.objects.filter(kanban=kanban)
        serializer = KanbanColumnOrderSerializer(colunas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def listar_cards(self, request, pk=None):
        """
        Lista todos os cards de uma coluna específica.
        Recebe um ID de coluna.
        """
        coluna = get_object_or_404(KanbanColumnOrder, pk=pk)
        cards = KanbanCard.objects.filter(coluna=coluna.coluna)
        serializer = KanbanCardSerializer(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

