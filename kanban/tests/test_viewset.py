from rest_framework.test import APITestCase, APIClient
from usuario.models import Usuario
from rest_framework import status
from django.urls import reverse
from kanban.models import Kanban, KanbanColumnOrder, KanbanCard, KanbanColumn
from kanban.views import KanbanViewSet
from django.contrib.auth import get_user_model
from kanban.signals import criar_kanban_ao_criar_usuario
from django.db.models.signals import post_save

User = get_user_model()

class KanbanViewSetTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Criação de um usuário e Kanban para testes
        cls.usuario = Usuario.objects.create(username="testuser", password="testpassword")
        cls.kanban = Kanban.objects.create(nome="Kanban Teste", descricao="Descrição do Kanban de Teste", usuario=cls.usuario)

        # Criação de colunas e cards para o Kanban
        cls.coluna1 = KanbanColumn.objects.create(nome="Coluna 1", meta_dados={"descricao": "Primeira coluna"})
        cls.coluna2 = KanbanColumn.objects.create(nome="Coluna 2", meta_dados={"descricao": "Segunda coluna"})

        cls.kanban_column_order1 = KanbanColumnOrder.objects.create(kanban=cls.kanban, coluna=cls.coluna1, posicao=1)
        cls.kanban_column_order2 = KanbanColumnOrder.objects.create(kanban=cls.kanban, coluna=cls.coluna2, posicao=2)

        cls.card1 = KanbanCard.objects.create(lead_nome="Lead 1", descricao="Primeiro Card", coluna=cls.coluna1, data_prazo="2024-12-31")
        cls.card2 = KanbanCard.objects.create(lead_nome="Lead 2", descricao="Segundo Card", coluna=cls.coluna2, data_prazo="2024-12-31")

    def setUp(self):
        # Autentica o usuário para ser utilizado nos testes
        self.client = APIClient()
        self.client.force_authenticate(user=self.usuario)

    def test_retrieve_kanban(self):
        """
        Testa se o método retrieve retorna corretamente o Kanban do usuário.
        """
        url = reverse('kanban-detail', kwargs={'pk': self.usuario.id})
        response = self.client.get(url)
        #print(f'test_retrieve_kanban response.data: {response.data}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.kanban.nome)
        self.assertEqual(response.data['descricao'], self.kanban.descricao)
        self.assertEqual(response.data['usuario'], self.usuario.username)

    def test_retrieve_kanban_not_found(self):
        """
        Testa se o método retrieve retorna 404 quando o Kanban não é encontrado.
        """
        url = reverse('kanban-detail', kwargs={'pk': 9999})  # ID inexistente
        response = self.client.get(url)
        #print(f'test_retrieve_kanban_not_found response.data: {response.data}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_colunas_e_cards(self):
        """
        Testa se o método colunas_e_cards retorna as colunas e os cards associados ao Kanban do usuário.
        """
        url = reverse('kanban-colunas-e-cards', kwargs={'pk': self.usuario.id})
        response = self.client.get(url)
        print(f'test_colunas_e_cards response.data: {response.data}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        kanban_data = response.data['kanban']
        colunas_data = response.data['colunas']

        # Verificando os dados do Kanban
        self.assertEqual(kanban_data['id'], self.kanban.id)
        self.assertEqual(kanban_data['nome'], self.kanban.nome)

        # Verificando as colunas e seus cards
        self.assertEqual(len(colunas_data), 2)

        coluna1_data = colunas_data[0]
        self.assertEqual(coluna1_data['id'], self.coluna1.id)
        self.assertEqual(coluna1_data['nome'], self.coluna1.nome)
        self.assertEqual(len(coluna1_data['cards']), 1)
        self.assertEqual(coluna1_data['cards'][0]['lead_nome'], self.card1.lead_nome)

        coluna2_data = colunas_data[1]
        self.assertEqual(coluna2_data['id'], self.coluna2.id)
        self.assertEqual(coluna2_data['nome'], self.coluna2.nome)
        self.assertEqual(len(coluna2_data['cards']), 1)
        self.assertEqual(coluna2_data['cards'][0]['lead_nome'], self.card2.lead_nome)

    def test_colunas_e_cards_not_found(self):
        """
        Testa se o método colunas_e_cards retorna 404 quando o Kanban não é encontrado.
        """
        url = reverse('kanban-colunas-e-cards', kwargs={'pk': 9999})  # ID inexistente
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class KanbanColumnViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Desconecta o sinal para evitar a criação automática de Kanban ao criar o usuário
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=User)
        # Cria um usuário para autenticar nos testes
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        
        # Cria uma coluna para testes de atualização
        cls.kanban_column = KanbanColumn.objects.create(
            nome="Coluna Teste",
            meta_dados={"descricao": "Teste de coluna"},
            prazo_alerta=5,
            cor_inicial="#FFFFFF",
            cor_alerta="#FF0000"
        )

    def setUp(self):
        # Autentica o usuário para ser utilizado nos testes
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_kanban_column(self):
        """
        Testa a criação de uma nova coluna do Kanban.
        """
        data = {
            "nome": "Nova Coluna",
            "prazo_alerta": 3
        }
        url = reverse('kanban-column-list')
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], data['nome'])
        self.assertEqual(response.data['prazo_alerta'], data['prazo_alerta'])

    def test_update_nome_ou_prazo(self):
        """
        Testa a atualização do nome e do prazo_alerta de uma coluna existente.
        """
        data = {
            "nome": "Coluna Atualizada",
            "prazo_alerta": 10
        }
        url = reverse('kanban-column-atualizar-nome-ou-prazo', args=[self.kanban_column.id])
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], data['nome'])
        self.assertEqual(response.data['prazo_alerta'], data['prazo_alerta'])

    def test_partial_update_nome(self):
        """
        Testa a atualização parcial do nome de uma coluna existente.
        """
        data = {
            "nome": "Nome Parcialmente Atualizado"
        }
        url = reverse('kanban-column-atualizar-nome-ou-prazo', args=[self.kanban_column.id])
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], data['nome'])
        self.assertEqual(response.data['prazo_alerta'], self.kanban_column.prazo_alerta)

    def test_partial_update_prazo_alerta(self):
        """
        Testa a atualização parcial do prazo_alerta de uma coluna existente.
        """
        data = {
            "prazo_alerta": 15
        }
        url = reverse('kanban-column-atualizar-nome-ou-prazo', args=[self.kanban_column.id])
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['prazo_alerta'], data['prazo_alerta'])
        self.assertEqual(response.data['nome'], self.kanban_column.nome)


class KanbanColumnOrderViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Desconecta o sinal para evitar a criação automática de Kanban ao criar o usuário
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=User)
        # Cria um usuário para autenticar nos testes
        cls.user = Usuario.objects.create_user(username='testuser', password='testpassword')
        # Cria um Kanban para ser utilizado nos testes
        cls.kanban = Kanban.objects.create(nome="Kanban Teste", descricao="Descrição do Kanban de Teste", usuario=cls.user)
        # Cria duas colunas para o Kanban
        cls.kanban_column_1 = KanbanColumn.objects.create(nome="Coluna 1", prazo_alerta=5)
        cls.kanban_column_2 = KanbanColumn.objects.create(nome="Coluna 2", prazo_alerta=3)
        # Cria uma ordem inicial de colunas
        cls.kanban_column_order_1 = KanbanColumnOrder.objects.create(kanban=cls.kanban, coluna=cls.kanban_column_1, posicao=1)
        cls.kanban_column_order_2 = KanbanColumnOrder.objects.create(kanban=cls.kanban, coluna=cls.kanban_column_2, posicao=2)
        # Cria um card para a coluna 1
        cls.card_1 = KanbanCard.objects.create(lead_nome="Lead 1", descricao="Primeiro Card", coluna=cls.kanban_column_1)
        # Cria um card para a coluna 2
        cls.card_2 = KanbanCard.objects.create(lead_nome="Lead 2", descricao="Segundo Card", coluna=cls.kanban_column_1)

    def setUp(self):
        # Autentica o usuário para ser utilizado nos testes
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_kanban_column_order(self):
        """
        Testa a criação de uma nova ordem de coluna do Kanban.
        """
        data = {
            "kanban_id": self.kanban.id,
            "coluna_id": self.kanban_column_2.id,
            "posicao": 2
        }
        url = reverse('kanbancolumnorder-list')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['kanban_id'], data['kanban_id'])
        self.assertEqual(response.data['coluna_id'], data['coluna_id'])
        self.assertEqual(response.data['posicao'], data['posicao'])

    def test_update_kanban_column_order_posicao(self):
        """
        Testa a atualização da posição de uma coluna existente no Kanban.
        """
        data = {
            "kanban_id": self.kanban.id,
            "coluna_id": self.kanban_column_1.id,
            "posicao": 3
        }
        url = reverse('kanbancolumnorder-atualizar-posicao', args=[self.kanban_column_order_1.id])
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['posicao'], data['posicao'])

    def test_listar_colunas_kanban(self):
        """
        Testa a listagem de todas as colunas de um Kanban específico.
        """
        url = reverse('kanbancolumnorder-listar-colunas')
        response = self.client.get(url, {'kanban_id': self.kanban.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['kanban_id'], self.kanban.id)
        self.assertEqual(response.data[0]['coluna_id'], self.kanban_column_1.id)
        self.assertEqual(response.data[0]['posicao'], self.kanban_column_order_1.posicao)

    def test_listar_cards(self):
        """
        Testa a listagem de todos os cards de uma coluna específica.
        """
        url = reverse('kanbancolumnorder-listar-cards', args=[self.kanban_column_order_1.id])
        response = self.client.get(url)
        #print(f'test_listar_cards response {response.data}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['lead_nome'], "Lead 1")
        self.assertEqual(response.data[0]['descricao'], "Primeiro Card")

    def test_listar_cards_sem_cards(self):
        """
        Testa a listagem de todos os cards de uma coluna específica quando não há cards.
        """
        url = reverse('kanbancolumnorder-listar-cards', args=[self.kanban_column_order_2.id])
        response = self.client.get(url)
        #print(f'test_listar_cards_sem_cards response.data: {response.data}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


    def test_criar_coluna_e_ordem(self):
        """
        Testa a criação de uma nova coluna e sua respectiva ordem no Kanban.
        """
        data = {
            "kanban_id": self.kanban.id,
            "nome": "Nova Coluna",
            "prazo_alerta": 5,
            "posicao": 2
        }
        url = reverse('kanbancolumnorder-criar-coluna-e-ordem')
        response = self.client.post(url, data)
        #print(f'test_criar_coluna_e_ordem data: {response.data}')
        # Verifica se a resposta está correta
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('coluna', response.data)

        # Verifica se os dados da coluna estão corretos
        coluna_data = response.data['coluna']
        self.assertEqual(coluna_data['nome'], data['nome'])
        self.assertEqual(coluna_data['prazo_alerta'], data['prazo_alerta'])

        # verifica se a posicao está correta
        posicao = response.data['posicao']
        self.assertEqual(posicao, 2)


    def test_remover_coluna_sem_cards(self):
        """
        Testa a remoção de uma coluna que não possui cards.
        """
        url = reverse('kanbancolumnorder-remover-coluna', args=[self.kanban_column_order_2.id])
        response = self.client.delete(url)

        # Verifica se a coluna foi removida com sucesso
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(KanbanColumnOrder.DoesNotExist):
            KanbanColumnOrder.objects.get(pk=self.kanban_column_order_2.id)
        with self.assertRaises(KanbanColumn.DoesNotExist):
            KanbanColumn.objects.get(pk=self.kanban_column_2.id)

    def test_remover_coluna_com_cards(self):
        """
        Testa a tentativa de remover uma coluna que possui cards.
        """
        url = reverse('kanbancolumnorder-remover-coluna', args=[self.kanban_column_order_1.id])
        response = self.client.delete(url)

        # Verifica se a remoção foi impedida devido à presença de cards
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Existem cards nessa coluna. Remova ou mova os cards antes de excluir a coluna.')

        # Verifica se a coluna e a ordem ainda existem
        self.assertTrue(KanbanColumnOrder.objects.filter(pk=self.kanban_column_order_1.id).exists())
        self.assertTrue(KanbanColumn.objects.filter(pk=self.kanban_column_1.id).exists())