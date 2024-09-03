from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from documentacao.models import DocumentoPessoaJuridica
from usuario.models import Usuario
from core.models import PessoaJuridica, Estado
import datetime

class DocumentoPessoaJuridicaViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')
        self.pessoa_juridica = PessoaJuridica.objects.create(
            cnpj='12.345.678/0001-00',
            data_fundacao=datetime.date(2000, 1, 1),
            nome_fantasia='Empresa XYZ',
            nome='Empresa XYZ LTDA',
            endereco='Rua B',
            bairro='Centro',
            cidade='São Paulo',
            estado=self.estado,
            cep='12345-678',
            data_abertura=datetime.date(2000, 1, 15),
            inscricao_estadual='123456789',
            natureza_juridica='Sociedade Limitada',
            atividade_principal_cnae='47.11-3-01',
        )

    def test_create_documento(self):
        url = reverse('docpessoajuridica-list')
        arquivo = SimpleUploadedFile("contrato_social.pdf", b"file_content", content_type="application/pdf")
        data = {
            'pessoa_juridica': self.pessoa_juridica.id,
            'tipo_documento': 'contrato_social',
            'descricao': 'Contrato Social da Empresa XYZ',
            'arquivo': arquivo,
            'data_emissao': '2020-01-01'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DocumentoPessoaJuridica.objects.count(), 1)
        self.assertEqual(DocumentoPessoaJuridica.objects.get().tipo_documento, 'contrato_social')

    def test_retrieve_documento(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='contrato_social',
            descricao='Contrato Social da Empresa XYZ',
            arquivo=SimpleUploadedFile("contrato_social.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        url = reverse('docpessoajuridica-detail', args=[documento.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo_documento'], 'contrato_social')

    def test_update_documento(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='contrato_social',
            descricao='Contrato Social da Empresa XYZ',
            arquivo=SimpleUploadedFile("contrato_social.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        url = reverse('docpessoajuridica-detail', args=[documento.id])
        data = {
            'pessoa_juridica': self.pessoa_juridica.id,
            'tipo_documento': 'cert_negativa_deb_tributarios',
            'descricao': 'Certidão Negativa de Débitos Tributários',
            'data_emissao': '2020-01-01',
            'arquivo': SimpleUploadedFile("cert_negativa.pdf", b"file_content", content_type="application/pdf"),
        }
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        documento.refresh_from_db()
        self.assertEqual(documento.tipo_documento, 'cert_negativa_deb_tributarios')

    def test_delete_documento(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='contrato_social',
            descricao='Contrato Social da Empresa XYZ',
            arquivo= SimpleUploadedFile("contrato_social.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        url = reverse('docpessoajuridica-detail', args=[documento.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DocumentoPessoaJuridica.objects.count(), 0)

    def test_list_documentos(self):
        DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='contrato_social',
            descricao='Contrato Social da Empresa XYZ',
            arquivo=SimpleUploadedFile("contrato_social.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='cert_negativa_deb_tributarios',
            descricao='Certidão Negativa de Débitos Tributários',
            arquivo=SimpleUploadedFile("cert_negativa.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-01-01'
        )
        url = reverse('docpessoajuridica-list') + f'?pessoa_juridica={self.pessoa_juridica.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
