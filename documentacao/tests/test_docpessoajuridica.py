from django.test import TestCase
from core.models import PessoaJuridica, Estado
from documentacao.models import DocumentoPessoaJuridica
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime

class DocPessoaJuridicaTestCase(TestCase):

    def setUp(self):
        # Criação de objetos iniciais para os testes
        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')
        self.pessoa_juridica = PessoaJuridica.objects.create(
            nome='Empresa ABC',
            email='empresa@example.com',
            telefone='12345-6789',
            endereco='Rua B',
            bairro='Centro',
            cidade='São Paulo',
            estado=self.estado,
            cep='12345-678',
            cnpj='12.345.678/0001-00',
            data_fundacao=datetime.date(2000, 1, 1),
            nome_fantasia='Fantasia ABC',
            inscricao_estadual='123456789',
            natureza_juridica='Sociedade Anônima',
            atividade_principal_cnae='62.01-1-00'
        )

    def test_create_documento_pessoa_juridica(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='CNPJ',
            descricao='CNPJ da Empresa ABC',
            arquivo=SimpleUploadedFile('cnpj.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2021, 1, 1)
        )
        self.assertEqual(documento.tipo_documento, 'CNPJ')
        self.assertEqual(documento.descricao, 'CNPJ da Empresa ABC')
        self.assertEqual(documento.pessoa_juridica, self.pessoa_juridica)

    def test_read_documento_pessoa_juridica(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='Contrato Social',
            descricao='Contrato Social da Empresa ABC',
            arquivo=SimpleUploadedFile('contrato_social.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2020, 5, 15)
        )
        documento_lido = DocumentoPessoaJuridica.objects.get(id=documento.id)
        self.assertEqual(documento_lido.tipo_documento, 'Contrato Social')
        self.assertEqual(documento_lido.descricao, 'Contrato Social da Empresa ABC')

    def test_update_documento_pessoa_juridica(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='Certidão Negativa de Débitos Tributários',
            descricao='Certidão Negativa de Débitos Tributários da Empresa ABC',
            arquivo=SimpleUploadedFile('certidao_negativa.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2019, 3, 22)
        )
        documento.descricao = 'Certidão Negativa Atualizada da Empresa ABC'
        documento.save()
        documento_atualizado = DocumentoPessoaJuridica.objects.get(id=documento.id)
        self.assertEqual(documento_atualizado.descricao, 'Certidão Negativa Atualizada da Empresa ABC')

    def test_delete_documento_pessoa_juridica(self):
        documento = DocumentoPessoaJuridica.objects.create(
            pessoa_juridica=self.pessoa_juridica,
            tipo_documento='Certidão Regularidade FGTS',
            descricao='Certidão Regularidade FGTS da Empresa ABC',
            arquivo=SimpleUploadedFile('fgts.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2021, 7, 10)
        )
        documento_id = documento.id
        documento.delete()
        with self.assertRaises(DocumentoPessoaJuridica.DoesNotExist):
            DocumentoPessoaJuridica.objects.get(id=documento_id)
