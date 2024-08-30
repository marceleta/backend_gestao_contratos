from django.test import TestCase
from core.models import Telefone, PessoaFisica, Estado
from core.serializers import TelefoneSerializer

class TelefoneSerializerTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        self.pessoa_fisica = PessoaFisica.objects.create(
            nome="João da Silva",
            email="joao@example.com",
            telefone="12345-6789",
            endereco="Rua A",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="12345-678",
            cpf="123.456.789-00",
            identidade="MG-12.345.678",
            orgao_expeditor="SSP-MG",
            data_nascimento="1980-01-01",
            estado_civil="Solteiro(a)",
            nacionalidade="Brasileiro"
        )
        self.telefone_data = {
            'numero': '(11) 99999-9999',
            'tipo': 'Celular'
        }
        self.telefone = Telefone.objects.create(
            numero=self.telefone_data['numero'],
            tipo=self.telefone_data['tipo'],
            content_object=self.pessoa_fisica
        )

    def test_telefone_serializer_create(self):
        serializer = TelefoneSerializer(data=self.telefone_data)
        self.assertTrue(serializer.is_valid())
        telefone = serializer.save(content_object=self.pessoa_fisica)
        self.assertEqual(telefone.numero, self.telefone_data['numero'])
        self.assertEqual(telefone.tipo, self.telefone_data['tipo'])

    def test_telefone_serializer_read(self):
        serializer = TelefoneSerializer(self.telefone)
        self.assertEqual(serializer.data['numero'], self.telefone_data['numero'])
        self.assertEqual(serializer.data['tipo'], self.telefone_data['tipo'])

    def test_telefone_serializer_update(self):
        nova_telefone_data = {
            'numero': '(11) 98888-8888',
            'tipo': 'Comercial'
        }
        serializer = TelefoneSerializer(self.telefone, data=nova_telefone_data, partial=True)
        self.assertTrue(serializer.is_valid())
        telefone = serializer.save()
        self.assertEqual(telefone.numero, nova_telefone_data['numero'])
        self.assertEqual(telefone.tipo, nova_telefone_data['tipo'])

    def test_telefone_serializer_delete(self):
        telefone_id = self.telefone.id
        self.telefone.delete()
        self.assertFalse(Telefone.objects.filter(id=telefone_id).exists())
