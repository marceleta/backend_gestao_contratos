from rest_framework import serializers
from rest_framework.test import APITestCase
from imovel.models import Imovel
from imovel.serializers import ImovelSerializer
from datetime import datetime

class ImovelSerializerTests(APITestCase):

    def setUp(self):
        # Dados do imóvel para os testes
        self.imovel_data = {
            'nome': 'Casa Azul',
            'endereco': 'Rua X, 123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01234-567',
            'area_total': 100.00,
            'area_util': 90.00,
            'tipo_imovel': 'casa',
            'num_quartos': 3,
            'num_banheiros': 2,
            'num_vagas_garagem': 1,
            'ano_construcao': 2010,
            'numero_registro': '12345ABC',
            'situacao_fiscal': 'OK',
            'certidoes_licencas': 'Certidão negativa',
            'disponibilidade': True,
            'data_cadastro': datetime.now()
        }
        self.imovel = Imovel.objects.create(**self.imovel_data)

    def test_serializer_create_imovel(self):
        # Testando a criação via serializer
        serializer = ImovelSerializer(data=self.imovel_data)
        print(str(serializer))
        self.assertTrue(serializer.is_valid())
        imovel = serializer.save()
        self.assertEqual(imovel.nome, 'Casa Azul')
        self.assertEqual(Imovel.objects.count(), 2)  # Já existe um no setUp

    def test_serializer_read_imovel(self):
        # Testando a leitura dos dados via serializer
        serializer = ImovelSerializer(self.imovel)
        data = serializer.data
        self.assertEqual(data['nome'], 'Casa Azul')
        self.assertEqual(data['cidade'], 'São Paulo')

    def test_serializer_update_imovel(self):
        # Testando a atualização dos dados via serializer
        update_data = self.imovel_data.copy()
        update_data['nome'] = 'Casa Verde'
        serializer = ImovelSerializer(instance=self.imovel, data=update_data)
        self.assertTrue(serializer.is_valid())
        updated_imovel = serializer.save()
        self.assertEqual(updated_imovel.nome, 'Casa Verde')

    def test_serializer_partial_update_imovel(self):
        # Testando a atualização parcial via serializer
        partial_update_data = {'nome': 'Casa Vermelha'}
        serializer = ImovelSerializer(instance=self.imovel, data=partial_update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_imovel = serializer.save()
        self.assertEqual(updated_imovel.nome, 'Casa Vermelha')

    def test_serializer_delete_imovel(self):
        # Testando a deleção do imóvel via serializer
        imovel_id = self.imovel.id
        self.imovel.delete()
        with self.assertRaises(Imovel.DoesNotExist):
            Imovel.objects.get(id=imovel_id)
