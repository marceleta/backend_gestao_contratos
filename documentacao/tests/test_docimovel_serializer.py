from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from documentacao.serializers import DocImovelSerializer
from documentacao.models import DocumentoImovel
from imovel.models import Imovel
import datetime

class DocImovelSerializerTestCase(TestCase):

    def setUp(self):
        # Criando um imóvel para ser usado nos testes
        self.imovel = Imovel.objects.create(
            nome='Imóvel Teste',
            endereco='Rua Teste, 123',
            bairro='Centro',
            cidade='Cidade Teste',
            estado='SP',
            area_total=120.00,
            area_util=100.00,
            tipo_imovel='casa',
            num_quartos=3,
            num_banheiros=2,
            num_vagas_garagem=2,
            ano_construcao=2010,
            caracteristicas_adicionais='Piscina, churrasqueira',
            latitude=-23.55052,
            longitude=-46.633308,
            status='disponivel',
            tipo_construcao='novo',
            numero_registro='12345',
            cep='12345-678'
        )

    def test_serializer_valid_data(self):
        arquivo = SimpleUploadedFile("matricula.pdf", b"file_content", content_type="application/pdf")
        data = {
            'imovel': self.imovel.id,
            'tipo_documento': 'matricula',
            'descricao': 'Matrícula do imóvel',
            'arquivo': arquivo,
            'data_emissao': '2024-01-01'
        }
        serializer = DocImovelSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento = serializer.save()
        self.assertEqual(documento.tipo_documento, 'matricula')
        self.assertEqual(documento.descricao, 'Matrícula do imóvel')

    def test_serializer_invalid_extension(self):
        arquivo = SimpleUploadedFile("matricula.exe", b"file_content", content_type="application/octet-stream")
        data = {
            'imovel': self.imovel.id,
            'tipo_documento': 'matricula',
            'descricao': 'Matrícula do imóvel',
            'arquivo': arquivo,
            'data_emissao': '2024-01-01'
        }
        serializer = DocImovelSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('arquivo', serializer.errors)

    def test_create_documento_imovel(self):
        arquivo = SimpleUploadedFile("certidao.pdf", b"file_content", content_type="application/pdf")
        data = {
            'imovel': self.imovel.id,
            'tipo_documento': 'cnd',
            'descricao': 'Certidão Negativa de Débitos',
            'arquivo': arquivo,
            'data_emissao': '2024-02-01'
        }
        serializer = DocImovelSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento = serializer.save()
        self.assertEqual(documento.tipo_documento, 'cnd')
        self.assertEqual(documento.descricao, 'Certidão Negativa de Débitos')

    def test_read_documento_imovel(self):
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='cnd',
            descricao='Certidão Negativa de Débitos',
            arquivo=SimpleUploadedFile("certidao.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2024-02-01'
        )
        serializer = DocImovelSerializer(documento)
        data = serializer.data
        self.assertEqual(data['tipo_documento'], 'cnd')
        self.assertEqual(data['descricao'], 'Certidão Negativa de Débitos')

    def test_update_documento_imovel(self):
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='escritura',
            descricao='Escritura Pública do Imóvel',
            arquivo=SimpleUploadedFile("escritura.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2024-02-01'
        )
        data = {
            'tipo_documento': 'matricula',
            'descricao': 'Matrícula do Imóvel Atualizada',
        }
        serializer = DocImovelSerializer(documento, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento_atualizado = serializer.save()
        self.assertEqual(documento_atualizado.tipo_documento, 'matricula')
        self.assertEqual(documento_atualizado.descricao, 'Matrícula do Imóvel Atualizada')

    def test_delete_documento_imovel(self):
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='iptu',
            descricao='Certidão Negativa de IPTU',
            arquivo=SimpleUploadedFile("iptu.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2024-02-01'
        )
        documento_id = documento.id
        documento.delete()
        with self.assertRaises(DocumentoImovel.DoesNotExist):
            DocumentoImovel.objects.get(id=documento_id)
