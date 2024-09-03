from django.test import TestCase
from core.models import PessoaFisica, Estado
from documentacao.models import DocumentoPessoaFisica
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime

class DocPessoaFisicaTestCase(TestCase):

    def setUp(self):
        # Criação de objetos iniciais para os testes
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

    def test_create_documento_pessoa_fisica(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='CPF',
            descricao='CPF de João da Silva',
            arquivo=SimpleUploadedFile('cpf.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2020, 1, 1)
        )
        self.assertEqual(documento.tipo_documento, 'CPF')
        self.assertEqual(documento.descricao, 'CPF de João da Silva')
        self.assertEqual(documento.pessoa_fisica, self.pessoa_fisica)

    def test_read_documento_pessoa_fisica(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='RG',
            descricao='RG de João da Silva',
            arquivo=SimpleUploadedFile('rg.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2019, 5, 15)
        )
        documento_lido = DocumentoPessoaFisica.objects.get(id=documento.id)
        self.assertEqual(documento_lido.tipo_documento, 'RG')
        self.assertEqual(documento_lido.descricao, 'RG de João da Silva')

    def test_update_documento_pessoa_fisica(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='CNH',
            descricao='CNH de João da Silva',
            arquivo=SimpleUploadedFile('cnh.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2018, 3, 22)
        )
        documento.descricao = 'CNH atualizada de João da Silva'
        documento.save()
        documento_atualizado = DocumentoPessoaFisica.objects.get(id=documento.id)
        self.assertEqual(documento_atualizado.descricao, 'CNH atualizada de João da Silva')

    def test_delete_documento_pessoa_fisica(self):
        documento = DocumentoPessoaFisica.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            tipo_documento='Comprovante de Residência',
            descricao='Comprovante de Residência de João da Silva',
            arquivo=SimpleUploadedFile('residencia.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2021, 7, 10)
        )
        documento_id = documento.id
        documento.delete()
        with self.assertRaises(DocumentoPessoaFisica.DoesNotExist):
            DocumentoPessoaFisica.objects.get(id=documento_id)
