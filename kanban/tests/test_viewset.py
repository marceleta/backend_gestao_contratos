from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
from usuario.models import Usuario
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from kanban.models import Kanban, KanbanCard, ContatoInicialColumn, VisitaImovelColumn
from kanban.serializers import KanbanCardSerializer
from kanban.signals import criar_kanban_ao_criar_usuario
from django.db.models.signals import post_save
from kanban.models import Kanban, KanbanColumnOrder, AbstractKanbanColumn

User = get_user_model()

class KanbanCardViewSetTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Criação de dados reutilizáveis
        cls.user = User.objects.create_user(username="testuser", password="123456")
        cls.kanban = Kanban.objects.create(usuario=cls.user, nome="Kanban Teste")
        cls.coluna = ContatoInicialColumn.objects.create(nome="Contato Inicial")
        cls.coluna_content_type = ContentType.objects.get_for_model(ContatoInicialColumn)
        
        cls.card_data = {
            'lead_nome': 'Lead Teste',
            'descricao': 'Descrição do teste',
            'content_type': cls.coluna_content_type.id,
            'object_id': cls.coluna.id,
        }

    def setUp(self):
        # Inicializa o cliente autenticado para cada teste
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_create_kanban_card(self):
        response = self.client.post('/api/v1/kanbancards/', data=self.card_data)
        #print('test_create_kanban_card: '+str(response.json()))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KanbanCard.objects.count(), 1)
        self.assertEqual(response.data['lead_nome'], self.card_data['lead_nome'])


    def test_create_kanban_card_invalid_column(self):
        invalid_data = self.card_data.copy()
        invalid_data['object_id'] = 999  # Coluna inexistente

        with self.assertRaises(ValidationError) as context:
            self.client.post('/api/v1/kanbancards/', data=invalid_data)

        # Verifica o conteúdo da exceção capturada
        exception = context.exception
        #print(f'test_create_kanban_card_invalid_column: {exception}')
        self.assertIn('object_id', exception.message_dict)
        self.assertEqual(exception.message_dict['object_id'][0], "Coluna não encontrada.")

    def test_partial_update_kanban_card(self):
        # Cria um card inicial
        card = KanbanCard.objects.create(
            lead_nome="Lead Original",
            content_type=self.coluna_content_type,
            object_id=self.coluna.id
        )
        partial_data = {'lead_nome': 'Novo Lead'}
        response = self.client.patch(f'/api/v1/kanbancards/{card.id}/', data=partial_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        card.refresh_from_db()
        self.assertEqual(card.lead_nome, partial_data['lead_nome'])

    def test_update_column_with_validation(self):
        # Cria um card inicial
        card = KanbanCard.objects.create(
            lead_nome="Lead Original",
            content_type=self.coluna_content_type,
            object_id=self.coluna.id
        )
        new_column = VisitaImovelColumn.objects.create(nome="Nova Coluna")
        update_data = {
            'object_id': new_column.id,
            'content_type': ContentType.objects.get_for_model(VisitaImovelColumn).id
        }

        # Faz a requisição de atualização
        response = self.client.patch(f'/api/v1/kanbancards/{card.id}/', data=update_data)
        #print(f'test_update_column_with_validation: {response.data}')

        # Verifica que a resposta tem status 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verifica que a chave 'detalhes_validacao' está presente na resposta
        self.assertIn('detalhes_validacao', response.data)

        # Verifica o conteúdo de 'detalhes_validacao'
        erros = response.data['detalhes_validacao']
        self.assertIn("O campo 'data_visita' (Data e hora da visita agendada) é obrigatório para esta coluna.", erros)
        self.assertIn("O campo 'observacoes_visita' (Observações sobre a visita) é obrigatório para esta coluna.", erros)

    
    def test_update_column_with_success(self):
        # Cria um card inicial
        card = KanbanCard.objects.create(
            lead_nome="Lead Original",
            content_type=self.coluna_content_type,
            object_id=self.coluna.id
        )
        new_column = VisitaImovelColumn.objects.create(nome="Nova Coluna")
        update_data = {
            'object_id': new_column.id,
            'content_type': ContentType.objects.get_for_model(VisitaImovelColumn).id,
            'data_visita': '2024-11-20T10:30:00Z',
            'observacoes_visita': 'Visita agendada com sucesso.'
        }

        # Faz a requisição de atualização
        response = self.client.patch(f'/api/v1/kanbancards/{card.id}/', data=update_data)
        #print(f'test_update_column_with_success: {response.data}')

        # Verifica que a resposta tem status 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Atualiza o objeto card do banco de dados
        card.refresh_from_db()

        # Verifica se os campos foram atualizados corretamente
        self.assertEqual(card.object_id, new_column.id)
        self.assertEqual(card.data_visita.isoformat(), '2024-11-20T10:30:00+00:00')
        self.assertEqual(card.observacoes_visita, 'Visita agendada com sucesso.')


    def test_permissions_for_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get('/api/v1/kanbancards/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class KanbanColumnViewSetTest(APITestCase):
    
    def setUp(self):
        """Configuração inicial para os testes."""
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        # Cria um Kanban para o usuário
        self.kanban = Kanban.objects.create(nome="Test Kanban", usuario=self.user)

    def test_create_column_with_valid_data(self):
        """Testa criação de coluna com dados válidos."""
        data = {
            "kanban_id": self.kanban.id,
            "nome": "Nova Coluna",
            "prazo_alerta": 5,
            "posicao": 1
        }
        response = self.client.post("/api/v1/kanban/columns/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("coluna", response.data)
        self.assertEqual(response.data["coluna"]["posicao"], 1)

    def test_create_column_without_position(self):
        """Testa criação de coluna sem fornecer a posição."""
        data = {
            "kanban_id": self.kanban.id,
            "nome": "Coluna Sem Posição",
            "prazo_alerta": 3
        }
        response = self.client.post("/api/v1/kanban/columns/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["coluna"]["posicao"], 1)

    def test_create_column_with_existing_position(self):
        """Testa criação de coluna em uma posição existente."""

         # Cria uma coluna fictícia
        column_class = type("TesteColumn", (AbstractKanbanColumn,),  {"__module__": AbstractKanbanColumn.__module__} )
        coluna = column_class.objects.create(nome="Coluna Teste", prazo_alerta=3)

        # Recupera o ContentType da coluna fictícia
        coluna_content_type = ContentType.objects.get_for_model(column_class)
        # Cria uma coluna inicial na posição 1
        KanbanColumnOrder.objects.create(
            kanban=self.kanban,
            coluna_content_type=coluna_content_type, 
            coluna_object_id=1,
            posicao=1
        )
        data = {
            "kanban_id": self.kanban.id,
            "nome": "Coluna na Mesma Posição",
            "prazo_alerta": 4,
            "posicao": 1
        }
        response = self.client.post("/api/v1/kanban/columns/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica que as posições foram ajustadas
        colunas = KanbanColumnOrder.objects.filter(kanban=self.kanban).order_by("posicao")
        self.assertEqual(colunas.count(), 2)
        self.assertEqual(colunas[0].posicao, 1)
        self.assertEqual(colunas[1].posicao, 2)

    def test_missing_required_fields(self):
        """Testa criação sem campos obrigatórios."""
        data = {
            "kanban_id": self.kanban.id,
            "nome": "Faltando Prazos"
        }
        response = self.client.post("/api/v1/kanban/columns/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("prazo_alerta", response.data["error"])

    def test_create_column_for_invalid_kanban(self):
        """Testa criação para um Kanban inexistente ou não pertencente ao usuário."""
        data = {
            "kanban_id": 999,  # Kanban inexistente
            "nome": "Coluna Inválida",
            "prazo_alerta": 2
        }
        response = self.client.post("/api/v1/kanban/columns/", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_create_column(self):
        """Testa que usuários não autenticados não podem criar colunas."""
        self.client.logout()
        data = {
            "kanban_id": self.kanban.id,
            "nome": "Coluna Sem Login",
            "prazo_alerta": 3
        }
        response = self.client.post("/api/v1/kanban/columns/", data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

