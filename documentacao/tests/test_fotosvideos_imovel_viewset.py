from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from documentacao.models import FotosVideoImovel
from imovel.models import Imovel
from usuario.models import Usuario
import datetime

class FotosVideoImovelViewSetTest(APITestCase):

    def setUp(self):
        # Criação do cliente autenticado
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

        # Criação de um imóvel para associar às mídias
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

    def test_create_fotos_video_imovel(self):
        # Teste de criação de uma mídia
        url = reverse('fotosvideoimovel-list')
        arquivo = SimpleUploadedFile("foto_drone.jpg", b"file_content", content_type="image/jpeg")
        data = {
            'imovel': self.imovel.id,
            'tipo_midia': 'foto_drone',
            'formato': 'imagem',
            'descricao': 'Foto aérea da casa',
            'arquivo': arquivo,
            'data_emissao': '2024-01-01'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FotosVideoImovel.objects.count(), 1)
        self.assertEqual(FotosVideoImovel.objects.get().tipo_midia, 'foto_drone')

    def test_retrieve_fotos_video_imovel(self):
        # Teste de recuperação de uma mídia
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='video_tour',
            formato='video',
            descricao='Vídeo tour da casa',
            arquivo=SimpleUploadedFile('video_tour.mp4', b'conteudo do arquivo', content_type='video/mp4'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('fotosvideoimovel-detail', args=[midia.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tipo_midia'], 'video_tour')

    def test_update_fotos_video_imovel(self):
        # Teste de atualização de uma mídia
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_profissional',
            formato='imagem',
            descricao='Foto profissional da casa',
            arquivo=SimpleUploadedFile('foto_profissional.jpg', b'conteudo do arquivo', content_type='image/jpeg'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('fotosvideoimovel-detail', args=[midia.id])
        data = {
            'imovel': self.imovel.id,
            'tipo_midia': 'video_drone',
            'formato': 'video',
            'descricao': 'Vídeo com drone atualizado',
            'arquivo': SimpleUploadedFile("video_drone.mp4", b"file_content", content_type="video/mp4"),
            'data_emissao': '2024-01-01'
        }
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        midia.refresh_from_db()
        self.assertEqual(midia.tipo_midia, 'video_drone')

    def test_delete_fotos_video_imovel(self):
        # Teste de deleção de uma mídia
        midia = FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_profissional',
            formato='imagem',
            descricao='Foto profissional da casa',
            arquivo=SimpleUploadedFile('foto_profissional.jpg', b'conteudo do arquivo', content_type='image/jpeg'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('fotosvideoimovel-detail', args=[midia.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FotosVideoImovel.objects.count(), 0)

    def test_list_fotos_video_imovel(self):
        # Teste de listagem de mídias filtradas por imóvel
        FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='foto_drone',
            formato='imagem',
            descricao='Foto aérea da casa',
            arquivo=SimpleUploadedFile('foto_drone.jpg', b'conteudo do arquivo', content_type='image/jpeg'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        FotosVideoImovel.objects.create(
            imovel=self.imovel,
            tipo_midia='video_tour',
            formato='video',
            descricao='Vídeo tour da casa',
            arquivo=SimpleUploadedFile('video_tour.mp4', b'conteudo do arquivo', content_type='video/mp4'),
            data_emissao=datetime.date(2024, 1, 1)
        )
        url = reverse('fotosvideoimovel-list') + f'?imovel={self.imovel.id}'
        #print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)