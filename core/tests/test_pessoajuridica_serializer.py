from django.test import TestCase
from core.models import PessoaJuridica, Telefone, Estado
from core.serializers import PessoaJuridicaSerializer

class PessoaJuridicaSerializerTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        self.telefone_data = [
            {'numero': '(11) 99999-9999', 'tipo': 'Celular'},
            {'numero': '(11) 3888-8888', 'tipo': 'Comercial'}
        ]
        self.pessoa_juridica_data = {
            'nome': 'Empresa X',
            'email': 'contato@empresax.com',
            'telefone': '12345-6789',
            'endereco': 'Av. Principal, 1000',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': self.estado,
            'cep': '12345-678',
            'cnpj': '12.345.678/0001-99',
            'data_fundacao': '2000-01-01',
            'nome_fantasia': 'Empresa X Ltda',
            'data_abertura': '2000-01-01',
            'inscricao_estadual': '123456789',
            'natureza_juridica': 'Sociedade Limitada',
            'atividade_principal_cnae': '6201-5/00',
        }
        self.pessoa_juridica = PessoaJuridica.objects.create(**self.pessoa_juridica_data)
        for telefone in self.telefone_data:
            Telefone.objects.create(content_object=self.pessoa_juridica, **telefone)

    def test_pessoa_juridica_serializer_create(self):
        nova_pessoa_juridica_data = self.pessoa_juridica_data.copy()
        nova_pessoa_juridica_data['email'] = 'contato2@empresax.com'  # Use a different email
        nova_pessoa_juridica_data['cnpj'] = '12.345.678/0001-98'  # Use a different CNPJ
        nova_pessoa_juridica_data['estado'] = self.estado.id
        nova_pessoa_juridica_data['telefones'] = self.telefone_data

        serializer = PessoaJuridicaSerializer(data=nova_pessoa_juridica_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        pessoa_juridica = serializer.save()
        self.assertEqual(pessoa_juridica.nome, nova_pessoa_juridica_data['nome'])

    def test_pessoa_juridica_serializer_update(self):
        nova_data = self.pessoa_juridica_data.copy()
        nova_data['nome_fantasia'] = 'Empresa Y Ltda'
        nova_data['estado'] = self.estado.id
        nova_data['telefones'] = self.telefone_data
        #print(nova_data)
        serializer = PessoaJuridicaSerializer(self.pessoa_juridica, data=nova_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        pessoa_juridica_atualizada = serializer.save()
        self.assertEqual(pessoa_juridica_atualizada.nome_fantasia, 'Empresa Y Ltda')

    def test_pessoa_juridica_serializer_read(self):
        serializer = PessoaJuridicaSerializer(self.pessoa_juridica)
        data = serializer.data
        self.assertEqual(data['nome'], self.pessoa_juridica_data['nome'])
        self.assertEqual(data['email'], self.pessoa_juridica_data['email'])
        self.assertEqual(data['telefone'], self.pessoa_juridica_data['telefone'])

    def test_pessoa_juridica_serializer_delete(self):
        pessoa_juridica_id = self.pessoa_juridica.id
        self.pessoa_juridica.delete()
        self.assertFalse(PessoaJuridica.objects.filter(id=pessoa_juridica_id).exists())

