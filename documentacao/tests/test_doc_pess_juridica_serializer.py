from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from documentacao.models import DocumentoPessoaJuridica
from core.models import Estado, PessoaJuridica
from documentacao.serializers import DocPessoaJuridicaSerializer
import datetime
from usuario.models import Usuario
from rest_framework.test import APIClient

class DocPessoaJuridicaSerializerTestCase(TestCase):

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

    def test_serializer_valid_data(self):
        arquivo = SimpleUploadedFile("contrato_social.pdf", b"file_content", content_type="application/pdf")
        data = {
            'pessoa_juridica': self.pessoa_juridica.id,
            'tipo_documento': 'contrato_social',
            'descricao': 'Contrato Social da Empresa XYZ',
            'arquivo': arquivo,
            'data_emissao': '2020-01-01'
        }
        serializer = DocPessoaJuridicaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento = serializer.save()
        self.assertEqual(documento.tipo_documento, 'contrato_social')
        self.assertEqual(documento.descricao, 'Contrato Social da Empresa XYZ')

    def test_serializer_invalid_extension(self):
        arquivo = SimpleUploadedFile("contrato_social.exe", b"file_content", content_type="application/octet-stream")
        data = {
            'pessoa_juridica': self.pessoa_juridica.id,
            'tipo_documento': 'contrato_social',
            'descricao': 'Contrato Social da Empresa XYZ',
            'arquivo': arquivo,
            'data_emissao': '2020-01-01'
        }
        serializer = DocPessoaJuridicaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('arquivo', serializer.errors)

    def test_create_documento_pessoa_juridica(self):
        arquivo = SimpleUploadedFile("cert_negativa.pdf", b"file_content", content_type="application/pdf")
        data = {
            'pessoa_juridica': self.pessoa_juridica.id,
            'tipo_documento': 'cert_negativa_deb_tributarios',
            'descricao': 'Certidão Negativa de Débitos Tributários',
            'arquivo': arquivo,
            'data_emissao': '2020-02-01'
        }
        serializer = DocPessoaJuridicaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento = serializer.save()
        self.assertEqual(documento.tipo_documento, 'cert_negativa_deb_tributarios')
        self.assertEqual(documento.descricao, 'Certidão Negativa de Débitos Tributários')

    def test_read_documento_pessoa_juridica(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='cert_negativa_deb_tributarios',
            descricao='Certidão Negativa de Débitos Tributários',
            arquivo=SimpleUploadedFile("cert_negativa.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-02-01'
        )
        serializer = DocPessoaJuridicaSerializer(documento)
        data = serializer.data
        self.assertEqual(data['tipo_documento'], 'cert_negativa_deb_tributarios')
        self.assertEqual(data['descricao'], 'Certidão Negativa de Débitos Tributários')

    def test_update_documento_pessoa_juridica(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='cert_negativa_deb_tributarios',
            descricao='Certidão Negativa de Débitos Tributários',
            arquivo=SimpleUploadedFile("cert_negativa.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-02-01'
        )
        data = {
            'tipo_documento': 'cert_regul_fgts',
            'descricao': 'Certidão de Regularidade FGTS',
        }
        serializer = DocPessoaJuridicaSerializer(documento, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento_atualizado = serializer.save()
        self.assertEqual(documento_atualizado.tipo_documento, 'cert_regul_fgts')
        self.assertEqual(documento_atualizado.descricao, 'Certidão de Regularidade FGTS')

    def test_delete_documento_pessoa_juridica(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='cert_negativa_deb_tributarios',
            descricao='Certidão Negativa de Débitos Tributários',
            arquivo=SimpleUploadedFile("cert_negativa.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-02-01'
        )
        documento_id = documento.id
        documento.delete()
        with self.assertRaises(DocumentoPessoaJuridica.DoesNotExist):
            DocumentoPessoaJuridica.objects.get(id=documento_id)
