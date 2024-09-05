from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from documentacao.models import DocumentoImovel
from imovel.models import Imovel
from usuario.models import Usuario
import datetime

class DocumentoImovelViewSetTest(APITestCase):

    def setUp(self):
        # Criação do cliente autenticado
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

        # Criação de um imóvel para associar aos documentos
        self.imovel = Imovel.objects.create(
            nome='Apartamento 101',
            endereco='Rua X, 123',
            bairro='Centro',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            area_total=80.00,
            area_util=65.00,
            tipo_imovel='apartamento',
            num_quartos=2,
            num_banheiros=2,
            num_vagas_garagem=1,
            ano_construcao=2015,
            numero_registro='12345ABC',
            disponibilidade=True
        )

    def test_create_documento_imovel(self):
        # Teste de criação de um documento de imóvel
        url = reverse('documentoimovel-list')
        arquivo = SimpleUploadedFile("matricula.pdf", b"file_content", content_type="application/pdf")
        data = {
            'imovel': self.imovel.id,
            'tipo_documento': 'matricula',
            'descricao': 'Matrícula do imóvel',
            'arquivo': arquivo,
            'data_emissao': '2024-01-01'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DocumentoImovel.objects.count(), 1)
        self.assertEqual(DocumentoImovel.objects.get().tipo_documento, 'matricula')

    def test_retrieve_documento_imovel(self):
        # Teste de recuperação de um documento de imóvel
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='cnd',
            descricao='Certidão Negativa de Débitos',
            arquivo=SimpleUploadedFile('certidao.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('documentoimovel-detail', args=[documento.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo_documento'], 'cnd')

    def test_update_documento_imovel(self):
        # Teste de atualização de um documento de imóvel
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='cnd',
            descricao='Certidão Negativa de Débitos',
            arquivo=SimpleUploadedFile('certidao.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('documentoimovel-detail', args=[documento.id])
        data = {
            'imovel': self.imovel.id,
            'tipo_documento': 'iptu',
            'descricao': 'Certidão Negativa de IPTU',
            'arquivo': SimpleUploadedFile("iptu.pdf", b"file_content", content_type="application/pdf"),
            'data_emissao': '2024-01-01'
        }
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        documento.refresh_from_db()
        self.assertEqual(documento.tipo_documento, 'iptu')

    def test_delete_documento_imovel(self):
        # Teste de deleção de um documento de imóvel
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='iptu',
            descricao='Certidão Negativa de IPTU',
            arquivo=SimpleUploadedFile('iptu.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('documentoimovel-detail', args=[documento.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DocumentoImovel.objects.count(), 0)

    def test_list_documento_imovel(self):
        # Teste de listagem de documentos filtrados por imóvel
        DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='matricula',
            descricao='Matrícula do imóvel',
            arquivo=SimpleUploadedFile('matricula.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='cnd',
            descricao='Certidão Negativa de Débitos',
            arquivo=SimpleUploadedFile('certidao.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('documentoimovel-list') + f'?imovel={self.imovel.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
