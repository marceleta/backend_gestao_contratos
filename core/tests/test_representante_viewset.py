from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import Estado, PessoaFisica, PessoaJuridica, Representante
from usuario.models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken

class RepresentanteViewSetTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Criação do usuário para autenticação
        cls.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Criando estados, pessoas físicas e jurídicas para os testes
        cls.estado_sp = Estado.objects.create(sigla='SP', nome='São Paulo')
        cls.estado_rj = Estado.objects.create(sigla='RJ', nome='Rio de Janeiro')

        cls.pessoa_fisica = PessoaFisica.objects.create(
            nome='João da Silva',
            email='joao@example.com',
            telefone='12345-6789',
            endereco='Rua A',
            bairro='Centro',
            cidade='São Paulo',
            estado=cls.estado_sp,
            cep='12345-678',
            cpf='123.456.789-00',
            identidade='MG-12.345.678',
            orgao_expeditor='SSP-MG',
            data_nascimento='1980-01-01',
            estado_civil='Solteiro(a)',
            nacionalidade='Brasileiro'
        )

        cls.pessoa_juridica = PessoaJuridica.objects.create(
            nome='Empresa ABC',
            email='empresa@example.com',
            telefone='12345-6789',
            endereco='Rua B',
            bairro='Centro',
            cidade='São Paulo',
            estado=cls.estado_rj,
            cep='12345-678',
            cnpj='12.345.678/0001-00',
            data_fundacao='2000-01-01',
            nome_fantasia='Fantasia ABC',
            inscricao_estadual='123456789',
            natureza_juridica='Sociedade Anônima',
            atividade_principal_cnae='62.01-1-00'
        )

    def setUp(self):
       # Geração do token JWT
       refresh = RefreshToken.for_user(self.usuario)
       self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')


    def test_create_representante(self):
        url = reverse('representante-list')
        data = {
            'pessoa_fisica': self.pessoa_fisica.id,
            'pessoa_juridica': self.pessoa_juridica.id,
            'cargo': 'Gerente',
            'nivel_autoridade': 'Supervisor'
        }
        response = self.client.post(url, data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Representante.objects.count(), 1)
        self.assertEqual(Representante.objects.get().cargo, 'Gerente')


    def test_retrieve_representante(self):
        representante = Representante.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            pessoa_juridica=self.pessoa_juridica,
            cargo='Gerente',
            nivel_autoridade='Supervisor'
        )
        url = reverse('representante-detail', args=[representante.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cargo'], 'Gerente')


    def test_update_representante(self):
        representante = Representante.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            pessoa_juridica=self.pessoa_juridica,
            cargo='Gerente',
            nivel_autoridade='Supervisor'
        )
        url = reverse('representante-detail', args=[representante.pk])
        data = {
            'cargo': 'Diretor',
            'nivel_autoridade': 'Gerente'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        representante.refresh_from_db()
        self.assertEqual(representante.cargo, 'Diretor')
        self.assertEqual(representante.nivel_autoridade, 'Gerente')


    def test_delete_representante(self):
        representante = Representante.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            pessoa_juridica=self.pessoa_juridica,
            cargo='Gerente',
            nivel_autoridade='Supervisor'
        )
        url = reverse('representante-detail', args=[representante.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Representante.objects.count(), 0)


    def test_update_representante_troca_pessoa_fisica(self):
        nova_pessoa_fisica = PessoaFisica.objects.create(
            nome='Carlos Pereira',
            email='carlos@example.com',
            telefone='12345-6789',
            endereco='Rua C',
            bairro='Centro',
            cidade='São Paulo',
            estado=self.estado_sp,
            cep='12345-678',
            cpf='987.654.321-00',
            identidade='SP-98.765.432',
            orgao_expeditor='SSP-SP',
            data_nascimento='1985-05-05',
            estado_civil='Casado(a)',
            nacionalidade='Brasileiro'
        )
        representante = Representante.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            pessoa_juridica=self.pessoa_juridica,
            cargo='Gerente',
            nivel_autoridade='Supervisor'
        )
        url = reverse('representante-detail', args=[representante.pk])
        data = {
            'pessoa_fisica': nova_pessoa_fisica.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        representante.refresh_from_db()
        self.assertEqual(representante.pessoa_fisica, nova_pessoa_fisica)


    def test_update_representante_troca_pessoa_juridica(self):
        nova_pessoa_juridica = PessoaJuridica.objects.create(
            nome='Empresa XYZ',
            email='empresa_xyz@example.com',
            telefone='12345-6789',
            endereco='Rua D',
            bairro='Centro',
            cidade='Rio de Janeiro',
            estado=self.estado_rj,
            cep='98765-432',
            cnpj='98.765.432/0001-99',
            data_fundacao='2010-10-10',
            nome_fantasia='Fantasia XYZ',
            inscricao_estadual='987654321',
            natureza_juridica='Sociedade Limitada',
            atividade_principal_cnae='70.10-1-00'
        )
        representante = Representante.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            pessoa_juridica=self.pessoa_juridica,
            cargo='Gerente',
            nivel_autoridade='Supervisor'
        )
        url = reverse('representante-detail', args=[representante.pk])
        data = {
            'pessoa_juridica': nova_pessoa_juridica.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        representante.refresh_from_db()
        self.assertEqual(representante.pessoa_juridica, nova_pessoa_juridica)





