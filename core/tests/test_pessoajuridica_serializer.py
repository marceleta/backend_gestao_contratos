from django.test import TestCase
from core.models import PessoaJuridica, Estado, Telefone, Endereco
from core.serializers import PessoaJuridicaSerializer
from django.contrib.contenttypes.models import ContentType

class PessoaJuridicaSerializerTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")

        # Dados dos Telefones
        self.telefone_data = [
            {'numero': '(11) 99999-9999', 'tipo': 'Celular'},
            {'numero': '(11) 3888-8888', 'tipo': 'Comercial'}
        ]

        # Dados do Endereço
        self.endereco_data = {
            'tipo_endereco': 'Comercial',
            'rua': 'Av. Principal',
            'numero': '1000',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': self.estado,  # Passando apenas o ID
            'cep': '12345-678'
        }

        # Dados da Pessoa Jurídica
        self.pessoa_juridica_data = {
            'nome': 'Empresa X',
            'email': 'contato@empresax.com',
            'cnpj': '12.345.678/0001-99',
            'data_fundacao': '2000-01-01',
            'nome_fantasia': 'Empresa X Ltda',
            'data_abertura': '2000-01-01',
            'inscricao_estadual': '123456789',
            'natureza_juridica': 'Sociedade Limitada',
            'atividade_principal_cnae': '6201-5/00',
        }

        # Criando a instância de Pessoa Jurídica
        self.pessoa_juridica = PessoaJuridica.objects.create(**self.pessoa_juridica_data)

        # Obtendo ContentType para PessoaJuridica
        self.content_type = ContentType.objects.get_for_model(PessoaJuridica)

        # Criando Telefones associados
        for telefone in self.telefone_data:
            Telefone.objects.create(content_object=self.pessoa_juridica, **telefone)

        # Criando Endereço associado
        self.endereco = Endereco.objects.create(content_object=self.pessoa_juridica, **self.endereco_data)

    def test_pessoa_juridica_serializer_create(self):
        """Testa se o serializer cria corretamente uma nova PessoaJuridica com telefones e endereços."""
        endereco_data = {
            'tipo_endereco': 'Comercial',
            'rua': 'Av. Principal',
            'numero': '1000',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': self.estado.id,  # Passando apenas o ID
            'cep': '12345-678'
        }
        nova_pessoa_juridica_data = self.pessoa_juridica_data.copy()
        nova_pessoa_juridica_data['email'] = 'contato2@empresax.com'
        nova_pessoa_juridica_data['cnpj'] = '12.345.678/0001-98'
        nova_pessoa_juridica_data['telefones'] = self.telefone_data
        nova_pessoa_juridica_data['enderecos'] = [endereco_data]

        serializer = PessoaJuridicaSerializer(data=nova_pessoa_juridica_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        pessoa_juridica = serializer.save()
        self.assertEqual(pessoa_juridica.nome, nova_pessoa_juridica_data['nome'])
        self.assertEqual(pessoa_juridica.cnpj, nova_pessoa_juridica_data['cnpj'])
        self.assertEqual(pessoa_juridica.telefones.count(), len(self.telefone_data))
        self.assertEqual(pessoa_juridica.enderecos.count(), 1)

    def test_pessoa_juridica_serializer_update(self):
        """Testa se o serializer atualiza corretamente os dados de PessoaJuridica."""
        nova_data = self.pessoa_juridica_data.copy()
        nova_data['nome_fantasia'] = 'Empresa Y Ltda'
        nova_data['telefones'] = [
            {'numero': '(11) 97777-7777', 'tipo': 'Celular'}
        ]
        nova_data['enderecos'] = [{
            'tipo_endereco': 'Filial',
            'rua': 'Rua Nova',
            'numero': '200',
            'bairro': 'Bairro Novo',
            'cidade': 'São Paulo',
            'estado': self.estado.id,
            'cep': '54321-876'
        }]

        serializer = PessoaJuridicaSerializer(self.pessoa_juridica, data=nova_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        pessoa_juridica_atualizada = serializer.save()

        self.assertEqual(pessoa_juridica_atualizada.nome_fantasia, 'Empresa Y Ltda')
        self.assertEqual(pessoa_juridica_atualizada.telefones.count(), 1)
        self.assertEqual(pessoa_juridica_atualizada.telefones.first().numero, '(11) 97777-7777')
        self.assertEqual(pessoa_juridica_atualizada.enderecos.count(), 1)
        self.assertEqual(pessoa_juridica_atualizada.enderecos.first().rua, 'Rua Nova')

    def test_pessoa_juridica_serializer_read(self):
        """Testa se o serializer lê corretamente os dados de PessoaJuridica."""
        serializer = PessoaJuridicaSerializer(self.pessoa_juridica)
        data = serializer.data

        self.assertEqual(data['nome'], self.pessoa_juridica_data['nome'])
        self.assertEqual(data['email'], self.pessoa_juridica_data['email'])
        self.assertEqual(data['cnpj'], self.pessoa_juridica_data['cnpj'])
        self.assertEqual(len(data['telefones']), len(self.telefone_data))
        self.assertEqual(len(data['enderecos']), 1)

    def test_pessoa_juridica_serializer_delete(self):
        """Testa se a PessoaJuridica é deletada corretamente."""
        pessoa_juridica_id = self.pessoa_juridica.id
        self.pessoa_juridica.delete()
        self.assertFalse(PessoaJuridica.objects.filter(id=pessoa_juridica_id).exists())


