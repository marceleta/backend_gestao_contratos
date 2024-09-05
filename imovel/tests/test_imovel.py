from django.test import TestCase
from imovel.models import Imovel, TransacaoImovel
from datetime import datetime

class ImovelTestCase(TestCase):

    def setUp(self):
        # Criação de um imóvel para os testes
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

    def test_create_imovel(self):
        # Teste de criação do imóvel
        self.assertEqual(Imovel.objects.count(), 1)
        self.assertEqual(self.imovel.nome, 'Apartamento 101')
        self.assertEqual(self.imovel.tipo_imovel, 'apartamento')

    def test_read_imovel(self):
        # Teste de leitura do imóvel
        imovel = Imovel.objects.get(id=self.imovel.id)
        self.assertEqual(imovel.nome, 'Apartamento 101')
        self.assertEqual(imovel.cep, '01234-567')

    def test_update_imovel(self):
        # Teste de atualização do imóvel
        self.imovel.nome = 'Apartamento 202'
        self.imovel.save()
        imovel_atualizado = Imovel.objects.get(id=self.imovel.id)
        self.assertEqual(imovel_atualizado.nome, 'Apartamento 202')

    def test_delete_imovel(self):
        # Teste de exclusão do imóvel
        imovel_id = self.imovel.id
        self.imovel.delete()
        with self.assertRaises(Imovel.DoesNotExist):
            Imovel.objects.get(id=imovel_id)


class TransacaoImovelTestCase(TestCase):

    def setUp(self):
        # Criação de um imóvel para os testes de transação
        self.imovel = Imovel.objects.create(
            nome='Casa Verde',
            endereco='Rua Y, 456',
            bairro='Jardim',
            cidade='Rio de Janeiro',
            estado='RJ',
            cep='98765-432',
            area_total=150.00,
            area_util=120.00,
            tipo_imovel='casa',
            num_quartos=3,
            num_banheiros=2,
            num_vagas_garagem=2,
            ano_construcao=2010,
            numero_registro='67890DEF',
            disponibilidade=True
        )

        # Criação de uma transação associada ao imóvel
        self.transacao = TransacaoImovel.objects.create(
            imovel=self.imovel,
            tipo_transacao='venda',
            valor=600000.00,
            data_disponibilidade=datetime.now().date()
        )

    def test_create_transacao_imovel(self):
        # Teste de criação de uma transação
        self.assertEqual(TransacaoImovel.objects.count(), 1)
        self.assertEqual(self.transacao.tipo_transacao, 'venda')
        self.assertEqual(self.transacao.valor, 600000.00)

    def test_read_transacao_imovel(self):
        # Teste de leitura de uma transação
        transacao = TransacaoImovel.objects.get(id=self.transacao.id)
        self.assertEqual(transacao.imovel.nome, 'Casa Verde')
        self.assertEqual(transacao.tipo_transacao, 'venda')

    def test_update_transacao_imovel(self):
        # Teste de atualização de uma transação
        self.transacao.valor = 650000.00
        self.transacao.save()
        transacao_atualizada = TransacaoImovel.objects.get(id=self.transacao.id)
        self.assertEqual(transacao_atualizada.valor, 650000.00)

    def test_delete_transacao_imovel(self):
        # Teste de exclusão de uma transação
        transacao_id = self.transacao.id
        self.transacao.delete()
        with self.assertRaises(TransacaoImovel.DoesNotExist):
            TransacaoImovel.objects.get(id=transacao_id)