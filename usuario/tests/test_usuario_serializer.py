from django.test import TestCase
from usuario.models import Usuario
from usuario.serializers import UsuarioSerializer

class UsuarioSerializerTestCase(TestCase):

    def setUp(self):
        # Criando um usuário administrador e um usuário regular para os testes
        self.admin_user = Usuario.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        
        self.regular_user = Usuario.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'
        )

    def test_create_usuario(self):
        """Teste de criação de um novo usuário."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newuserpass'
        }
        serializer = UsuarioSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario = serializer.save()
        self.assertEqual(usuario.username, 'newuser')

    def test_read_usuario(self):
        """Teste de leitura dos detalhes de um usuário e suas permissões."""
        serializer = UsuarioSerializer(self.admin_user)
        data = serializer.data
        self.assertEqual(data['username'], 'admin')
        self.assertIn('permissoes', data)
        self.assertIsInstance(data['permissoes'], list)
        # Verifica se as permissões estão corretas
        self.assertIn('usuario.add_usuario', data['permissoes'])

    def test_update_usuario(self):
        """Teste de atualização de um usuário existente (PUT)."""
        data = {'username': 'user1_updated', 'email': 'user1_updated@example.com'}
        serializer = UsuarioSerializer(self.regular_user, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario_atualizado = serializer.save()
        self.assertEqual(usuario_atualizado.username, 'user1_updated')
        self.assertEqual(usuario_atualizado.email, 'user1_updated@example.com')

    def test_partial_update_usuario(self):
        """Teste de atualização parcial de um usuário existente (PATCH)."""
        data = {'first_name': 'PartiallyUpdated'}
        serializer = UsuarioSerializer(self.regular_user, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario_atualizado = serializer.save()
        self.assertEqual(usuario_atualizado.first_name, 'PartiallyUpdated')

    def test_delete_usuario(self):
        """Teste de deleção de um usuário."""
        usuario_id = self.regular_user.id
        self.regular_user.delete()
        with self.assertRaises(Usuario.DoesNotExist):
            Usuario.objects.get(id=usuario_id)

    def test_usuario_permissoes(self):
        """Teste específico para a consulta de permissões de um usuário."""
        serializer = UsuarioSerializer(self.admin_user)
        permissoes = serializer.data['permissoes']
        self.assertIsInstance(permissoes, list)
        # Verifica se as permissões retornadas estão corretas
        self.assertIn('auth.add_permission', permissoes)  # Exemplo de permissão presente
        self.assertIn('auth.view_permission', permissoes)



