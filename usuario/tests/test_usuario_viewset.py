from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from usuario.models import Usuario
from rest_framework.authtoken.models import Token

class UsuarioViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Criação de um superusuário e um usuário regular para os testes
        self.admin_user = Usuario.objects.create_superuser(
            username='adminuser', password='adminpass', email='admin@example.com'
        )
        self.regular_user = Usuario.objects.create_user(
            username='regularuser', password='regularpass', email='regular@example.com'
        )

        self.admin_token = Token.objects.create(user=self.admin_user)
        self.regular_token = Token.objects.create(user=self.regular_user)

    def authenticate_as(self, user_type='regular'):
        """Autentica o cliente como admin ou usuário regular forçando a autenticação."""
        user = self.admin_user if user_type == 'admin' else self.regular_user
        self.client.force_authenticate(user=user)


    def test_create_usuario(self):
        """Testa a criação de um novo usuário, acessível apenas para admins."""
        self.authenticate_as('admin')
        url = reverse('usuario-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newuserpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 3)  # 1 admin + 1 regular + 1 novo

    def test_retrieve_usuario(self):
        """Testa a recuperação de um usuário específico."""
        self.authenticate_as('regular')
        url = reverse('usuario-detail', args=[self.regular_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'regularuser')

    def test_update_usuario(self):
        """Testa a atualização de um usuário específico."""
        self.authenticate_as('regular')
        url = reverse('usuario-detail', args=[self.regular_user.id])
        data = {'first_name': 'UpdatedName'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'UpdatedName')

    def test_delete_usuario(self):
        """Testa a exclusão de um usuário, acessível apenas para admins."""
        self.authenticate_as('admin')
        url = reverse('usuario-detail', args=[self.regular_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Usuario.objects.count(), 1)  # Apenas o admin deve restar

    def test_list_usuarios(self):
        """Testa a listagem de todos os usuários, acessível apenas para admins."""
        self.authenticate_as('admin')
        url = reverse('usuario-list')
        response = self.client.get(url)
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 usuários (admin e regular)

    def test_regular_user_cannot_create_user(self):
        """Testa que um usuário regular não pode criar novos usuários."""
        self.authenticate_as('regular')
        url = reverse('usuario-list')
        data = {
            'username': 'forbiddenuser',
            'email': 'forbidden@example.com',
            'password': 'forbiddenpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_consulta_permissoes(self):
        """Testa a consulta das permissões de um usuário específico."""
        self.authenticate_as('admin')
        url = reverse('usuario-detail', args=[self.admin_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        permissoes = response.data.get('permissoes', [])
        self.assertIsInstance(permissoes, list)
        self.assertIn('usuario.add_usuario', permissoes)  # Exemplo de permissão para admin
