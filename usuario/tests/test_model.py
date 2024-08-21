from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

Usuario = get_user_model()

class UsuarioTestCase(TestCase):

    def setUp(self):
        # Configuração inicial para os testes
        self.client = APIClient()
        self.admin_user = Usuario.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.force_authenticate(user=self.admin_user)
        self.regular_user = Usuario.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'
        )

    def test_create_usuario(self):
        """Testa a criação de um novo usuário."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newuserpass'
        }
        response = self.client.post(reverse('usuario-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(username='newuser').exists())

    def test_update_usuario(self):
        """Testa a atualização de um usuário existente."""
        data = {
            'username': 'user1_updated',
            'email': 'user1_updated@example.com'
        }
        url = reverse('usuario-detail', args=[self.regular_user.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, 'user1_updated')
        self.assertEqual(self.regular_user.email, 'user1_updated@example.com')

    def test_delete_usuario(self):
        """Testa a exclusão de um usuário."""
        url = reverse('usuario-detail', args=[self.regular_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Usuario.objects.filter(id=self.regular_user.id).exists())

    def test_regular_user_permissions(self):
        """Testa se um usuário regular não pode criar ou deletar outros usuários."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'username': 'forbiddenuser',
            'email': 'forbidden@example.com',
            'password': 'forbiddenpass'
        }
        response = self.client.post(reverse('usuario-list'), data)
        print('response.data: '+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        url = reverse('usuario-detail', args=[self.admin_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)