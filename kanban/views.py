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
        response_data = {
            "kanban": {
                "id": kanban.id,
                "nome": kanban.nome,
                "descricao": kanban.descricao,
                "ultima_atualizacao": kanban.ultima_atualizacao,
            },
            "colunas": [
                {
                    "id": coluna.coluna.id,
                    "nome": coluna.coluna.nome,
                    "posicao": coluna.posicao,
                    "prazo_alerta": coluna.coluna.prazo_alerta,
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

        #print(f'prazo_alerta: {request.data.get('prazo_alerta')}')

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

    @action(detail=False, methods=['post'])
    def criar_coluna_e_ordem(self, request):
        #import pdb
        #pdb.set_trace()
        """
        Cria uma nova coluna e depois cria a ordem da coluna no Kanban.
        Recebe o Nome da coluna, prazo de alerta, posição e ID do Kanban.
        """
        kanban_id = int(request.data.get('kanban_id'))
        nome_coluna = request.data.get('nome')
        prazo_alerta = int(request.data.get('prazo_alerta'))
        posicao = int(request.data.get('posicao'))
        
        # Verifica se os dados necessários foram fornecidos
        if not kanban_id or not nome_coluna or not prazo_alerta or not posicao:
            return Response({'error': 'Todos os campos são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        # Persistindo a nova coluna
        coluna_data = {
            'nome': nome_coluna,
            'prazo_alerta': prazo_alerta,
        }
        coluna_serializer = KanbanColumnSerializer(data=coluna_data)
        #coluna_serializer.is_valid(raise_exception=True)
        #coluna = coluna_serializer.save()
        if not coluna_serializer.is_valid():
            print("Erros do serializer de KanbanColumn:", coluna_serializer.errors)
            return Response(
                {'error': 'Erro ao validar os dados da coluna.', 'detalhes': coluna_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        coluna = coluna_serializer.save()

        # Criando a ordem da coluna no Kanban
        kanban_column_order_data = {
            'kanban_id': kanban_id,
            'coluna_id': coluna.id,
            'posicao': posicao,
        }
        kanban_column_order_serializer = KanbanColumnOrderSerializer(data=kanban_column_order_data)
        kanban_column_order_serializer.is_valid(raise_exception=True)
        kanban_column_order = kanban_column_order_serializer.save()

        # Retornando os dados das duas operações
        return Response({
            'coluna': coluna_serializer.data,
            'posicao': kanban_column_order_serializer.data['posicao'],
        }, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['delete'])
    def remover_coluna(self, request, pk=None):
        """
        Remove uma coluna específica do Kanban.
        Primeiro verifica se existem cards na coluna, e se houver, avisa o usuário que eles devem ser removidos ou movidos.
        """
        # Obtendo a instância de KanbanColumnOrder correspondente
        kanban_column = get_object_or_404(KanbanColumn, pk=pk)

        kanban_column_order = KanbanColumnOrder.objects.get(coluna=kanban_column)

        #print(f'remover_coluna pk: {pk}')

        # Verificando se há cards associados à coluna
        cards = KanbanCard.objects.filter(coluna=kanban_column_order.coluna)
        if cards.exists():
            return Response(
                {'error': 'Existem cards nessa coluna. Remova ou mova os cards antes de excluir a coluna.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se não houver cards, deletar KanbanColumnOrder e KanbanColumn
        KanbanColumnOrder.remover_coluna(kanban=kanban_column_order.kanban, coluna=kanban_column)
       

        return Response({'message': 'Coluna removida com sucesso.'}, status=status.HTTP_204_NO_CONTENT)
