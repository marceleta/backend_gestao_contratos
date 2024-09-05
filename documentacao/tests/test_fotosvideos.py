from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from documentacao.models import FotosVideoImovel
from imovel.models import Imovel
import datetime

class FotosVideoImovelTestCase(TestCase):

    def setUp(self):
        # Criação de um imóvel completo para associar aos arquivos de mídia
        self.imovel = Imovel.objects.create(
            nome='Casa de Praia',
            endereco='Rua do Sol, 101',
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

    def test_create_fotos_video_imovel(self):
        # Teste de criação de um arquivo de mídia do imóvel
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_drone',
            formato='imagem',
            descricao='Foto aérea da casa',
            arquivo=SimpleUploadedFile('foto_drone.jpg', b'conteudo do arquivo', content_type='image/jpeg'),
            data_emissao=datetime.date(2023, 5, 1)
        )
        self.assertEqual(midia.tipo_midia, 'foto_drone')
        self.assertEqual(midia.descricao, 'Foto aérea da casa')
        self.assertEqual(midia.imovel, self.imovel)

    def test_read_fotos_video_imovel(self):
        # Teste de leitura de um arquivo de mídia do imóvel
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='video_tour',
            formato='video',
            descricao='Vídeo tour da casa',
            arquivo=SimpleUploadedFile('video_tour.mp4', b'conteudo do arquivo', content_type='video/mp4'),
            data_emissao=datetime.date(2023, 5, 15)
        )
        midia_lida = FotosVideoImovel.objects.get(id=midia.id)
        self.assertEqual(midia_lida.tipo_midia, 'video_tour')
        self.assertEqual(midia_lida.descricao, 'Vídeo tour da casa')

    def test_update_fotos_video_imovel(self):
        # Teste de atualização de um arquivo de mídia do imóvel
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_profissional',
            formato='imagem',
            descricao='Foto profissional da casa',
            arquivo=SimpleUploadedFile('foto_profissional.jpg', b'conteudo do arquivo', content_type='image/jpeg'),
            data_emissao=datetime.date(2023, 5, 10)
        )
        midia.descricao = 'Foto profissional atualizada'
        midia.save()
        midia_atualizada = FotosVideoImovel.objects.get(id=midia.id)
        self.assertEqual(midia_atualizada.descricao, 'Foto profissional atualizada')

    def test_delete_fotos_video_imovel(self):
        # Teste de deleção de um arquivo de mídia do imóvel
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='depoimento_cliente',
            formato='video',
            descricao='Depoimento de cliente satisfeito',
            arquivo=SimpleUploadedFile('depoimento_cliente.mp4', b'conteudo do arquivo', content_type='video/mp4'),
            data_emissao=datetime.date(2023, 6, 1)
        )
        midia_id = midia.id
        midia.delete()
        with self.assertRaises(FotosVideoImovel.DoesNotExist):
            FotosVideoImovel.objects.get(id=midia_id)
