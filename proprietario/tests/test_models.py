from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from core.models import Estado, Telefone
from proprietario.models import Proprietario, Representante
from rest_framework.authtoken.models import Token
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class ProprietarioModelTest(TestCase):

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
            data_nascimento='1985-06-15',
            preferencia_comunicacao='Email'
        )
        self.content_type = ContentType.objects.get_for_model(Proprietario)
        self.telefone1 = Telefone.objects.create(
            pessoa=self.proprietario,
            numero='11999999999',
            tipo='Celular',
            content_type=self.content_type,
            object_id=self.proprietario.id
        )
        self.telefone2 = Telefone.objects.create(
            pessoa=self.proprietario,
            numero='1133333333',
            tipo='Residencial',
            content_type=self.content_type,
            object_id=self.proprietario.id
        )

    def test_proprietario_creation(self):
        self.assertEqual(self.proprietario.nome, 'Carlos Souza')
        self.assertEqual(self.proprietario.cpf, '12345678901')
        self.assertEqual(self.proprietario.estado.nome, 'São Paulo')

    def test_proprietario_str(self):
        self.assertEqual(str(self.proprietario), 'Carlos Souza (Proprietário)')

    def test_proprietario_multiple_telefones(self):
        telefones = Telefone.objects.filter(object_id=self.proprietario.id, content_type=self.content_type)
        self.assertEqual(telefones.count(), 2)
        self.assertIn(self.telefone1, telefones)
        self.assertIn(self.telefone2, telefones)

class ProprietarioAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
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
            estado_civil='Casado(a)',
            data_nascimento='1985-06-15'
        )
        self.telefone1 = Telefone.objects.create(pessoa=self.proprietario, numero='11999999999', tipo='Celular')
        self.telefone2 = Telefone.objects.create(pessoa=self.proprietario, numero='1133333333', tipo='Residencial')

    def test_create_proprietario(self):
        url = reverse('proprietario-list')
        
        content_type = ContentType.objects.get_for_model(Proprietario)

        self.assertEqual(Proprietario.objects.count(), 1)
        self.assertEqual(Telefone.objects.filter(content_type=content_type, object_id=self.proprietario.id).count(), 2)

    def test_get_proprietario(self):    
        
        # Faz a requisição GET
        url = reverse('proprietario-detail', args=[self.proprietario.id])
        response = self.client.get(url, format='json')

        # Verifica se a resposta está correta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.proprietario.nome)
        self.assertEqual(len(response.data['telefones']), 2)

    def test_update_proprietario(self):
        # Dados de atualização
        data = {
            "nome": "Carlos Souza Junior",
            "cpf": "12345678901",
            "email": "carlosjr@example.com",
            "endereco": "Avenida Paulista, 1000",
            "bairro": "Bela Vista",
            "cidade": "São Paulo",
            "estado": self.estado.id,
            "cep": "01310-100",
            "nacionalidade": "Brasileiro",
            "estado_civil": "Casado(a)",
            "data_nascimento": "1985-06-15",
            "preferencia_comunicacao": "Telefone",
            "telefones": [
                {"numero": "11988888888", "tipo": "Celular"},
                {"numero": "1132222222", "tipo": "Residencial"}
            ]
        }

        # Faz a requisição PUT
        url = reverse('proprietario-detail', args=[self.proprietario.id])
        response = self.client.put(url, data, format='json')

        # Verifica se a resposta está correta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Proprietario.objects.get().nome, "Carlos Souza Junior")
        self.assertEqual(Telefone.objects.filter(object_id=self.proprietario.id).count(), 2)



class RepresentanteModelTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla='RJ', nome='Rio de Janeiro')
        self.representante = Representante.objects.create(
            nome='Mariana Lima',
            cpf='09876543210',
            email='mariana@example.com',
            endereco='Avenida C, 789',
            bairro='Botafogo',
            cidade='Rio de Janeiro',
            estado=self.estado,
            cep='22250-040',
            nacionalidade='Brasileira',
            data_nascimento='1985-06-15',
            estado_civil='Solteira'
        )
        self.content_type = ContentType.objects.get_for_model(Representante)

        # Adicionando os telefones ao representante
        self.telefone1 = Telefone.objects.create(
        numero='21988888888',
        tipo='Celular',
        content_type=self.content_type,
        object_id=self.representante.id
        )
        self.telefone2 = Telefone.objects.create(
            numero='2133334444',
            tipo='Residencial',
            content_type=self.content_type,
            object_id=self.representante.id
        )

    def test_representante_creation(self):
        self.assertEqual(self.representante.nome, 'Mariana Lima')
        self.assertEqual(self.representante.cpf, '09876543210')
        self.assertEqual(self.representante.estado.nome, 'Rio de Janeiro')

    def test_representante_str(self):
        self.assertEqual(str(self.representante), 'Mariana Lima (Representante)')

    def test_representante_multiple_telefones(self):  
        telefones = Telefone.objects.filter(object_id=self.representante.id, content_type=self.content_type)
        self.assertEqual(telefones.count(), 2)
        self.assertIn(self.telefone1, telefones)
        self.assertIn(self.telefone2, telefones)

class RepresentanteAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.estado = Estado.objects.create(sigla='RJ', nome='Rio de Janeiro')
        self.representante = Representante.objects.create(
            nome='Mariana Lima',
            cpf='09876543210',
            email='mariana@example.com',
            endereco='Avenida C, 789',
            bairro='Botafogo',
            cidade='Rio de Janeiro',
            estado=self.estado,
            cep='22250-040',
            nacionalidade='Brasileira',
            data_nascimento='1985-06-15',
            estado_civil='Solteira'
        )
        self.telefone1 = Telefone.objects.create(pessoa=self.representante, numero='21988888888', tipo='Celular')
        self.telefone2 = Telefone.objects.create(pessoa=self.representante, numero='2133334444', tipo='Residencial')

    def test_create_representante(self):

        # Obtenha o ContentType do modelo Representante
        content_type = ContentType.objects.get_for_model(Representante)
        
        self.assertEqual(self.representante.nome, "Mariana Lima")
        self.assertEqual(self.representante.cpf, "09876543210")
        self.assertEqual(self.representante.telefones.count(), 2)
        self.assertEqual(Telefone.objects.filter(content_type=content_type, object_id=self.representante.id).count(), 2)

    def test_get_representante(self):
        
        url = reverse('representante-detail', args=[self.representante.id])
        response = self.client.get(url, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.representante.nome)
        self.assertEqual(len(response.data['telefones']), 2)

    def test_update_representante(self):
        
        self.telefone1 = Telefone.objects.create(
            numero="21988888888",
            tipo="Celular",
            content_type=ContentType.objects.get_for_model(Representante),
            object_id=self.representante.id
        )

        data = {
            "nome": "Mariana Lima Silva",
            "cpf": "09876543210",
            "email": "marianasilva@example.com",
            "endereco": "Rua Nova, 100",
            "bairro": "Copacabana",
            "cidade": "Rio de Janeiro",
            "estado": self.estado.id,
            "cep": "22000-000",
            "nacionalidade": "Brasileira",
            "data_nascimento": "1985-06-15",
            "estado_civil": "Casado(a)",
            "telefones": [
                {"numero": "21977777777", "tipo": "Celular"},
                {"numero": "2134444444", "tipo": "Residencial"}
            ]
        }

        url = reverse('representante-detail', args=[self.representante.id])
        response = self.client.put(url, data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Representante.objects.get().nome, "Mariana Lima Silva")
        self.assertEqual(Telefone.objects.filter(object_id=self.representante.id).count(), 2)

        