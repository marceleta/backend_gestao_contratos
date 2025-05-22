from django.test import TestCase
from core.models import PessoaFisica, Estado, Telefone, Endereco
from core.serializers import PessoaFisicaSerializer

class PessoaFisicaSerializerTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        self.telefone_data = [{
            'numero': '(11) 99999-9999',
            'tipo': 'Celular'
        }]
        self.endereco_data = {
            'tipo_endereco': 'Residencial',
            'rua': 'Rua A',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': self.estado,
            'cep': '12345-678'
        }
        self.pessoa_fisica_data = {
            'nome': 'João da Silva',
            'email': 'joao@example.com',
            'cpf': '123.456.789-00',
            'identidade': 'MG-12.345.678',
            'orgao_expeditor': 'SSP-MG',
            'cnh': None,
            'orgao_expeditor_cnh': None,
            'data_nascimento': '1980-01-01',
            'estado_civil': 'Solteiro(a)',
            'nacionalidade': 'Brasileiro',
            'profissao': None
        }
        self.pessoa_fisica = PessoaFisica.objects.create(**self.pessoa_fisica_data)
        for telefone in self.telefone_data:
            Telefone.objects.create(content_object=self.pessoa_fisica, **telefone)
        self.endereco = Endereco.objects.create(content_object=self.pessoa_fisica, **self.endereco_data)

    def test_pessoa_fisica_serializer_create(self):
        
        endereco_data = {
            'tipo_endereco': 'Residencial',
            'rua': 'Rua A',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': self.estado.id,
            'cep': '12345-678'
        }

        data = {
            'nome': 'João da Silva',
            'email': 'joao2@example.com',
            'cpf': '123.456.789-99',
            'identidade': 'SP-12.345.678',
            'orgao_expeditor': 'SSP-MG',
            'cnh': '1234565647',
            'orgao_expeditor_cnh': 'DETRAN-MG',
            'data_nascimento': '1980-01-01',
            'estado_civil': 'Solteiro(a)',
            'nacionalidade': 'Brasileiro',
            'profissao': 'Empresario',
            'telefones': self.telefone_data,
            'enderecos': [endereco_data]
        }
        serializer = PessoaFisicaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        pessoa_fisica = serializer.save()
        self.assertEqual(pessoa_fisica.nome, data['nome'])
        self.assertEqual(pessoa_fisica.cpf, data['cpf'])
        self.assertEqual(pessoa_fisica.telefones.count(), 1)
        self.assertEqual(pessoa_fisica.enderecos.count(), 1)

    def test_pessoa_fisica_serializer_read(self):
        serializer = PessoaFisicaSerializer(self.pessoa_fisica)
        self.assertEqual(serializer.data['nome'], self.pessoa_fisica_data['nome'])
        self.assertEqual(serializer.data['cpf'], self.pessoa_fisica_data['cpf'])
        self.assertEqual(serializer.data['telefones'][0]['numero'], self.telefone_data[0]['numero'])
        self.assertEqual(serializer.data['enderecos'][0]['rua'], self.endereco_data['rua'])

    def test_pessoa_fisica_serializer_update(self):
        nova_pessoa_fisica_data = self.pessoa_fisica_data.copy()
        nova_pessoa_fisica_data.update({
            'nome': 'João Silva',
            'cpf': '123.456.789-00',
            'telefones': [{'numero': '(11) 98888-8888', 'tipo': 'Comercial'}],
            'enderecos': [{'tipo_endereco': 'Comercial', 'rua': 'Avenida Paulista', 'numero': '1000', 'bairro': 'Bela Vista', 'cidade': 'São Paulo', 'estado': self.estado.id, 'cep': '01310-000'}]
        })
        serializer = PessoaFisicaSerializer(self.pessoa_fisica, data=nova_pessoa_fisica_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        pessoa_fisica_atualizada = serializer.save()
        self.assertEqual(pessoa_fisica_atualizada.nome, nova_pessoa_fisica_data['nome'])
        self.assertEqual(pessoa_fisica_atualizada.telefones.count(), 1)
        self.assertEqual(pessoa_fisica_atualizada.telefones.first().numero, nova_pessoa_fisica_data['telefones'][0]['numero'])
        self.assertEqual(pessoa_fisica_atualizada.enderecos.count(), 1)
        self.assertEqual(pessoa_fisica_atualizada.enderecos.first().rua, nova_pessoa_fisica_data['enderecos'][0]['rua'])

    def test_pessoa_fisica_serializer_delete(self):
        pessoa_fisica_id = self.pessoa_fisica.id
        self.pessoa_fisica.delete()
        self.assertFalse(PessoaFisica.objects.filter(id=pessoa_fisica_id).exists())

