from rest_framework.exceptions import ValidationError
from usuario.models import Usuario
from django.test import TestCase
from kanban.serializers import KanbanSerializer, KanbanCardSerializer, KanbanColumnSerializer
from kanban.models import Kanban, KanbanCard, KanbanColumnOrder, ContatoInicialColumn
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from kanban.signals import criar_kanban_ao_criar_usuario
from django.db.models.signals import post_save

User = get_user_model()

class KanbanCardSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        cls.user = User.objects.create_user(username="testuser", password="123456")
        cls.kanban, _ = Kanban.objects.get_or_create(
            nome="Kanban Teste", descricao="Teste de Kanban", usuario=cls.user
        )

        cls.column = ContatoInicialColumn.objects.create(nome='Contato Inicial')

        cls.column_order = KanbanColumnOrder.objects.create(
            kanban=cls.kanban,
            coluna_content_type=ContentType.objects.get_for_model(ContatoInicialColumn),
            coluna_object_id=cls.column.id,
            posicao=1
        )
        cls.card_data = {
            'lead_nome': 'Lead Test',
            'descricao': 'Descrição do teste',
            'content_type': ContentType.objects.get_for_model(ContatoInicialColumn),
            'object_id': cls.column.id,
            'cor_atual': '#00FF00',
        }
        #print(str(cls.card_data))
        cls.card = KanbanCard.objects.create(**cls.card_data)

    def test_card_serialization(self):
        serializer = KanbanCardSerializer(self.card)
        self.assertEqual(serializer.data['lead_nome'], self.card_data['lead_nome'])
        self.assertEqual(serializer.data['descricao'], self.card_data['descricao'])

    def test_card_deserialization(self):
        self.card_data['content_type'] = ContentType.objects.get_for_model(ContatoInicialColumn).id
        serializer = KanbanCardSerializer(data=self.card_data)
        if not serializer.is_valid():
            print(str(serializer.errors))
        self.assertTrue(serializer.is_valid())
        card = serializer.save()
        self.assertEqual(card.lead_nome, self.card_data['lead_nome'])

    def test_card_invalid_data(self):
        invalid_data = self.card_data.copy()
        invalid_data['cor_atual'] = 'invalid_color'
        serializer = KanbanCardSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cor_atual', serializer.errors)


class KanbanColumnSerializerTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        cls.user = User.objects.create_user(username="testuser", password="123456")
        cls.kanban = Kanban.objects.create(nome="Kanban Teste", usuario=cls.user)
        cls.abstract_column_instance = ContatoInicialColumn.objects.create(nome="Contato Inicial")
        
        cls.column_order = KanbanColumnOrder.objects.create(
            kanban=cls.kanban,
            coluna_content_type=ContentType.objects.get_for_model(ContatoInicialColumn),
            coluna_object_id=cls.abstract_column_instance.id,
            posicao=1
        )

    def test_column_serialization(self):
        serializer = KanbanColumnSerializer(self.column_order)
        #print(str(serializer.data))
        self.assertEqual(serializer.data['coluna'].id, self.abstract_column_instance.id)
        

    def test_column_representation(self):
        serializer = KanbanColumnSerializer(self.column_order)
        representation = serializer.data
        #print(str(representation['coluna'].nome))
        self.assertIn('Contato Inicial', representation['coluna'].nome)


class KanbanSerializerTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        cls.user = User.objects.create_user(username="testuser", password="123456")
        cls.kanban_data = {
            'nome': 'Kanban Teste',
            'descricao': 'Teste de kanban',
            'usuario': cls.user.id,
        }
        cls.kanban = Kanban.objects.create(
            nome=cls.kanban_data['nome'],
            descricao=cls.kanban_data['descricao'],
            usuario=cls.user
        )

    def test_kanban_serialization(self):
        serializer = KanbanSerializer(self.kanban)
        self.assertEqual(serializer.data['nome'], self.kanban_data['nome'])
        self.assertEqual(serializer.data['descricao'], self.kanban_data['descricao'])
        self.assertEqual(serializer.data['usuario'], self.user.id)

    def test_kanban_deserialization(self):
        serializer = KanbanSerializer(data=self.kanban_data)
        self.assertTrue(serializer.is_valid())
        kanban = serializer.save()
        self.assertEqual(kanban.nome, self.kanban_data['nome'])
        self.assertEqual(kanban.usuario, self.user)

    def test_kanban_create_existing_user(self):
        serializer = KanbanSerializer(data=self.kanban_data)
        self.assertTrue(serializer.is_valid())
        kanban = serializer.save()
        self.assertEqual(kanban, self.kanban)
