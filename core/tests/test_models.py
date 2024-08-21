from django.test import TestCase
from core.models import Estado, Telefone
from django.contrib.contenttypes.models import ContentType
from proprietario.models import Proprietario

class EstadoModelTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')

    def test_estado_creation(self):
        self.assertEqual(self.estado.sigla, 'SP')
        self.assertEqual(self.estado.nome, 'São Paulo')

    def test_estado_str(self):
        self.assertEqual(str(self.estado), 'São Paulo')

    def test_sigla_unique(self):
        with self.assertRaises(Exception):
            Estado.objects.create(sigla='SP', nome='Outro Nome')

class TelefoneModelTest(TestCase):
    def setUp(self):
        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')
        self.proprietario = Proprietario.objects.create(
            nome='Carlos Souza',
            cpf='12345678901',
            email='carlos@example.com',
            endereco='Rua B, 456',
            bairro='Centro',
            cidade='São Paulo',
            estado=self.estado,
            cep='01000-000',
            nacionalidade='Brasileiro',
            estado_civil='Casado',
            data_nascimento='1985-06-15'
        )
        self.content_type = ContentType.objects.get_for_model(Proprietario)
        self.telefone = Telefone.objects.create(
            pessoa=self.proprietario,
            numero='11999999999',
            tipo='Celular',
            content_type=self.content_type,
            object_id=self.proprietario.id
        )

    def test_telefone_creation(self):
        self.assertEqual(self.telefone.numero, '11999999999')
        self.assertEqual(self.telefone.tipo, 'Celular')

    def test_telefone_str(self):
        self.assertEqual(str(self.telefone), '11999999999 (Celular)')