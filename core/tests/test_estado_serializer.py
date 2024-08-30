from django.test import TestCase
from core.models import Estado
from core.serializers import EstadoSerializer

class EstadoSerializerTest(TestCase):

    def setUp(self):
        self.estado_data = {
            'sigla': 'SP',
            'nome': 'São Paulo'
        }
        self.estado = Estado.objects.create(**self.estado_data)

    def test_estado_serializer_create(self):
        nova_estado_data = {
            'sigla': 'RJ',
            'nome': 'Rio de Janeiro'
        }
        serializer = EstadoSerializer(data=nova_estado_data)
        self.assertTrue(serializer.is_valid())
        estado = serializer.save()
        self.assertEqual(estado.sigla, nova_estado_data['sigla'])
        self.assertEqual(estado.nome, nova_estado_data['nome'])

    def test_estado_serializer_read(self):
        serializer = EstadoSerializer(self.estado)
        self.assertEqual(serializer.data['sigla'], self.estado_data['sigla'])
        self.assertEqual(serializer.data['nome'], self.estado_data['nome'])

    def test_estado_serializer_update(self):
        nova_estado_data = {
            'nome': 'São Paulo Atualizado'
        }
        serializer = EstadoSerializer(self.estado, data=nova_estado_data, partial=True)
        self.assertTrue(serializer.is_valid())
        estado_atualizado = serializer.save()
        self.assertEqual(estado_atualizado.nome, nova_estado_data['nome'])
        self.assertEqual(estado_atualizado.sigla, self.estado.sigla)

    def test_estado_serializer_delete(self):
        estado_id = self.estado.id
        self.estado.delete()
        self.assertFalse(Estado.objects.filter(id=estado_id).exists())
