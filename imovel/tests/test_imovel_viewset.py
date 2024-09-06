from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from imovel.models import Imovel, SituacaoFiscal, TransacaoImovel
from usuario.models import Usuario


class ImovelViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

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
            numero_registro='98765XYZ',
            disponibilidade=True
        )

    def test_create_imovel(self):
        url = reverse('imovel-list')
        data = {
            'nome': 'Casa Nova',
            'endereco': 'Rua Nova, 456',
            'bairro': 'Bairro Novo',
            'cidade': 'Recife',
            'estado': 'PE',
            'cep': '70000-000',
            'area_total': 200.00,
            'area_util': 180.00,
            'tipo_imovel': 'casa',
            'num_quartos': 3,
            'num_banheiros': 2,
            'num_vagas_garagem': 1,
            'ano_construcao': 2020,
            'numero_registro': '12345ABC',
            'disponibilidade': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Imovel.objects.count(), 2)

    def test_retrieve_imovel(self):
        url = reverse('imovel-detail', args=[self.imovel.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Casa de Praia')

    def test_update_imovel(self):
        url = reverse('imovel-detail', args=[self.imovel.id])
        data = {
            'nome': 'Casa de Verão Atualizada',
            'endereco': 'Rua Atualizada, 123',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.imovel.refresh_from_db()
        self.assertEqual(self.imovel.nome, 'Casa de Verão Atualizada')

    def test_delete_imovel(self):
        url = reverse('imovel-detail', args=[self.imovel.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Imovel.objects.count(), 0)

    def test_list_imoveis(self):
        url = reverse('imovel-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class SituacaoFiscalViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

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
            numero_registro='98765XYZ',
            disponibilidade=True
        )

        self.situacao_fiscal = SituacaoFiscal.objects.create(
            imovel=self.imovel,
            tipo='regular',
            descricao='Imóvel Regularizado',
            data_referencia='2024-01-01'
        )

    def test_create_situacao_fiscal(self):
        url = reverse('situacaofiscal-list')
        data = {
            'imovel': self.imovel.id,
            'tipo': 'iptu_atrasado',
            'descricao': 'IPTU está atrasado',
            'data_referencia': '2024-02-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SituacaoFiscal.objects.count(), 2)

    def test_retrieve_situacao_fiscal(self):
        url = reverse('situacaofiscal-detail', args=[self.situacao_fiscal.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo'], 'regular')

    def test_update_situacao_fiscal(self):
        url = reverse('situacaofiscal-detail', args=[self.situacao_fiscal.id])
        data = {
            'tipo': 'iptu_atrasado',
            'descricao': 'IPTU está atrasado agora'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.situacao_fiscal.refresh_from_db()
        self.assertEqual(self.situacao_fiscal.tipo, 'iptu_atrasado')

    def test_delete_situacao_fiscal(self):
        url = reverse('situacaofiscal-detail', args=[self.situacao_fiscal.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SituacaoFiscal.objects.count(), 0)

    def test_list_situacoes_fiscais(self):
        url = reverse('situacaofiscal-list') + f'?imovel_id={self.imovel.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_situacao_fiscal_choices(self):
        # Teste do método que retorna as opções de SITUACAO_FISCAL_CHOICES
        url = reverse('situacaofiscal-situacao-fiscal-choices')  # O nome da URL conforme o padrão gerado pelo router
        response = self.client.get(url)

        # Verifica se o status de retorno é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se o conteúdo do retorno é uma lista de tuplas
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)  # Verifica se há itens na lista

        # Verifica o primeiro item da lista
        expected_first_choice = ('regular', 'Imóvel Regular')
        self.assertEqual(response.data[0], expected_first_choice)


class TransacaoImovelViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

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
            numero_registro='98765XYZ',
            disponibilidade=True
        )

        self.transacao = TransacaoImovel.objects.create(
            imovel=self.imovel,
            tipo_transacao='venda',
            valor=500000.00,
            comissao=5.00,
            condicoes_pagamento='À vista',
            data_disponibilidade='2024-01-01'
        )

    def test_create_transacao_imovel(self):
        url = reverse('transacaoimovel-list')
        data = {
            'imovel': self.imovel.id,
            'tipo_transacao': 'aluguel',
            'valor': 3000.00,
            'comissao': 10.00,
            'condicoes_pagamento': 'Mensal',
            'data_disponibilidade': '2024-01-01',
        }
        #print('url '+str(url))
        #print('data: '+str(data))
        response = self.client.post(url, data, format='json')
        #print('response.data: '+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TransacaoImovel.objects.count(), 2)

    def test_retrieve_transacao_imovel(self):
        url = reverse('transacaoimovel-detail', args=[self.transacao.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo_transacao'], 'venda')

    def test_update_transacao_imovel(self):
        url = reverse('transacaoimovel-detail', args=[self.transacao.id])
        data = {
            'tipo_transacao': 'aluguel',
            'valor': 4000.00
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transacao.refresh_from_db()
        self.assertEqual(self.transacao.tipo_transacao, 'aluguel')

    def test_delete_transacao_imovel(self):
        url = reverse('transacaoimovel-detail', args=[self.transacao.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TransacaoImovel.objects.count(), 0)

    def test_list_transacoes_imovel(self):
        url = reverse('transacaoimovel-list') + f'?imovel_id={self.imovel.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_tipo_transacao_choices(self):
        # Teste do método que retorna as opções de TIPO_TRANSACAO_CHOICES
        url = reverse('transacaoimovel-tipo-transacao-choices')  # URL do método customizado
        response = self.client.get(url)

        # Verifica se o status de retorno é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verifica se o conteúdo do retorno é uma lista de dicionários
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)  # Verifica se a lista contém elementos

        # Verifica o formato do primeiro item da lista
        first_choice = response.data[0]
        self.assertIn('value', first_choice)
        self.assertIn('label', first_choice)

        # Verifica o primeiro item da lista se corresponde ao valor esperado
        expected_first_choice = {"value": "venda", "label": "Venda"}
        self.assertEqual(first_choice, expected_first_choice)
