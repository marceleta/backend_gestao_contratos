from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import PessoaFisica, Estado
from documentacao.models import DocumentoPessoaFisica
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
from usuario.models import Usuario
from rest_framework.test import APIClient

class DocPessoaFisicaViewSetTest(APITestCase):

    def setUp(self):

        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')
        self.pessoa_fisica = PessoaFisica.objects.create(
            nome='João da Silva',
            email='joao@example.com',
            telefone='12345-6789',
            endereco='Rua A',
            bairro='Centro',
            cidade='São Paulo',
            estado=self.estado,
            cep='12345-678',
            cpf='123.456.789-00',
            identidade='MG-12.345.678',
            orgao_expeditor='SSP-MG',
            data_nascimento=datetime.date(1980, 1, 1),
            estado_civil='Solteiro(a)',
            nacionalidade='Brasileiro'
        )

    def test_create_documento(self):
        url = reverse('docpessoafisica-list')
        arquivo = SimpleUploadedFile("cpf.pdf", b"file_content", content_type="application/pdf")
        data = {
            'pessoa_fisica': self.pessoa_fisica.id,
            'tipo_documento': 'CPF',
            'descricao': 'CPF de João da Silva',
            'arquivo': arquivo,
            'data_emissao': '2020-01-01'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DocumentoPessoaFisica.objects.count(), 1)
        self.assertEqual(DocumentoPessoaFisica.objects.get().tipo_documento, 'CPF')

    def test_retrieve_documento(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='CPF',
            descricao='CPF de João da Silva',
            arquivo=SimpleUploadedFile("cpf.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        url = reverse('docpessoafisica-detail', args=[documento.id])
        #print(url)
        response = self.client.get(url)
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo_documento'], 'CPF')

    def test_update_documento(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='CPF',
            descricao='CPF de João da Silva',
            arquivo=SimpleUploadedFile("cpf.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        url = reverse('docpessoafisica-detail', args=[documento.id])
        data = {
            'pessoa_fisica': self.pessoa_fisica.id,
            'tipo_documento': 'RG',
            'descricao': 'RG de João da Silva',
            'data_emissao': '2020-01-01',
            'arquivo': SimpleUploadedFile("cpf.pdf", b"file_content", content_type="application/pdf"),
        }
        response = self.client.put(url, data, format='multipart')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        documento.refresh_from_db()
        self.assertEqual(documento.tipo_documento, 'RG')

    def test_delete_documento(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='CPF',
            descricao='CPF de João da Silva',
            arquivo= SimpleUploadedFile("cpf.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        url = reverse('docpessoafisica-detail', args=[documento.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DocumentoPessoaFisica.objects.count(), 0)

    def test_list_documentos(self):
        DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='CPF',
            descricao='CPF de João da Silva',
            arquivo=SimpleUploadedFile("cpf.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='RG',
            descricao='RG de João da Silva',
            arquivo=SimpleUploadedFile("rg.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        #print('Documentos: '+str(DocumentoPessoaFisica.objects.all()))
        url = reverse('docpessoafisica-list') + f'?pessoa_fisica={self.pessoa_fisica.id}'
        #print(url)
        response = self.client.get(url)
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)




