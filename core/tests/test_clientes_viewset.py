from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import PessoaFisica, PessoaJuridica, Estado, Telefone, Endereco
from usuario.models import Usuario
from django.db.models import Q


class ClienteViewSetTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Criar um usuário para autenticação
        cls.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Criar estados para associação
        cls.estado_sp = Estado.objects.create(sigla='SP', nome='São Paulo')
        cls.estado_rj = Estado.objects.create(sigla='RJ', nome='Rio de Janeiro')

        # Criar uma PessoaFisica
        cls.pessoa_fisica = PessoaFisica.objects.create(
            nome='João da Silva', email='joao@example.com',
            cpf='123.456.789-00', identidade='MG-12.345.678',
            orgao_expeditor='SSP-MG', data_nascimento='1980-01-01',
            estado_civil='Solteiro(a)', nacionalidade='Brasileiro'
        )

        # Adicionar telefone e endereço à PessoaFisica
        Telefone.objects.create(numero='12345-6789', tipo='Residencial', content_object=cls.pessoa_fisica)
        Endereco.objects.create(
            tipo_endereco='Residencial', rua='Rua A', numero='123', bairro='Centro',
            cidade='São Paulo', estado=cls.estado_sp, cep='12345-678',
            content_object=cls.pessoa_fisica
        )

        # Criar uma PessoaJuridica
        cls.pessoa_juridica = PessoaJuridica.objects.create(
            nome='Empresa XYZ', email='contato@xyz.com.br',
            cnpj='12.345.678/0001-99', data_fundacao='2000-01-01',
            nome_fantasia='Fantasia XYZ', inscricao_estadual='123456789',
            natureza_juridica='Sociedade Anônima', atividade_principal_cnae='6201-5/00'
        )

        # Adicionar telefone e endereço à PessoaJuridica
        Telefone.objects.create(numero='12345-6789', tipo='Comercial', content_object=cls.pessoa_juridica)
        Endereco.objects.create(
            tipo_endereco='Comercial', rua='Av. Principal, 1000', numero='1000', bairro='Centro',
            cidade='Rio de Janeiro', estado=cls.estado_rj, cep='20000-000',
            content_object=cls.pessoa_juridica
        )

    def setUp(self):
        # Configuração do token JWT
        refresh = RefreshToken.for_user(self.usuario)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_pessoa_fisica(self):
        url = reverse('cliente-list')
        data = {
            "nome": "Maria Silva",
            "email": "maria@example.com",
            "cpf": "111.222.333-44",
            "identidade": "MG-12.345.679",
            "orgao_expeditor": "SSP-MG",
            "data_nascimento": "1990-01-01",
            "estado_civil": "Solteiro(a)",
            "nacionalidade": "Brasileiro",
            "profissao": "Engenheiro",
            "telefones": [{"numero": "98765-4321", "tipo": "Celular"}],
            "enderecos": [{
                "tipo_endereco": "Residencial",
                "rua": "Rua B",
                "numero": "456",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": self.estado_sp.id,
                "cep": "12345-678"
            }]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['nome'], 'Maria Silva')

    def test_create_pessoa_juridica(self):
        url = reverse('cliente-list')
        data = {
            "nome": "Empresa ABC",
            "email": "contato@abc.com.br",
            "cnpj": "12.345.678/0001-88",
            "data_fundacao": "2010-01-01",
            "nome_fantasia": "Fantasia ABC",
            "inscricao_estadual": "987654321",
            "natureza_juridica": "Sociedade Limitada",
            "atividade_principal_cnae": "6201-5/00",
            "telefones": [{"numero": "12345-6789", "tipo": "Comercial"}],
            "enderecos": [{
                "tipo_endereco": "Comercial",
                "rua": "Av. Nova",
                "numero": "2000",
                "bairro": "Centro",
                "cidade": "Rio de Janeiro",
                "estado": self.estado_rj.id,
                "cep": "20000-000"
            }]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['nome'], 'Empresa ABC')

    def test_retrieve_pessoa_fisica(self):
        url = reverse('cliente-detail', args=[self.pessoa_fisica.pk]) + '?tipo=fisica'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.pessoa_fisica.nome)

    def test_retrieve_pessoa_juridica(self):
        url = reverse('cliente-detail', args=[self.pessoa_juridica.pk]) + '?tipo=juridica'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.pessoa_juridica.nome)

    def test_update_pessoa_fisica(self):
        url = reverse('cliente-detail', args=[self.pessoa_fisica.pk]) + '?tipo=fisica'
        data = {
            "nome": "João da Silva Atualizado",
            "email": "joaoatualizado@example.com",
            "telefones": [{"numero": "98765-4321", "tipo": "Celular"}],
            "enderecos": [{
                "tipo_endereco": "Residencial",
                "rua": "Rua B",
                "numero": "789",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": self.estado_sp.id,
                "cep": "12345-678"
            }]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'João da Silva Atualizado')

    def test_destroy_pessoa_fisica(self):
        url = reverse('cliente-detail', args=[self.pessoa_fisica.pk]) + '?tipo=fisica'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PessoaFisica.objects.filter(pk=self.pessoa_fisica.pk).exists())

    def test_destroy_pessoa_juridica(self):
        url = reverse('cliente-detail', args=[self.pessoa_juridica.pk]) + '?tipo=juridica'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PessoaJuridica.objects.filter(pk=self.pessoa_juridica.pk).exists())

    def test_search_cliente_com_resultados(self):
        url = reverse('cliente-search_by_nome') + '?search=João'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(cliente['nome'] == 'João da Silva' for cliente in response.data['results']))

    def test_search_cliente_sem_resultados(self):
        url = reverse('cliente-search_by_nome') + '?search=NomeInexistente'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], "Nenhum registro encontrado para o termo de busca fornecido.")

