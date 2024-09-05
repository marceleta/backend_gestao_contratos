from django.test import TestCase
from rest_framework.test import APIClient
from documentacao.models import FotosVideoImovel
from imovel.models import Imovel
from documentacao.serializers import FotosVideoImovelSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime

class FotosVideoImovelSerializerTestCase(TestCase):

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
        arquivo = SimpleUploadedFile("foto_drone.jpg", b"file_content", content_type="image/jpeg")
        data = {
            'imovel': self.imovel.id,
            'tipo_midia': 'foto_drone',
            'formato': 'imagem',
            'descricao': 'Foto aérea do imóvel',
            'arquivo': arquivo,
            'data_emissao': '2024-01-01'
        }
        serializer = FotosVideoImovelSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        midia = serializer.save()
        self.assertEqual(midia.tipo_midia, 'foto_drone')
        self.assertEqual(midia.formato, 'imagem')

    def test_serializer_invalid_extension(self):
        arquivo = SimpleUploadedFile("foto_drone.exe", b"file_content", content_type="application/octet-stream")
        data = {
            'imovel': self.imovel.id,
            'tipo_midia': 'foto_drone',
            'formato': 'imagem',
            'descricao': 'Foto aérea do imóvel',
            'arquivo': arquivo,
            'data_emissao': '2024-01-01'
        }
        serializer = FotosVideoImovelSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('arquivo', serializer.errors)

    def test_create_fotos_video_imovel(self):
        arquivo = SimpleUploadedFile("video_drone.mp4", b"file_content", content_type="video/mp4")
        data = {
            'imovel': self.imovel.id,
            'tipo_midia': 'video_drone',
            'formato': 'video',
            'descricao': 'Vídeo aéreo com drone do imóvel',
            'arquivo': arquivo,
            'data_emissao': '2024-02-01'
        }
        serializer = FotosVideoImovelSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        midia = serializer.save()
        self.assertEqual(midia.tipo_midia, 'video_drone')
        self.assertEqual(midia.formato, 'video')

    def test_read_fotos_video_imovel(self):
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_profissional',
            formato='imagem',
            descricao='Foto profissional do imóvel',
            arquivo=SimpleUploadedFile("foto_profissional.jpg", b"file_content", content_type="image/jpeg"),
            data_emissao='2024-02-01'
        )
        serializer = FotosVideoImovelSerializer(midia)
        data = serializer.data
        self.assertEqual(data['tipo_midia'], 'foto_profissional')
        self.assertEqual(data['descricao'], 'Foto profissional do imóvel')

    def test_update_fotos_video_imovel(self):
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_profissional',
            formato='imagem',
            descricao='Foto profissional do imóvel',
            arquivo=SimpleUploadedFile("foto_profissional.jpg", b"file_content", content_type="image/jpeg"),
            data_emissao='2024-02-01'
        )
        data = {
            'tipo_midia': 'video_drone',
            'formato': 'video',
            'descricao': 'Vídeo com drone atualizado',
        }
        serializer = FotosVideoImovelSerializer(midia, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        midia_atualizada = serializer.save()
        self.assertEqual(midia_atualizada.tipo_midia, 'video_drone')
        self.assertEqual(midia_atualizada.formato, 'video')

    def test_delete_fotos_video_imovel(self):
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_profissional',
            formato='imagem',
            descricao='Foto profissional do imóvel',
            arquivo=SimpleUploadedFile("foto_profissional.jpg", b"file_content", content_type="image/jpeg"),
            data_emissao='2024-02-01'
        )
        midia_id = midia.id
        midia.delete()
        with self.assertRaises(FotosVideoImovel.DoesNotExist):
            FotosVideoImovel.objects.get(id=midia_id)
