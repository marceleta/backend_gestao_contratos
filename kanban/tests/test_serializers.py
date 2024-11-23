from rest_framework.test import APITestCase
from rest_framework.serializers import ValidationError
from kanban.serializers import KanbanSerializer, KanbanColumnSerializer, KanbanColumnOrderSerializer, KanbanCardSerializer
from kanban.models import Kanban, KanbanColumnOrder, KanbanColumn, KanbanCard
from usuario.models import Usuario
from kanban.signals import criar_kanban_ao_criar_usuario
from django.db.models.signals import post_save
from django.utils import timezone

class KanbanSerializerTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Criação de um usuário e Kanban para testes
        cls.usuario = Usuario.objects.create(username="testuser")
        cls.kanban = Kanban.objects.create(
            nome="Kanban Teste",
            descricao="Descrição do Kanban de Teste",
            usuario=cls.usuario
        )
        cls.coluna1 = KanbanColumn.objects.create(
            nome="Contato Inicial",
            meta_dados={"lead_nome": "Nome do lead", "descricao": "Descrição do lead"}
        )
        cls.coluna2 = KanbanColumn.objects.create(
            nome="Visita ao Imóvel",
            meta_dados={"data_visita": "Data da visita", "observacoes_visita": "Observações"}
        )
        KanbanColumnOrder.objects.create(kanban=cls.kanban, coluna=cls.coluna1, posicao=1)
        KanbanColumnOrder.objects.create(kanban=cls.kanban, coluna=cls.coluna2, posicao=2)

    def test_serializer_fields(self):
        """
        Testa se todos os campos esperados estão presentes no serializer.
        """
        serializer = KanbanSerializer(instance=self.kanban)
        data = serializer.data

        # Campos esperados no serializer
        expected_fields = {
            "id",
            "nome",
            "descricao",
            "data_criacao",
            "ultima_atualizacao",
            "usuario",
            "colunas"
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_colunas_serialization(self):
        """
        Testa se as colunas associadas ao Kanban são serializadas corretamente.
        """
        serializer = KanbanSerializer(instance=self.kanban)
        data = serializer.data

        #print(f'test_colunas_serialization data: {data}')

        self.assertEqual(len(data["colunas"]), 2)  # Deve conter duas colunas
        self.assertEqual(data["colunas"][0]['coluna_id'], self.coluna1.id)
        self.assertEqual(data["colunas"][0]["kanban_id"], self.kanban.id)

    def test_usuario_field(self):
        """
        Testa se o campo `usuario` retorna o nome do usuário corretamente.
        """
        serializer = KanbanSerializer(instance=self.kanban)
        data = serializer.data

        self.assertEqual(data["usuario"], "testuser")

    def test_read_only_fields(self):
        """
        Testa se os campos `id`, `data_criacao`, `ultima_atualizacao` e `usuario` são de leitura apenas.
        """
        payload = {
            "id": 999,
            "nome": "Kanban Alterado",
            "descricao": "Nova descrição",
            "data_criacao": "2024-11-19T12:00:00Z",
            "ultima_atualizacao": "2024-11-19T13:00:00Z",
            "usuario": "alterado"
        }
        serializer = KanbanSerializer(instance=self.kanban, data=payload, partial=True)

        serializer.is_valid(raise_exception=True)
        updated_kanban = serializer.save()

        # Verifica que os campos de leitura não foram alterados
        self.assertNotEqual(updated_kanban.id, payload["id"], "O campo `id` não deve ser alterável.")
        self.assertNotEqual(updated_kanban.data_criacao, payload["data_criacao"], "O campo `data_criacao` não deve ser alterável.")
        self.assertNotEqual(updated_kanban.ultima_atualizacao, payload["ultima_atualizacao"], "O campo `ultima_atualizacao` não deve ser alterável.")
        self.assertNotEqual(updated_kanban.usuario.username, payload["usuario"], "O campo `usuario` não deve ser alterável.")


class KanbanColumnSerializerTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Cria uma instância KanbanColumn para ser usada nos testes
        cls.kanban_column = KanbanColumn.objects.create(
            nome="Contato Inicial",
            meta_dados={"descricao": "Lead inicial"},
            prazo_alerta=3,
            cor_inicial="#FFFFFF",
            cor_alerta="#FF0000"
        )

    def test_serializer_fields(self):
        """
        Testa se todos os campos esperados estão presentes no serializer.
        """
        serializer = KanbanColumnSerializer(instance=self.kanban_column)
        data = serializer.data

        # Campos esperados no serializer
        expected_fields = {
            'id', 'nome', 'meta_dados', 'prazo_alerta', 'cor_inicial', 'cor_alerta'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_read_only_field_id(self):
            """
            Testa se o campo `id` é de somente leitura.
            """
            payload = {
                "id": 999,
                "nome": "Coluna Alterada",
                "meta_dados": {"descricao": "Lead alterado"},
                "prazo_alerta": 5,
                "cor_inicial": "#000000",
                "cor_alerta": "#00FF00"
            }
            serializer = KanbanColumnSerializer(instance=self.kanban_column, data=payload, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_kanban = serializer.save()

            # Verifica que o campo `id` não foi alterado
            self.assertEqual(updated_kanban.id, self.kanban_column.id, "O campo `id` não deve ser alterável.")


    def test_valid_serialization(self):
        """
        Testa se a serialização de uma instância KanbanColumn ocorre corretamente.
        """
        serializer = KanbanColumnSerializer(instance=self.kanban_column)
        data = serializer.data

        self.assertEqual(data['id'], self.kanban_column.id)
        self.assertEqual(data['nome'], self.kanban_column.nome)
        self.assertEqual(data['meta_dados'], self.kanban_column.meta_dados)
        self.assertEqual(data['prazo_alerta'], self.kanban_column.prazo_alerta)
        self.assertEqual(data['cor_inicial'], self.kanban_column.cor_inicial)
        self.assertEqual(data['cor_alerta'], self.kanban_column.cor_alerta)

    def test_valid_deserialization(self):
        """
        Testa se a desserialização e a criação de uma nova instância KanbanColumn ocorrem corretamente.
        """
        payload = {
            "nome": "Nova Coluna",
            "meta_dados": {"descricao": "Novo lead"},
            "prazo_alerta": 7,
            "cor_inicial": "#123456",
            "cor_alerta": "#654321"
        }
        serializer = KanbanColumnSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
        kanban_column = serializer.save()

        self.assertEqual(kanban_column.nome, payload['nome'])
        self.assertEqual(kanban_column.meta_dados, payload['meta_dados'])
        self.assertEqual(kanban_column.prazo_alerta, payload['prazo_alerta'])
        self.assertEqual(kanban_column.cor_inicial, payload['cor_inicial'])
        self.assertEqual(kanban_column.cor_alerta, payload['cor_alerta'])

    def test_invalid_deserialization(self):
        """
        Testa a validação do serializer ao enviar dados inválidos.
        """
        payload = {
            "nome": "",  # Nome não deve ser vazio
            "meta_dados": {},  # Meta_dados deve ser um dicionário não vazio
            "prazo_alerta": -1,  # Prazo alerta não deve ser negativo
            "cor_inicial": "123",  # Cor deve ser um código hexadecimal válido
            "cor_alerta": "xyz"
        }
        serializer = KanbanColumnSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        #print(f'test_invalid_deserialization serializer.errors: {serializer.errors}')
        self.assertIn('nome', serializer.errors)
        self.assertIn('prazo_alerta', serializer.errors)
        self.assertIn('cor_inicial', serializer.errors)
        self.assertIn('cor_alerta', serializer.errors)


class KanbanColumnOrderSerializerTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Criação de um usuário e Kanban para testes
        cls.usuario = Usuario.objects.create(username="testuser")
        # Cria uma instância Kanban para ser usada nos testes
        cls.kanban = Kanban.objects.create(nome="Kanban Teste", descricao="Descrição do Kanban de Teste", usuario=cls.usuario)
        # Cria uma instância KanbanColumn para ser usada nos testes
        cls.kanban_column = KanbanColumn.objects.create(
            nome="Contato Inicial",
            meta_dados={"descricao": "Lead inicial"},
            prazo_alerta=3,
            cor_inicial="#FFFFFF",
            cor_alerta="#FF0000"
        )
        cls.kanban_column_order = KanbanColumnOrder.objects.create(
            kanban=cls.kanban,
            coluna=cls.kanban_column,
            posicao=1
        )

    def test_serializer_fields(self):
        """
        Testa se todos os campos esperados estão presentes no serializer.
        """
        serializer = KanbanColumnOrderSerializer(instance=self.kanban_column_order)
        data = serializer.data
        #print(f'test_serializer_fields data: {data}')
        # Campos esperados no serializer
        expected_fields = {
            'id', 'kanban_id', 'coluna_id', 'posicao'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_valid_serialization(self):
        """
        Testa se a serialização de uma instância KanbanColumnOrder ocorre corretamente.
        """
        serializer = KanbanColumnOrderSerializer(instance=self.kanban_column_order)
        data = serializer.data
        #print(f'test_valid_serialization data: {data}')

        self.assertEqual(data['id'], self.kanban_column_order.id)
        self.assertEqual(data['coluna_id'], self.kanban_column.id)
        self.assertEqual(data['kanban_id'], self.kanban.id)
        self.assertEqual(data['posicao'], self.kanban_column_order.posicao)

    def test_valid_deserialization(self):
        """
        Testa se a desserialização e a criação de uma nova instância KanbanColumnOrder ocorrem corretamente.
        """
        usuario2 = Usuario.objects.create(username="testuser 2")
        kanban = Kanban.objects.create(nome="Kanban Teste 2", descricao="Descrição do Kanban de Teste 2", usuario=usuario2)
        # Cria uma instância KanbanColumn para ser usada nos testes
        kanban_column = KanbanColumn.objects.create(
            nome="Contato Inicial",
            meta_dados={"descricao": "Lead inicial"},
            prazo_alerta=3,
            cor_inicial="#FFFFFF",
            cor_alerta="#FF0000"
        )
        payload = {
            "coluna_id": kanban_column.id,
            "posicao": 2,
            "kanban_id": kanban.id
        }
        serializer = KanbanColumnOrderSerializer(data=payload)
        if not serializer.is_valid():
            print(f'test_valid_deserialization data: {serializer.errors}')
        self.assertTrue(serializer.is_valid())
        kanban_column_order = serializer.save()

        self.assertEqual(kanban_column_order.coluna, kanban_column)
        self.assertEqual(kanban_column_order.posicao, payload['posicao'])


class KanbanCardSerializerTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Cria uma instância KanbanColumn para ser usada nos testes
        cls.kanban_column = KanbanColumn.objects.create(
            nome="Contato Inicial",
            meta_dados={"descricao": "Lead inicial"},
            prazo_alerta=3,
            cor_inicial="#FFFFFF",
            cor_alerta="#FF0000"
        )
        
        # Cria uma instância KanbanCard para ser usada nos testes
        cls.kanban_card = KanbanCard.objects.create(
            lead_nome="Lead Teste",
            descricao="Descrição do lead teste",
            data_prazo=timezone.now() + timezone.timedelta(days=7),
            coluna=cls.kanban_column
        )

    def test_serializer_fields(self):
        """
        Testa se todos os campos esperados estão presentes no serializer.
        """
        serializer = KanbanCardSerializer(instance=self.kanban_card)
        data = serializer.data

        # Campos esperados no serializer
        expected_fields = {
            'id', 'lead_nome', 'descricao', 'data_criacao', 'ultima_atualizacao',
            'data_prazo', 'cor_atual', 'dados_adicionais', 'coluna'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_read_only_fields(self):
        """
        Testa se os campos `id`, `data_criacao`, `ultima_atualizacao` e `cor_atual` são de somente leitura.
        """
        payload = {
            "id": 999,
            "lead_nome": "Lead Alterado",
            "descricao": "Descrição alterada",
            "data_criacao": "2024-11-19T12:00:00Z",
            "ultima_atualizacao": "2024-11-19T13:00:00Z",
            "cor_atual": "#123456",
            "data_prazo": timezone.now() + timezone.timedelta(days=10),
            "coluna": self.kanban_column.id
        }
        serializer = KanbanCardSerializer(instance=self.kanban_card, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_kanban_card = serializer.save()

        # Verifica que os campos de leitura não foram alterados
        self.assertEqual(updated_kanban_card.id, self.kanban_card.id, "O campo `id` não deve ser alterável.")
        self.assertEqual(updated_kanban_card.data_criacao, self.kanban_card.data_criacao, "O campo `data_criacao` não deve ser alterável.")
        self.assertEqual(updated_kanban_card.ultima_atualizacao, self.kanban_card.ultima_atualizacao, "O campo `ultima_atualizacao` não deve ser alterável.")
        self.assertEqual(updated_kanban_card.cor_atual, self.kanban_card.cor_atual, "O campo `cor_atual` não deve ser alterável.")

    def test_valid_serialization(self):
        """
        Testa se a serialização de uma instância KanbanCard ocorre corretamente.
        """
        serializer = KanbanCardSerializer(instance=self.kanban_card)
        data = serializer.data

        self.assertEqual(data['id'], self.kanban_card.id)
        self.assertEqual(data['lead_nome'], self.kanban_card.lead_nome)
        self.assertEqual(data['descricao'], self.kanban_card.descricao)
        self.assertEqual(data['data_criacao'], self.kanban_card.data_criacao.isoformat())
        self.assertEqual(data['ultima_atualizacao'], self.kanban_card.ultima_atualizacao.isoformat())
        self.assertEqual(data['data_prazo'], self.kanban_card.data_prazo.isoformat())
        self.assertEqual(data['cor_atual'], self.kanban_card.cor_atual)
        self.assertEqual(data['coluna'], self.kanban_card.coluna.id)

    def test_valid_deserialization(self):
        """
        Testa se a desserialização e a criação de uma nova instância KanbanCard ocorrem corretamente.
        """
        payload = {
            "lead_nome": "Novo Lead",
            "descricao": "Descrição do novo lead",
            "data_prazo": timezone.now() + timezone.timedelta(days=5),
            "coluna": self.kanban_column.id
        }
        serializer = KanbanCardSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
        kanban_card = serializer.save()

        self.assertEqual(kanban_card.lead_nome, payload['lead_nome'])
        self.assertEqual(kanban_card.descricao, payload['descricao'])
        self.assertEqual(kanban_card.data_prazo, payload['data_prazo'])
        self.assertEqual(kanban_card.coluna, self.kanban_column)

    def test_invalid_deserialization(self):
        """
        Testa a validação do serializer ao enviar dados inválidos.
        """
        payload = {
            "lead_nome": "",  # Lead_nome não deve ser vazio
            "data_prazo": "data inválida",  # Data_prazo deve ser uma data válida
            "coluna": "coluna inválida"  # Coluna deve ser um ID válido
        }
        serializer = KanbanCardSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('lead_nome', serializer.errors)
        self.assertIn('data_prazo', serializer.errors)
        self.assertIn('coluna', serializer.errors)