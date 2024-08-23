from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from core.models import Estado, Telefone
from locatario.models import Locatario
from django.utils.dateparse import parse_date
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model


User = get_user_model()

class LocatarioModelTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla='MG', nome='Minas Gerais')
        self.locatario = Locatario.objects.create(
            nome='Ana Souza',
            cpf='12345678901',
            identidade='0101010101',
            orgao_expeditor='SSP/BA',
            email='ana@example.com',
            endereco='Rua C, 789',
            bairro='Savassi',
            cidade='Belo Horizonte',
            estado=self.estado,
            cep='30110-000',
            nacionalidade='Brasileira',
            estado_civil='Solteira'
        )        

        self.content_type = ContentType.objects.get_for_model(Locatario)
        self.telefone1 = Telefone.objects.create(
            pessoa=self.locatario,
            numero='11987654321',
            tipo='Celular',
            content_type=self.content_type,
            object_id=self.locatario.id
        )
        self.telefone2 = Telefone.objects.create(
            pessoa=self.locatario,
            numero='1122222222',
            tipo='Residencial',
            content_type=self.content_type,
            object_id=self.locatario.id
        )

    def test_locatario_creation(self):
        self.assertEqual(self.locatario.nome, 'Ana Souza')
        self.assertEqual(self.locatario.cpf, '12345678901')
        self.assertEqual(self.locatario.estado.nome, 'Minas Gerais')
       
    def test_locatario_str(self):
        self.assertEqual(str(self.locatario), 'Ana Souza (Locatário)')

    def test_locatario_multiple_telefones(self):
        telefones = Telefone.objects.filter(object_id=self.locatario.id, content_type=self.content_type)
        self.assertEqual(telefones.count(), 2)
        self.assertIn(self.telefone1, telefones)
        self.assertIn(self.telefone2, telefones)

class LocatarioAPITestCase(APITestCase):

    def setUp(self):
         # Criar usuário para autenticação
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Gerar o token JWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Configurar o cliente com o token JWT
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        #print(f"Token: {self.access_token}")

        # Criar Estado
        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')

    def test_create_locatario(self):
        url = reverse('locatario-list')
        data = {
            "nome": "José da Silva",
            "cpf": "12345678901",
            'identidade':'0101010101',
            'orgao_expeditor':'SSP BA',
            "email": "jose.silva@example.com",
            "endereco": "Rua A, 123",
            "bairro": "Bela Vista",
            "cidade": "São Paulo",
            "estado": self.estado.id,
            "cep": "01000-000",
            "nacionalidade": "Brasileiro",
            "estado_civil": "Solteiro(a)",
            "data_nascimento": "1990-01-01",
            "telefones": [
                {"numero": "11999999999", "tipo": "Celular"},
                {"numero": "1133333333", "tipo": "Residencial"}
            ]
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Locatario.objects.count(), 1)
        self.assertEqual(Telefone.objects.count(), 2)
        
    
        locatario = Locatario.objects.first()
    
        # Verifica se dois telefones foram criados e associados ao locatario
        self.assertEqual(Telefone.objects.filter(content_type__model='locatario', object_id=locatario.id).count(), 2)

        # Verifica se os telefones criados possuem os números corretos
        self.assertTrue(Telefone.objects.filter(numero="11999999999", tipo="Celular", object_id=locatario.id).exists())
        self.assertTrue(Telefone.objects.filter(numero="1133333333", tipo="Residencial", object_id=locatario.id).exists())

    def test_get_locatario(self):
        locatario = Locatario.objects.create(
            nome='José da Silva',
            cpf='12345678901',
            identidade = '0101010101',
            orgao_expeditor='SSP BA',
            email='jose.silva@example.com',
            endereco='Rua A, 123',
            bairro='Bela Vista',
            cidade='São Paulo',
            estado=self.estado,
            cep='01000-000',
            nacionalidade='Brasileiro',
            estado_civil='Solteiro(a)',
            data_nascimento='1990-01-01'
        )
        url = reverse('locatario-detail', args=[locatario.id])
        response = self.client.get(url, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'José da Silva')

    def test_update_locatario(self):
        locatario = Locatario.objects.create(
            nome='José da Silva',
            cpf='12345678901',
            identidade = '0101010101',
            orgao_expeditor='SSP BA',
            email='jose.silva@example.com',
            endereco='Rua A, 123',
            bairro='Bela Vista',
            cidade='São Paulo',
            estado=self.estado,
            cep='01000-000',
            nacionalidade='Brasileiro',
            estado_civil='Solteiro(a)',
            data_nascimento='1990-01-01'
        )
        url = reverse('locatario-detail', args=[locatario.id])
        data = {
            "nome": "José da Silva Junior",
            "cpf": "12345678901",
            'identidade':'0101010101',
            'orgao_expeditor':'SSP BA',
            "email": "jose.junior@example.com",
            "endereco": "Rua B, 456",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": self.estado.id,
            "cep": "02000-000",
            "nacionalidade": "Brasileiro",
            "estado_civil": "Casado(a)",
            "data_nascimento": "1990-01-01",
            "telefones": [
                {"numero": "11999999999", "tipo": "Celular"},
                {"numero": "1133333333", "tipo": "Residencial"}
            ]
        }
        response = self.client.put(url, data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'José da Silva Junior')
        #self.assertEqual(Telefone.objects.filter(pessoa=locatario).count(), 2)
        #self.assertEqual(Telefone.objects.filter(pessoa=locatario, numero="11999999999").exists(), True)

        content_type = ContentType.objects.get_for_model(locatario)
        telefone_count = Telefone.objects.filter(
            content_type=content_type, object_id=locatario.id).count()
        
        self.assertEqual(telefone_count, 2)

    def test_pagination_of_locatarios(self):
        # Criar vários locatários para testar a paginação
        for i in range(15):
            Locatario.objects.create(
                nome=f'Locatario {i+1}',
                cpf=f'{i+1:03d}.456.789-0{i+1:01d}',
                identidade=f'{i+1:02d}3456789',
                orgao_expeditor='SSP-SP',
                email=f'locatario{i+1}@email.com',
                endereco=f'Rua {i+1}, 123',
                bairro='Centro',
                cidade='Cidade Exemplo',
                estado=self.estado,
                cep='01000-000',
                nacionalidade='Brasileiro',
                estado_civil='Solteiro(a)',
                data_nascimento='1990-01-01'
            )

        # Defina a URL do endpoint de locatários
        url = reverse('locatario-list')

        # Faça uma requisição GET para a primeira página
        response = self.client.get(url, {'page': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Assumindo que a página tem 10 itens por padrão

        # Verifique se há uma próxima página
        self.assertIsNotNone(response.data['next'])

        # Faça uma requisição GET para a segunda página
        response = self.client.get(url, {'page': 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Os 5 locatários restantes

        # Verifique se a segunda página é a última
        self.assertIsNone(response.data['next'])
