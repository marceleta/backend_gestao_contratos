from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from usuario.models import Usuario
from core.models import Estado
from rest_framework_simplejwt.tokens import RefreshToken

class EstadoViewSetTest(APITestCase):

    def setUp(self):
        
        Estado.objects.create(sigla='SP', nome='São Paulo')
        Estado.objects.create(sigla='RJ', nome='Rio de Janeiro')

        # Criar um usuário para autenticação
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')
        
    
        refresh = RefreshToken.for_user(self.usuario)
        self.token = str(refresh.access_token)

        # Configurar o cabeçalho de autorização para incluir o token JWT
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')


    def test_list_estados(self):
        """
        Testa a operação de listar todos os estados.
        """
        url = reverse('estado-list')
        response = self.client.get(url)
        #print(response.data)
        
        # Verifica se o status é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se a lista de estados tem o tamanho esperado
        self.assertEqual(len(response.data['results']), 2)
        
        # Verifica se os nomes dos estados estão corretos
        self.assertEqual(response.data['results'][1]['nome'], 'São Paulo')
        self.assertEqual(response.data['results'][0]['nome'], 'Rio de Janeiro')

    def test_get_estado(self):
        """
        Testa a operação de recuperar um estado específico.
        """
        estado = Estado.objects.get(sigla='SP')
        url = reverse('estado-detail', args=[estado.id])
        response = self.client.get(url)
        
        # Verifica se o status é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se o nome do estado está correto
        self.assertEqual(response.data['nome'], 'São Paulo')

