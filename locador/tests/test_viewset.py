from django.test import TestCase
from rest_framework.test import APIClient
from usuario.models import Usuario
from rest_framework import status
from django.urls import reverse
from locador.models import Locador
from core.models import PessoaFisica, Estado
from django.contrib.contenttypes.models import ContentType

class LocadorViewSetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)  # Autentica o cliente de teste
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        self.pessoa_fisica = PessoaFisica.objects.create(
            nome="João da Silva",
            email="joao@example.com",
            telefone="12345-6789",
            endereco="Rua A",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="12345-678",
            cpf="123.456.789-00",
            identidade="MG-12.345.678",
            orgao_expeditor="SSP-MG",
            data_nascimento="1980-01-01",
            estado_civil="Solteiro(a)",
            nacionalidade="Brasileiro"
        )
        self.content_type = ContentType.objects.get_for_model(PessoaFisica)
        self.locador_data = {
            'content_type': self.content_type.id,
            'object_id': self.pessoa_fisica.id
        }
        self.url = reverse('locador-list')

    def test_create_locador(self):
        response = self.client.post(self.url, self.locador_data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Locador.objects.count(), 1)
        self.assertEqual(Locador.objects.get().content_object, self.pessoa_fisica)

    def test_read_locador(self):
        locador = Locador.objects.create(content_type=self.content_type, object_id=self.pessoa_fisica.id)
        url = reverse('locador-detail', args=[locador.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['object_id'], self.pessoa_fisica.id)

    def test_update_locador(self):
        locador = Locador.objects.create(content_type=self.content_type, object_id=self.pessoa_fisica.id)
        nova_pessoa_fisica = PessoaFisica.objects.create(
            nome="Maria Silva",
            email="maria@example.com",
            telefone="12345-6799",
            endereco="Rua B",
            bairro="Centro",
            cidade="Rio de Janeiro",
            estado=self.estado,
            cep="12345-679",
            cpf="123.456.789-01",
            identidade="RJ-12.345.679",
            orgao_expeditor="SSP-RJ",
            data_nascimento="1990-01-01",
            estado_civil="Casado(a)",
            nacionalidade="Brasileiro"
        )
        nova_content_type = ContentType.objects.get_for_model(PessoaFisica)
        update_data = {
            'content_type': nova_content_type.id,
            'object_id': nova_pessoa_fisica.id
        }
        url = reverse('locador-detail', args=[locador.id])
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        locador.refresh_from_db()
        self.assertEqual(locador.content_object, nova_pessoa_fisica)

    def test_delete_locador(self):
        locador = Locador.objects.create(content_type=self.content_type, object_id=self.pessoa_fisica.id)
        url = reverse('locador-detail', args=[locador.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Locador.objects.count(), 0)


 