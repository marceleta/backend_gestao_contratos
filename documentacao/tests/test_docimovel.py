from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from imovel.models import Imovel
from documentacao.models import DocumentoImovel
import datetime

class DocumentoImovelTestCase(TestCase):

    def setUp(self):
        # Criação de um imóvel completo para associar aos documentos
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
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='matricula',
            descricao='Matrícula do Imóvel',
            arquivo=SimpleUploadedFile('matricula.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2021, 1, 1)
        )
        self.assertEqual(documento.tipo_documento, 'matricula')
        self.assertEqual(documento.descricao, 'Matrícula do Imóvel')
        self.assertEqual(documento.imovel, self.imovel)


    def test_read_documento_imovel(self):
        # Teste de leitura de um documento de imóvel
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='cert_negativa_iptu',
            descricao='Certidão Negativa de IPTU',
            arquivo=SimpleUploadedFile('iptu.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2021, 6, 15)
        )
        documento_lido = DocumentoImovel.objects.get(id=documento.id)
        self.assertEqual(documento_lido.tipo_documento, 'cert_negativa_iptu')
        self.assertEqual(documento_lido.descricao, 'Certidão Negativa de IPTU')

    def test_update_documento_imovel(self):
        # Teste de atualização de um documento de imóvel
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='habitese',
            descricao='Habite-se do Imóvel',
            arquivo=SimpleUploadedFile('habitese.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2020, 11, 22)
        )
        documento.descricao = 'Habite-se atualizado'
        documento.save()
        documento_atualizado = DocumentoImovel.objects.get(id=documento.id)
        self.assertEqual(documento_atualizado.descricao, 'Habite-se atualizado')

    def test_delete_documento_imovel(self):
        # Teste de deleção de um documento de imóvel
        documento = DocumentoImovel.objects.create(
            imovel=self.imovel,
            tipo_documento='recibo_itbi',
            descricao='Recibo de ITBI',
            arquivo=SimpleUploadedFile('itbi.pdf', b'conteudo do arquivo', content_type='application/pdf'),
            data_emissao=datetime.date(2020, 7, 10)
        )
        documento_id = documento.id
        documento.delete()
        with self.assertRaises(DocumentoImovel.DoesNotExist):
            DocumentoImovel.objects.get(id=documento_id)
