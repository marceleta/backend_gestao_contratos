from django.test import TestCase
from django.utils import timezone
from imovel.models import Imovel, SituacaoFiscal, TransacaoImovel
import datetime

class ImovelTestCase(TestCase):

    def setUp(self):
        # Criação de um objeto Imovel
        self.imovel = Imovel.objects.create(
            nome='Casa de Praia',
            endereco='Rua do Sol, 123',
            bairro='Beira Mar',
            cidade='Fortaleza',
            estado='CE',
            cep='60000-000',
            area_total=150.00,
            area_util=130.00,
            tipo_imovel='casa',
            num_quartos=4,
            num_banheiros=3,
            num_vagas_garagem=2,
            ano_construcao=2018,
            caracteristicas_adicionais='Piscina, churrasqueira',
            latitude=-3.71722,
            longitude=-38.5434,
            status='disponivel',
            tipo_construcao='novo',
            numero_registro='12345ABC'
        )

    def test_create_imovel(self):
        # Teste de criação de um imóvel
        self.assertEqual(Imovel.objects.count(), 1)
        self.assertEqual(self.imovel.nome, 'Casa de Praia')

    def test_read_imovel(self):
        # Teste de leitura de um imóvel
        imovel = Imovel.objects.get(id=self.imovel.id)
        self.assertEqual(imovel.nome, 'Casa de Praia')

    def test_update_imovel(self):
        # Teste de atualização de um imóvel
        self.imovel.nome = 'Casa de Campo'
        self.imovel.save()
        self.assertEqual(self.imovel.nome, 'Casa de Campo')

    def test_delete_imovel(self):
        # Teste de deleção de um imóvel
        self.imovel.delete()
        self.assertEqual(Imovel.objects.count(), 0)


class SituacaoFiscalTestCase(TestCase):

    def setUp(self):
        # Criando um objeto Imovel
        self.imovel = Imovel.objects.create(
            nome='Casa de Praia',
            endereco='Rua do Sol, 123',
            bairro='Beira Mar',
            cidade='Fortaleza',
            estado='CE',
            cep='60000-000',
            area_total=150.00,
            area_util=130.00,
            tipo_imovel='casa',
            num_quartos=4,
            num_banheiros=3,
            num_vagas_garagem=2,
            ano_construcao=2018,
            numero_registro='12345ABC'
        )
        
        # Criando um objeto SituacaoFiscal
        self.situacao_fiscal = SituacaoFiscal.objects.create(
            imovel=self.imovel,
            tipo='iptu_atrasado',
            descricao='IPTU em atraso desde 2020',
            data_referencia=datetime.date(2021, 1, 1)
        )

    def test_create_situacao_fiscal(self):
        # Teste de criação de uma situação fiscal
        self.assertEqual(SituacaoFiscal.objects.count(), 1)
        self.assertEqual(self.situacao_fiscal.tipo, 'iptu_atrasado')

    def test_read_situacao_fiscal(self):
        # Teste de leitura de uma situação fiscal
        situacao = SituacaoFiscal.objects.get(id=self.situacao_fiscal.id)
        self.assertEqual(situacao.descricao, 'IPTU em atraso desde 2020')

    def test_update_situacao_fiscal(self):
        # Teste de atualização de uma situação fiscal
        self.situacao_fiscal.descricao = 'IPTU em atraso desde 2021'
        self.situacao_fiscal.save()
        self.assertEqual(self.situacao_fiscal.descricao, 'IPTU em atraso desde 2021')

    def test_delete_situacao_fiscal(self):
        # Teste de deleção de uma situação fiscal
        self.situacao_fiscal.delete()
        self.assertEqual(SituacaoFiscal.objects.count(), 0)


class TransacaoImovelTestCase(TestCase):

    def setUp(self):
        # Criando um objeto Imovel
        self.imovel = Imovel.objects.create(
            nome='Casa de Praia',
            endereco='Rua do Sol, 123',
            bairro='Beira Mar',
            cidade='Fortaleza',
            estado='CE',
            cep='60000-000',
            area_total=150.00,
            area_util=130.00,
            tipo_imovel='casa',
            num_quartos=4,
            num_banheiros=3,
            num_vagas_garagem=2,
            ano_construcao=2018,
            numero_registro='12345ABC'
        )
        
        # Criando um objeto TransacaoImovel
        self.transacao_imovel = TransacaoImovel.objects.create(
            imovel=self.imovel,
            tipo_transacao='venda',
            valor=500000.00,
            comissao=5.00,
            condicoes_pagamento='Entrada + 24x sem juros',
            data_disponibilidade=datetime.date(2022, 12, 1)
        )

    def test_create_transacao_imovel(self):
        # Teste de criação de uma transação imobiliária
        self.assertEqual(TransacaoImovel.objects.count(), 1)
        self.assertEqual(self.transacao_imovel.tipo_transacao, 'venda')

    def test_read_transacao_imovel(self):
        # Teste de leitura de uma transação imobiliária
        transacao = TransacaoImovel.objects.get(id=self.transacao_imovel.id)
        self.assertEqual(transacao.valor, 500000.00)

    def test_update_transacao_imovel(self):
        # Teste de atualização de uma transação imobiliária
        self.transacao_imovel.valor = 550000.00
        self.transacao_imovel.save()
        self.assertEqual(self.transacao_imovel.valor, 550000.00)

    def test_delete_transacao_imovel(self):
        # Teste de deleção de uma transação imobiliária
        self.transacao_imovel.delete()
        self.assertEqual(TransacaoImovel.objects.count(), 0)
