from django.test import TestCase
from rest_framework.test import APIClient
from imovel.models import Imovel, SituacaoFiscal, TransacaoImovel
from imovel.serializers import ImovelSerializer, SituacaoFiscalSerializer, TransacaoImovelSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime

class ImovelSerializerTestCase(TestCase):

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
            numero_registro='12345',
            cep='12345-678'
        )

    def test_create_imovel(self):
        # Teste de criação de imóvel com dados válidos
        data = {
            'nome': 'Imóvel Novo',
            'endereco': 'Rua Nova, 456',
            'bairro': 'Bairro Novo',
            'cidade': 'Cidade Nova',
            'estado': 'RJ',
            'cep': '65432-876',
            'area_total': 200.00,
            'area_util': 180.00,
            'tipo_imovel': 'casa',
            'num_quartos': 4,
            'num_banheiros': 3,
            'num_vagas_garagem': 2,
            'ano_construcao': 2015,
            'caracteristicas_adicionais': 'Piscina e jardim',
            'numero_registro': '67890'
        }
        serializer = ImovelSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        imovel = serializer.save()
        self.assertEqual(imovel.nome, 'Imóvel Novo')

    def test_read_imovel(self):
        # Teste de leitura de um imóvel
        serializer = ImovelSerializer(self.imovel)
        data = serializer.data
        self.assertEqual(data['nome'], 'Imóvel Teste')

    def test_update_imovel(self):
        # Teste de atualização de um imóvel
        data = {'nome': 'Imóvel Atualizado'}
        serializer = ImovelSerializer(self.imovel, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        imovel_atualizado = serializer.save()
        self.assertEqual(imovel_atualizado.nome, 'Imóvel Atualizado')

    def test_delete_imovel(self):
        # Teste de deleção de um imóvel
        imovel_id = self.imovel.id
        self.imovel.delete()
        with self.assertRaises(Imovel.DoesNotExist):
            Imovel.objects.get(id=imovel_id)


class SituacaoFiscalSerializerTestCase(TestCase):

    def setUp(self):
        # Criando um imóvel e situação fiscal para teste
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
            numero_registro='12345',
            cep='12345-678'
        )
        self.situacao_fiscal = SituacaoFiscal.objects.create(
            imovel=self.imovel,
            tipo='iptu_atrasado',
            descricao='IPTU em atraso desde 2020',
            data_referencia=datetime.date(2021, 1, 1)
        )

    def test_create_situacao_fiscal(self):
        # Teste de criação de situação fiscal
        data = {
            'imovel': self.imovel.id,
            'tipo': 'cnd_disponivel',
            'descricao': 'Certidão Negativa de Débitos disponível',
            'data_referencia': '2023-01-01'
        }
        serializer = SituacaoFiscalSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        situacao_fiscal = serializer.save()
        self.assertEqual(situacao_fiscal.tipo, 'cnd_disponivel')

    def test_read_situacao_fiscal(self):
        # Teste de leitura de uma situação fiscal
        serializer = SituacaoFiscalSerializer(self.situacao_fiscal)
        data = serializer.data
        self.assertEqual(data['tipo'], 'iptu_atrasado')

    def test_update_situacao_fiscal(self):
        # Teste de atualização de uma situação fiscal
        data = {'tipo': 'cnd_disponivel'}
        serializer = SituacaoFiscalSerializer(self.situacao_fiscal, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        situacao_atualizada = serializer.save()
        self.assertEqual(situacao_atualizada.tipo, 'cnd_disponivel')

    def test_delete_situacao_fiscal(self):
        # Teste de deleção de uma situação fiscal
        situacao_id = self.situacao_fiscal.id
        self.situacao_fiscal.delete()
        with self.assertRaises(SituacaoFiscal.DoesNotExist):
            SituacaoFiscal.objects.get(id=situacao_id)


class TransacaoImovelSerializerTestCase(TestCase):

    def setUp(self):
        # Criando um imóvel e uma transação para teste
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
            numero_registro='12345',
            cep='12345-678'
        )
        self.transacao_imovel = TransacaoImovel.objects.create(
            imovel=self.imovel,
            tipo_transacao='venda',
            valor=500000.00,
            comissao=5.00,
            condicoes_pagamento='Entrada + 24x',
            data_disponibilidade=datetime.date(2022, 12, 1)
        )

    def test_create_transacao_imovel(self):
        # Teste de criação de uma transação imobiliária
        data = {
            'imovel': self.imovel.id,
            'tipo_transacao': 'aluguel',
            'valor': 2500.00,
            'comissao': 10.00,
            'condicoes_pagamento': 'Mensal',
            'data_disponibilidade': '2023-05-01'
        }
        serializer = TransacaoImovelSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        transacao_imovel = serializer.save()
        self.assertEqual(transacao_imovel.tipo_transacao, 'aluguel')

    def test_read_transacao_imovel(self):
        # Teste de leitura de uma transação
        serializer = TransacaoImovelSerializer(self.transacao_imovel)
        data = serializer.data
        self.assertEqual(data['tipo_transacao'], 'venda')

    def test_update_transacao_imovel(self):
        # Teste de atualização de uma transação
        data = {'tipo_transacao': 'aluguel', 'valor': 3000.00}
        serializer = TransacaoImovelSerializer(self.transacao_imovel, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        transacao_atualizada = serializer.save()
        self.assertEqual(transacao_atualizada.tipo_transacao, 'aluguel')

    def test_delete_transacao_imovel(self):
        # Teste de deleção de uma transação
        transacao_id = self.transacao_imovel.id
        self.transacao_imovel.delete()
        with self.assertRaises(TransacaoImovel.DoesNotExist):
            TransacaoImovel.objects.get(id=transacao_id)

