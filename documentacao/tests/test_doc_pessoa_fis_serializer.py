from django.test import TestCase
from core.models import PessoaFisica, Estado
from documentacao.models import DocumentoPessoaFisica
from documentacao.serializers import DocPessoaFisicaSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime

class DocPessoaFisicaSerializerTestCase(TestCase):

    def setUp(self):
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

    def test_serializer_valid_data(self):
        arquivo = SimpleUploadedFile("cpf.pdf", b"file_content", content_type="application/pdf")
        data = {
            'pessoa_fisica': self.pessoa_fisica.id,
            'tipo_documento': 'CPF',
            'descricao': 'CPF de João da Silva',
            'arquivo': arquivo,
            'data_emissao': '2020-01-01'
        }
        serializer = DocPessoaFisicaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento = serializer.save()
        self.assertEqual(documento.tipo_documento, 'CPF')
        self.assertEqual(documento.descricao, 'CPF de João da Silva')

    def test_serializer_invalid_extension(self):
        arquivo = SimpleUploadedFile("cpf.exe", b"file_content", content_type="application/octet-stream")
        data = {
            'pessoa_fisica': self.pessoa_fisica.id,
            'tipo_documento': 'CPF',
            'descricao': 'CPF de João da Silva',
            'arquivo': arquivo,
            'data_emissao': '2020-01-01'
        }
        serializer = DocPessoaFisicaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('arquivo', serializer.errors)

    def test_create_documento_pessoa_fisica(self):
        arquivo = SimpleUploadedFile("rg.pdf", b"file_content", content_type="application/pdf")
        data = {
            'pessoa_fisica': self.pessoa_fisica.id,
            'tipo_documento': 'RG',
            'descricao': 'RG de João da Silva',
            'arquivo': arquivo,
            'data_emissao': '2020-02-01'
        }
        serializer = DocPessoaFisicaSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento = serializer.save()
        self.assertEqual(documento.tipo_documento, 'RG')
        self.assertEqual(documento.descricao, 'RG de João da Silva')


    def test_read_documento_pessoa_fisica(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='RG',
            descricao='RG de João da Silva',
            arquivo=SimpleUploadedFile("rg.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-02-01'
        )
        serializer = DocPessoaFisicaSerializer(documento)
        data = serializer.data
        self.assertEqual(data['tipo_documento'], 'RG')
        self.assertEqual(data['descricao'], 'RG de João da Silva')

    def test_update_documento_pessoa_fisica(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='RG',
            descricao='RG de João da Silva',
            arquivo=SimpleUploadedFile("rg.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-02-01'
        )
        data = {
            'tipo_documento': 'CNH',
            'descricao': 'CNH de João da Silva',
        }
        serializer = DocPessoaFisicaSerializer(documento, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        documento_atualizado = serializer.save()
        self.assertEqual(documento_atualizado.tipo_documento, 'CNH')
        self.assertEqual(documento_atualizado.descricao, 'CNH de João da Silva')

    
    def test_delete_documento_pessoa_fisica(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='RG',
            descricao='RG de João da Silva',
            arquivo=SimpleUploadedFile("rg.pdf", b"file_content", content_type="application/pdf"),
            data_emissao='2020-02-01'
        )
        documento_id = documento.id
        documento.delete()
        with self.assertRaises(DocumentoPessoaFisica.DoesNotExist):
            DocumentoPessoaFisica.objects.get(id=documento_id)



    


